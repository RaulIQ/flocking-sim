import sys
from dataclasses import dataclass
from math import atan2, inf, tau
from threading import Thread
from typing import final

import pygame
import rclpy
from flocking_msgs.msg import Bearing, Range, Role
from flocking_msgs.msg import Senses as Letter
from geometry_msgs.msg import Point, PoseStamped, Twist, TwistStamped, Vector3
from pygame import K_ESCAPE, KEYDOWN, QUIT
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import NavSatFix

from agent.command import Command
from agent.senses import Senses
from agent.vector import Vector
from autopilot.spot import Spot
from scenarios.report import Report
from scenarios.route import Route
from scenarios.scenario import Scenario
from scenarios.tally import Passage, Tally
from simulator.baton import Baton
from simulator.body import Body
from simulator.control import Pilot
from simulator.flock import Flock
from simulator.view import View


@final
@dataclass(frozen=True)
class Census:
    """Where every copter truly is in the shared frame, from what its own MAVROS tells.

    Every copter counts its local position from its own home, so the place
    comes from its latitude and longitude around the shared origin. The
    heading, the velocity and the turn of the local frame are shared by all
    copters, east and north alike, and are taken as they are.
    """

    origin: Spot
    count: int

    def complete(self, heard: dict) -> bool:
        return all(
            {"fix", "pose", "motion"} <= set(heard.get(number, {}))
            for number in range(1, self.count + 1)
        )

    def airborne(self, heard: dict, altitude: float) -> bool:
        return all(
            heard[number]["pose"].pose.position.z >= 0.9 * altitude
            for number in range(1, self.count + 1)
        )

    def bodies(self, heard: dict) -> tuple:
        return tuple(
            Body(
                self.origin.offset(
                    Spot(heard[number]["fix"].latitude, heard[number]["fix"].longitude)
                ),
                atan2(
                    2.0
                    * (
                        heard[number]["pose"].pose.orientation.w
                        * heard[number]["pose"].pose.orientation.z
                        + heard[number]["pose"].pose.orientation.x
                        * heard[number]["pose"].pose.orientation.y
                    ),
                    1.0
                    - 2.0
                    * (
                        heard[number]["pose"].pose.orientation.y ** 2
                        + heard[number]["pose"].pose.orientation.z ** 2
                    ),
                )
                % tau,
                Vector(
                    heard[number]["motion"].twist.linear.x,
                    heard[number]["motion"].twist.linear.y,
                ),
                heard[number]["motion"].twist.angular.z,
            )
            for number in range(1, self.count + 1)
        )


@final
@dataclass(frozen=True)
class Post:
    """What the ground sends one drone in one tick: whether it leads and what its own sensors would measure."""

    senses: Senses
    leader: bool

    def message(self) -> Letter:
        return Letter(
            leader=self.leader,
            ranges=[Range(tag=echo.tag, distance=echo.distance) for echo in self.senses.signals.ranges],
            bearings=[
                Bearing(tag=sight.tag, angle=sight.angle) for sight in self.senses.signals.bearings
            ],
            roles=[Role(tag=word.tag, leader=word.leader) for word in self.senses.signals.roles],
            obstacles=[Point(x=offset.x, y=offset.y) for offset in self.senses.obstacles],
            request=Twist(
                linear=Vector3(x=self.senses.request.velocity.x, y=self.senses.request.velocity.y),
                angular=Vector3(z=self.senses.request.spin),
            ),
        )


@final
@dataclass(frozen=True)
class Hands:
    """The pilot at the keyboard of the window, who reports nothing."""

    pilot: Pilot

    def rest(self, body: Body) -> "Hands":
        return self

    def command(self, body: Body) -> Command:
        return Command(
            self.pilot.velocity(tuple(pygame.key.get_pressed())),
            self.pilot.spin(tuple(pygame.key.get_pressed())),
        )

    def told(self, frame: int, tally: Tally, flock: Flock) -> tuple:
        return ()


@final
@dataclass(frozen=True)
class Script:
    """A scripted pilot: the leader flies the route of a scenario, and the run is reported once it ends.

    The frames are counted from the moment the whole cloud is airborne, so
    the report comes exactly once, at the frame the scenario ends.
    """

    name: str
    scenario: Scenario
    route: Route

    def rest(self, body: Body) -> "Script":
        return Script(self.name, self.scenario, self.route.rest(body))

    def command(self, body: Body) -> Command:
        return self.route.command(body)

    def told(self, frame: int, tally: Tally, flock: Flock) -> tuple:
        if frame != round(self.scenario.seconds * self.scenario.settings.picture.window.rate):
            return ()
        return Report(self.name, self.scenario, tally, flock).lines()[:-1]


@final
@dataclass(frozen=True)
class Ground:
    """The ground station: a window on the true cloud, the keyboard of the pilot and the senses of every drone.

    The senses stand in for the camera and the radio the copters do not
    have; they are sent only once every copter is heard of in full. Until
    then the window shows the drones where they are mustered. The pilot, at
    the keyboard or scripted, takes over once the whole cloud is airborne,
    and from then on every frame is tallied as a scenario would be. ROS listens on
    a thread of its own, started only once every subscription and publisher
    is made, and the window keeps the beat.
    """

    node: object
    settings: object
    census: Census
    heard: dict

    def listen(self) -> tuple:
        for number in range(1, self.census.count + 1):
            for kind, message, topic in (
                ("fix", NavSatFix, "global_position/global"),
                ("pose", PoseStamped, "local_position/pose"),
                ("motion", TwistStamped, "local_position/velocity_local"),
            ):
                self.node.create_subscription(
                    message,
                    f"/uav{number}/mavros/{topic}",
                    lambda received, number=number, kind=kind: self.heard.setdefault(number, {}).update(
                        {kind: received}
                    ),
                    qos_profile_sensor_data,
                )
        mails = tuple(
            self.node.create_publisher(Letter, f"/uav{number}/senses", qos_profile_sensor_data)
            for number in range(1, self.census.count + 1)
        )
        Thread(target=rclpy.spin, args=(self.node,), daemon=True).start()
        return mails

    def run(self, flock: Flock, walls: tuple, pilot, altitude: float) -> None:
        mails = self.listen()
        pygame.init()
        pygame.display.set_caption("flocking-sim on ROS 2")
        view = View(
            pygame.display.set_mode(
                (self.settings.picture.window.width, self.settings.picture.window.height)
            ),
            self.settings,
        )
        baton = Baton(view, self.settings.swarm.bubbles.soft)
        clock = pygame.time.Clock()
        events = pygame.event.get()
        frame = 0
        tally = Tally(inf, inf, 0, Passage(0, 0.0))
        while not [
            event
            for event in events
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE)
        ]:
            clock.tick(self.settings.picture.window.rate)
            flock = baton.passed(flock, events)
            if self.census.complete(self.heard):
                flock = Flock(
                    tuple(
                        drone.placed(body)
                        for drone, body in zip(flock.drones, self.census.bodies(self.heard))
                    )
                )
                request = Command(Vector(0.0, 0.0), 0.0)
                if frame or self.census.airborne(self.heard, altitude):
                    pilot = pilot.rest(flock.leader().body)
                    request = pilot.command(flock.leader().body)
                    frame += 1
                    tally = tally.after(frame / self.settings.picture.window.rate, flock, self.settings)
                    for line in pilot.told(frame, tally, flock):
                        self.node.get_logger().info(line)
                for mail, drone in zip(mails, flock.drones):
                    mail.publish(Post(flock.sensed(drone, request, walls), drone.leader).message())
            view.show(flock, walls)
            pygame.display.flip()
            events = pygame.event.get()
        pygame.quit()


if __name__ == "__main__":
    from os import environ

    from config import copters, sortie
    from scenarios.catalogue import catalogue
    from simulator.stage import Stage

    rclpy.init(args=sys.argv)
    Ground(
        rclpy.create_node("ground"),
        copters(),
        Census(sortie(copters()).hangar.fleet.origin, copters().swarm.muster.count),
        {},
    ).run(
        Stage(copters(), None).flock(),
        Stage(copters(), None).walls(),
        Script(
            environ["ROUTE"],
            Scenario(
                catalogue()[environ["ROUTE"]].story,
                copters(),
                catalogue()[environ["ROUTE"]].route,
                catalogue()[environ["ROUTE"]].seconds,
            ),
            catalogue()[environ["ROUTE"]].route,
        )
        if environ.get("ROUTE")
        else Hands(Pilot(copters().limits)),
        sortie(copters()).hold.altitude,
    )
    rclpy.shutdown()
