from dataclasses import dataclass
from typing import final

from agent.tracks import Tracks
from flocking_msgs.msg import Senses as Letter
from flocking_ros.board.board import Board
from geometry_msgs.msg import PoseStamped, TwistStamped
from mavros_msgs.msg import ExtendedState, PositionTarget
import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data


@final
@dataclass(frozen=True)
class Duty:
    """
    One board at work on its own clock.

    It listens to MAVROS and to its senses between ticks and asks for a speed
    on every tick. Until it has heard all four it asks for nothing, and the
    autopilot holds the copter where it is. It asks for nothing either while
    the copter stands, takes off or lands, since a speed asked in GUIDED
    cancels a takeoff the autopilot has begun. What it heard last and what the
    mind remembers live in one dictionary, the only thing here that changes.
    """

    node: Node
    board: Board
    rate: float
    state: dict

    def run(self) -> None:
        self.node.create_subscription(
            TwistStamped,
            'mavros/local_position/velocity_body',
            self.moved,
            qos_profile_sensor_data,
        )
        self.node.create_subscription(
            PoseStamped, 'mavros/local_position/pose', self.placed, qos_profile_sensor_data
        )
        self.node.create_subscription(Letter, 'senses', self.told, qos_profile_sensor_data)
        self.node.create_subscription(
            ExtendedState, 'mavros/extended_state', self.landed, qos_profile_sensor_data
        )
        self.state['out'] = self.node.create_publisher(
            PositionTarget, 'mavros/setpoint_raw/local', 10
        )
        self.node.create_timer(1.0 / self.rate, self.tick)
        self.node.get_logger().info(f'The board flies by its senses at {self.rate} Hz')
        rclpy.spin(self.node)

    def moved(self, twist: TwistStamped) -> None:
        self.state['twist'] = twist.twist

    def placed(self, pose: PoseStamped) -> None:
        self.state['height'] = pose.pose.position.z

    def told(self, letter: Letter) -> None:
        self.state['letter'] = letter

    def landed(self, flight: ExtendedState) -> None:
        self.state['flight'] = flight

    def tick(self) -> None:
        if not {'twist', 'height', 'letter', 'flight'} <= set(self.state):
            return
        if self.state['flight'].landed_state != ExtendedState.LANDED_STATE_IN_AIR:
            return
        senses = self.board.senses(self.state['twist'], self.state['letter'])
        self.state['memory'] = self.board.mind.recalled(
            self.state.get('memory', Tracks(())), senses
        )
        self.state['out'].publish(
            self.board.target(
                self.state['memory'], senses, self.state['height'], self.state['letter'].leader
            )
        )
