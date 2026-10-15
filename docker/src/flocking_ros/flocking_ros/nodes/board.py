from config import frames, sortie
from flocking_ros.board.board import Board
from flocking_ros.board.duty import Duty
import rclpy
from simulator.stage import Stage


def main() -> None:
    rclpy.init()
    node = rclpy.create_node('board')
    settings = frames()[node.declare_parameter('frame', 'freestyle').value]
    Duty(
        node,
        Board(Stage(settings, None).mind(), sortie(settings).hold),
        settings.picture.window.rate,
        {},
    ).run()
