from os import environ

from config import copters, sortie
from flocking_ros.ground.census import Census
from flocking_ros.ground.ground import Ground
from flocking_ros.ground.hands import Hands
from flocking_ros.ground.script import Script
import rclpy
from scenarios.catalogue import catalogue
from scenarios.scenario import Scenario
from simulator.control import Pilot
from simulator.stage import Stage


def main() -> None:
    rclpy.init()
    Ground(
        rclpy.create_node('ground'),
        copters(),
        Census(sortie(copters()).hangar.fleet.origin, copters().swarm.muster.count),
        {},
    ).run(
        Stage(copters(), None).flock(),
        Stage(copters(), None).walls(),
        Script(
            environ['ROUTE'],
            Scenario(
                catalogue()[environ['ROUTE']].story,
                copters(),
                catalogue()[environ['ROUTE']].route,
                catalogue()[environ['ROUTE']].seconds,
            ),
            catalogue()[environ['ROUTE']].route,
        )
        if environ.get('ROUTE')
        else Hands(Pilot(copters().limits)),
        sortie(copters()).hold.altitude,
    )
    rclpy.shutdown()
