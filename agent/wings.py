from dataclasses import dataclass
from math import cos, sin
from typing import final

from agent.neighbour import Neighbour
from agent.tuning import Limits, Rope
from agent.vector import Vector


@final
@dataclass(frozen=True)
class Wings:
    """The two wings of the wedge behind a flying leader, as the drone at the origin sees them.

    Each wing leaves the line of flight backward at the angle of the wedge,
    starts a spring rest behind the leader and runs for the length of the
    wedge. The wing on the inside of a turn the pilot asks for folds toward
    the track of the leader, the more the harder it turns, and lies right
    behind it at the top spin, so that the cloud never hangs on the side the
    leader turns to. The place is the point of either wing nearest to the drone.
    """

    rope: Rope
    limits: Limits
    turn: float

    def place(self, leader: Neighbour) -> Vector:
        return min(
            (self.point(leader, side) for side in (1.0, -1.0)),
            key=lambda point: point.length(),
        )

    def point(self, leader: Neighbour, side: float) -> Vector:
        ahead = leader.velocity.times(1.0 / leader.velocity.length())
        angle = self.rope.wedge.angle * (
            max(0.0, 1.0 - abs(self.turn) / self.limits.spin)
            if self.turn * side > 0.0
            else 1.0
        )
        wing = Vector(0.0, 0.0).minus(ahead).times(cos(angle)).plus(
            Vector(-ahead.y, ahead.x).times(side * sin(angle))
        )
        return leader.offset.plus(
            wing.times(
                max(
                    self.rope.spring.rest,
                    min(
                        self.rope.spring.rest + self.rope.wedge.length,
                        -leader.offset.dot(wing),
                    ),
                )
            )
        )
