import sys
from dataclasses import dataclass
from typing import final

import rclpy
from geometry_msgs.msg import PoseStamped, Twist, TwistStamped, Vector3
from mavros_msgs.msg import PositionTarget
from rclpy.qos import qos_profile_sensor_data

from agent.command import Command
from agent.mind import Mind
from agent.senses import Motion, Senses
from agent.signals import Signals
from agent.tracks import Tracks
from agent.vector import Vector
from autopilot.hold import Hold


@final
@dataclass(frozen=True)
class Board:
    """The companion computer of one copter: what MAVROS tells goes into the mind, the speed it decides goes back.

    MAVROS speaks the frame of the copter as ROS does, forward, left and up,
    with turns counterclockwise, which is the frame of the agent too, so
    nothing changes sign on the way.
    """

    mind: Mind
    hold: Hold
    request: Command

    def senses(self, twist: Twist) -> Senses:
        return Senses(
            Motion(Vector(twist.linear.x, twist.linear.y), twist.angular.z),
            Signals((), (), ()),
            (),
            self.request,
        )

    def target(self, memory: Tracks, senses: Senses, height: float) -> PositionTarget:
        command = self.mind.command(memory, senses)
        return PositionTarget(
            coordinate_frame=PositionTarget.FRAME_BODY_NED,
            type_mask=PositionTarget.IGNORE_PX
            | PositionTarget.IGNORE_PY
            | PositionTarget.IGNORE_PZ
            | PositionTarget.IGNORE_AFX
            | PositionTarget.IGNORE_AFY
            | PositionTarget.IGNORE_AFZ
            | PositionTarget.IGNORE_YAW,
            velocity=Vector3(
                x=command.velocity.x, y=command.velocity.y, z=self.hold.climb(height)
            ),
            yaw_rate=command.spin,
        )


@final
@dataclass(frozen=True)
class Duty:
    """One board at work on its own clock: it listens to MAVROS between ticks and asks for a speed on every tick.

    What it heard last and what the mind remembers live in one dictionary,
    the only thing here that changes.
    """

    node: object
    board: Board
    rate: float
    state: dict

    def run(self) -> None:
        self.node.create_subscription(
            TwistStamped,
            "mavros/local_position/velocity_body",
            lambda twist: self.state.update(twist=twist.twist),
            qos_profile_sensor_data,
        )
        self.node.create_subscription(
            PoseStamped,
            "mavros/local_position/pose",
            lambda pose: self.state.update(height=pose.pose.position.z),
            qos_profile_sensor_data,
        )
        self.node.create_timer(
            1.0 / self.rate,
            lambda: self.tick(
                self.node.create_publisher(PositionTarget, "mavros/setpoint_raw/local", 10)
                if "out" not in self.state
                else self.state["out"]
            ),
        )
        self.node.get_logger().info(f"The board flies {self.board.request} at {self.rate} Hz")
        rclpy.spin(self.node)

    def tick(self, out) -> None:
        self.state["out"] = out
        if "twist" not in self.state or "height" not in self.state:
            return
        senses = self.board.senses(self.state["twist"])
        self.state["memory"] = self.board.mind.recalled(
            self.state.get("memory", Tracks(())), senses
        )
        out.publish(self.board.target(self.state["memory"], senses, self.state["height"]))


if __name__ == "__main__":
    from config import copters, sortie
    from simulator.stage import Stage

    rclpy.init(args=sys.argv)
    Duty(
        rclpy.create_node("board"),
        Board(
            Stage(copters(), None).mind().led(True),
            sortie(copters()).hold,
            Command(Vector(float(sys.argv[1]), float(sys.argv[2])), float(sys.argv[3])),
        ),
        copters().picture.window.rate,
        {},
    ).run()
