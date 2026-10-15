from config import frames, sortie
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
    settings = frames()[node.declare_parameter('frame', 'freestyle').value]
    Ground(
        node,
        settings,
        Census(sortie(settings).hangar.fleet.origin, settings.swarm.muster.count),
        {},
    ).run(
        Stage(settings, None).flock(),
        Stage(settings, None).walls(),
        Script(
            route,
            Scenario(
                catalogue()[route].story,
                settings,
                catalogue()[route].route,
                catalogue()[route].seconds,
            ),
            catalogue()[route].route,
        )
        if route
        else Hands(Pilot(settings.limits)),
        sortie(settings).hold.altitude,
    )
    rclpy.shutdown()
