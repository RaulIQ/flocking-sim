from dataclasses import dataclass
from math import atan2, pi
from typing import final

from agent.neighbour import Neighbour
from agent.vector import Vector


@final
@dataclass(frozen=True)
class Way:
    """Where a flying leader goes next, as the drone at the origin sees it.

    The way starts at the leader, runs along its velocity and bends into an
    arc by the turn its pilot asks for, in radians a second, counterclockwise.
    It ends after the reach, in metres, and never runs more than once around.
    The turn comes from the pilot, not from the motion of the leader, so a
    follower knows the bend as soon as the leader itself does.
    """

    leader: Neighbour
    turn: float
    reach: float

    def nearest(self) -> Vector:
        return self.place(self.along())

    def along(self) -> float:
        speed = self.leader.velocity.length()
        if self.turn == 0.0:
            return max(
                0.0,
                min(self.reach, -self.leader.offset.dot(self.leader.velocity) / speed),
            )
        arm = self.leader.offset.minus(self.centre())
        angle = (
            atan2(arm.x * -self.centre().y + arm.y * self.centre().x, -arm.dot(self.centre()))
            * (1.0 if self.turn > 0.0 else -1.0)
        ) % (2.0 * pi)
        span = min(self.reach, 2.0 * pi * speed / abs(self.turn))
        if angle * speed / abs(self.turn) <= span:
            return angle * speed / abs(self.turn)
        return min((0.0, span), key=lambda length: self.place(length).length())

    def place(self, length: float) -> Vector:
        speed = self.leader.velocity.length()
        if self.turn == 0.0:
            return self.leader.offset.plus(self.leader.velocity.times(length / speed))
        return self.centre().plus(
            self.leader.offset.minus(self.centre()).turned(length * self.turn / speed)
        )

    def centre(self) -> Vector:
        return self.leader.offset.plus(
            Vector(-self.leader.velocity.y, self.leader.velocity.x).times(1.0 / self.turn)
        )
