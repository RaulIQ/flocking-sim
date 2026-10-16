from dataclasses import dataclass
from typing import final

from agent.neighbour import Neighbour
from agent.vector import Vector


@final
@dataclass(frozen=True)
class Sweep:
    """The circle a flying leader goes round while its pilot holds a turn, as the drone at the origin sees it.

    A leader that keeps turning comes back round to every point of its
    circle, so a follower anywhere inside it is in the way sooner or later.
    The exit is the shortest move that takes the drone out of the circle
    widened by a clearance, straight away from its centre, and nothing when
    the drone already stands outside or the leader flies straight. The turn
    is in radians a second, counterclockwise, as the pilot asks for it.
    """

    leader: Neighbour
    turn: float

    def exit(self, clearance: float) -> Vector:
        if self.turn == 0.0:
            return Vector(0.0, 0.0)
        centre = self.leader.offset.plus(
            Vector(-self.leader.velocity.y, self.leader.velocity.x).times(1.0 / self.turn)
        )
        depth = self.leader.velocity.length() / abs(self.turn) + clearance - centre.length()
        if depth <= 0.0:
            return Vector(0.0, 0.0)
        return Vector(0.0, 0.0).minus(centre).times(depth / centre.length())
