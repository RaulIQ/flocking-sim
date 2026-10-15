from config import copters, sortie
from flocking_ros.board.board import Board
from flocking_ros.board.duty import Duty
import rclpy
from simulator.stage import Stage


def main() -> None:
    rclpy.init()
    Duty(
        rclpy.create_node('board'),
        Board(Stage(copters(), None).mind(), sortie(copters()).hold),
        copters().picture.window.rate,
        {},
    ).run()
