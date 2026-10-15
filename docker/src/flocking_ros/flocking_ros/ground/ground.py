from dataclasses import dataclass
from functools import partial
from math import inf
from threading import Thread
from typing import final

from agent.command import Command
from agent.vector import Vector
from config import Settings
from flocking_msgs.msg import Senses as Letter
from flocking_ros.ground.census import Census
from flocking_ros.ground.helm import Helm
from flocking_ros.ground.post import Post
from geometry_msgs.msg import PoseStamped, TwistStamped
import pygame
from pygame import K_ESCAPE, KEYDOWN, QUIT
import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from scenarios.tally import Passage, Tally
from sensor_msgs.msg import NavSatFix
from simulator.baton import Baton
from simulator.flock import Flock
from simulator.view import View


@final
@dataclass(frozen=True)
class Ground:
    """
    The ground station: a window on the true cloud, the pilot and the senses of every drone.

    The senses stand in for the camera and the radio the copters do not
    have; they are sent only once every copter is heard of in full. Until
    then the window shows the drones where they are mustered. The pilot, at
    the keyboard or scripted, takes over once the whole cloud is airborne,
    and from then on every frame is tallied as a scenario would be. ROS
    listens on a thread of its own, started only once every subscription and
    publisher is made. The beat comes from the clock of the node, which is the
    wall clock, or the clock of Gazebo when the node uses the time of the
    simulation.
    """

    node: Node
    settings: Settings
    census: Census
    heard: dict

    def listen(self) -> tuple:
        for number in range(1, self.census.count + 1):
            for kind, message, topic in (
                ('fix', NavSatFix, 'global_position/global'),
                ('pose', PoseStamped, 'local_position/pose'),
                ('motion', TwistStamped, 'local_position/velocity_local'),
            ):
                self.node.create_subscription(
                    message,
                    f'/uav{number}/mavros/{topic}',
                    partial(self.hear, number, kind),
                    qos_profile_sensor_data,
                )
        mails = tuple(
            self.node.create_publisher(Letter, f'/uav{number}/senses', qos_profile_sensor_data)
            for number in range(1, self.census.count + 1)
        )
        Thread(target=rclpy.spin, args=(self.node,), daemon=True).start()
        return mails

    def hear(self, number: int, kind: str, message: object) -> None:
        self.heard.setdefault(number, {})[kind] = message

    def run(self, flock: Flock, walls: tuple, helm: Helm, altitude: float) -> None:
        mails = self.listen()
        pygame.init()
        pygame.display.set_caption('flocking-sim on ROS 2')
        view = View(
            pygame.display.set_mode(
                (self.settings.picture.window.width, self.settings.picture.window.height)
            ),
            self.settings,
        )
        baton = Baton(view, self.settings.swarm.bubbles.soft)
        rate = self.node.create_rate(self.settings.picture.window.rate)
        events = pygame.event.get()
        frame = 0
        tally = Tally(inf, inf, 0, Passage(0, 0.0))
        while not [
            event
            for event in events
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE)
        ]:
            rate.sleep()
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
                    helm = helm.rest(flock.leader().body)
                    request = helm.command(flock.leader().body)
                    frame += 1
                    tally = tally.after(
                        frame / self.settings.picture.window.rate, flock, self.settings
                    )
                    for line in helm.told(frame, tally, flock):
                        self.node.get_logger().info(line)
                for mail, drone in zip(mails, flock.drones):
                    mail.publish(Post(flock.sensed(drone, request, walls), drone.leader).message())
            view.show(flock, walls)
            pygame.display.flip()
            events = pygame.event.get()
        pygame.quit()
