from dataclasses import dataclass
from typing import final

from agent.command import Command
from agent.mind import Mind
from agent.senses import Motion, Senses
from agent.signals import Bearing, Range, Role, Signals
from agent.tracks import Tracks
from agent.vector import Vector
from autopilot.hold import Hold
from flocking_msgs.msg import Senses as Letter
from geometry_msgs.msg import Twist, Vector3
from mavros_msgs.msg import PositionTarget


@final
@dataclass(frozen=True)
class Board:
    """
    The companion computer of one copter, between its senses and its autopilot.

    Its own motion and the senses the ground sends go into the mind, and the
    speed the mind decides goes back to MAVROS. MAVROS speaks the frame of the
    copter as ROS does, forward, left and up, with turns counterclockwise,
    which is the frame of the agent too, so nothing changes sign on the way.
    Whether the drone leads is part of what it is told, so the same board
    flies a leader and a follower.
    """

    mind: Mind
    hold: Hold

    def senses(self, twist: Twist, letter: Letter) -> Senses:
        return Senses(
            Motion(Vector(twist.linear.x, twist.linear.y), twist.angular.z),
            Signals(
                tuple(Range(echo.tag, echo.distance) for echo in letter.ranges),
                tuple(Bearing(sight.tag, sight.angle) for sight in letter.bearings),
                tuple(Role(word.tag, word.leader) for word in letter.roles),
            ),
            tuple(Vector(point.x, point.y) for point in letter.obstacles),
            Command(
                Vector(letter.request.linear.x, letter.request.linear.y),
                letter.request.angular.z,
            ),
        )

    def target(
        self, memory: Tracks, senses: Senses, height: float, leader: bool
    ) -> PositionTarget:
        command = self.mind.led(leader).command(memory, senses)
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
