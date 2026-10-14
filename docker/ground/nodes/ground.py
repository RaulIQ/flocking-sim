import sys
from dataclasses import dataclass
from math import atan2, tau
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
class Ground:
    """The ground station: a window on the true cloud, the keyboard of the pilot and the senses of every drone.

    The senses stand in for the camera and the radio the copters do not
    have; they are sent only once every copter is heard of in full. Until
    then the window shows the drones where they are mustered. ROS listens on
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

    def run(self, flock: Flock, walls: tuple) -> None:
        mails = self.listen()
        pygame.init()
        pygame.display.set_caption("flocking-sim on ROS 2")
        view = View(
            pygame.display.set_mode(
                (self.settings.picture.window.width, self.settings.picture.window.height)
            ),
            self.settings,
        )
        pilot = Pilot(self.settings.limits)
        baton = Baton(view, self.settings.swarm.bubbles.soft)
        clock = pygame.time.Clock()
        events = pygame.event.get()
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
                request = Command(
                    pilot.velocity(tuple(pygame.key.get_pressed())),
                    pilot.spin(tuple(pygame.key.get_pressed())),
                )
                for mail, drone in zip(mails, flock.drones):
                    mail.publish(Post(flock.sensed(drone, request, walls), drone.leader).message())
            view.show(flock, walls)
            pygame.display.flip()
            events = pygame.event.get()
        pygame.quit()


if __name__ == "__main__":
    from config import copters, sortie
    from simulator.stage import Stage

    rclpy.init(args=sys.argv)
    Ground(
        rclpy.create_node("ground"),
        copters(),
        Census(sortie(copters()).hangar.fleet.origin, copters().swarm.muster.count),
        {},
    ).run(Stage(copters(), None).flock(), Stage(copters(), None).walls())
    rclpy.shutdown()
