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
    node = rclpy.create_node('ground')
    route = node.declare_parameter('route', '').value
    Ground(
        node,
        copters(),
        Census(sortie(copters()).hangar.fleet.origin, copters().swarm.muster.count),
        {},
    ).run(
        Stage(copters(), None).flock(),
        Stage(copters(), None).walls(),
        Script(
            route,
            Scenario(
                catalogue()[route].story,
                copters(),
                catalogue()[route].route,
                catalogue()[route].seconds,
            ),
            catalogue()[route].route,
        )
        if route
        else Hands(Pilot(copters().limits)),
        sortie(copters()).hold.altitude,
    )
    rclpy.shutdown()
