from dataclasses import dataclass
from typing import final

from agent.bond import Bond
from agent.neighbour import Neighbour
from agent.sweep import Sweep
from agent.tuning import Limits, Rope
from agent.vector import Vector
from agent.way import Way
from agent.wings import Wings


@final
@dataclass(frozen=True)
class Tow:
    """How a leader moves one follower: it carries it along, draws it into a wedge behind, and lets it out of its way.

    A follower of a hovering leader is held around it by the spring of the
    rope. A follower of a flying leader flies along with it and is pulled
    toward the nearest point of the wedge behind it. A follower that stands
    in the way of the leader is neither carried ahead nor pulled; it steps
    off the way to the side it already stands on, at least as fast as the
    leader comes. The way bends with the turn the pilot asks for and reaches
    as far as the leader flies in the horizon of the rope, plus the rest of
    its spring. A follower inside the circle a turning leader goes round is
    not pulled either; it flies along and moves straight out of the circle
    widened by the clearance of the wedge. This is our own choice; it keeps
    the leader first and leaves it free to turn.
    """

    rope: Rope
    limits: Limits
    turn: float

    def carry(self, leader: Neighbour) -> Vector:
        if self.blocks(leader):
            ahead = leader.velocity.times(1.0 / leader.velocity.length())
            away = Vector(0.0, 0.0).minus(self.way(leader).nearest())
            return (
                away.times(1.0 / away.length())
                if away.length() > 0.0
                else Vector(-ahead.y, ahead.x)
            ).times(
                min(
                    self.limits.speed,
                    self.rope.gain * (self.rope.spring.rest - away.length())
                    + leader.velocity.length(),
                )
            )
        return leader.velocity.plus(
            self.exit(leader).times(self.rope.gain)
        ).capped(self.limits.speed)

    def hold(self, leader: Neighbour) -> Vector:
        if leader.velocity.length() < 0.1:
            return Bond(self.rope.spring).velocity(leader.offset)
        if self.blocks(leader) or self.exit(leader).length() > 0.0:
            return Vector(0.0, 0.0)
        place = Wings(self.rope, self.limits, self.turn).place(leader)
        if place.length() == 0.0:
            return place
        return place.times(
            self.rope.wedge.pull
            * min(place.length(), self.rope.spring.reach)
            / place.length()
        )

    def blocks(self, leader: Neighbour) -> bool:
        return (
            leader.velocity.length() >= 0.1
            and self.way(leader).along() > 0.0
            and self.way(leader).nearest().length() < self.rope.spring.rest
        )

    def exit(self, leader: Neighbour) -> Vector:
        if leader.velocity.length() < 0.1:
            return Vector(0.0, 0.0)
        return Sweep(leader, self.turn).exit(self.rope.wedge.clearance)

    def way(self, leader: Neighbour) -> Way:
        return Way(
            leader,
            self.turn,
            self.rope.spring.rest + leader.velocity.length() * self.rope.horizon,
        )
