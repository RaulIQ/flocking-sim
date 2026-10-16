from dataclasses import dataclass
from typing import final

from agent.bond import Bond
from agent.neighbour import Neighbour
from agent.tuning import Limits, Rope
from agent.vector import Vector


@final
@dataclass(frozen=True)
class Tow:
    """How a leader moves one follower: it carries it along on a rope and lets it step out of its way.

    A follower behind its leader, beside its way or far ahead of it flies
    along with the leader and is held by the spring of the rope. A follower
    that stands in the way of a flying leader is neither carried ahead of it
    nor shoved along its line, as a rope hanging slack would neither drag nor
    push; it steps off the line to the side it already stands on, at least as
    fast as the leader comes. The way is as wide as the rest of the spring on
    either side of the leader's line and reaches as far ahead as the leader
    flies in the horizon of the rope. This is our own choice; it lets the
    leader fly through its cloud, which then closes up behind it.
    """

    rope: Rope
    limits: Limits

    def carry(self, leader: Neighbour) -> Vector:
        if not self.blocks(leader):
            return leader.velocity
        ahead = leader.velocity.times(1.0 / leader.velocity.length())
        place = Vector(0.0, 0.0).minus(leader.offset)
        lateral = place.minus(ahead.times(place.dot(ahead)))
        return (
            lateral.times(1.0 / lateral.length())
            if lateral.length() > 0.0
            else Vector(-ahead.y, ahead.x)
        ).times(
            min(
                self.limits.speed,
                self.rope.gain * (self.rope.spring.rest - lateral.length())
                + leader.velocity.length(),
            )
        )

    def hold(self, leader: Neighbour) -> Vector:
        if self.blocks(leader):
            return Vector(0.0, 0.0)
        return Bond(self.rope.spring).velocity(leader.offset)

    def blocks(self, leader: Neighbour) -> bool:
        speed = leader.velocity.length()
        place = Vector(0.0, 0.0).minus(leader.offset)
        if speed < 0.1 or place.dot(leader.velocity) <= 0.0:
            return False
        along = place.dot(leader.velocity) / speed
        return (
            place.minus(leader.velocity.times(along / speed)).length() < self.rope.spring.rest
            and along < self.rope.spring.rest + speed * self.rope.horizon
        )
