from dataclasses import dataclass
from math import tau
from typing import final

from config import Limits
from simulator.vector import Vector


@final
@dataclass(frozen=True)
class Command:
    """A request in the frame of one drone, x along its nose and y to its left."""

    velocity: Vector
    spin: float


@final
@dataclass(frozen=True)
class Body:
    """The true state of one drone, whose speed lags behind every request."""

    position: Vector
    heading: float
    velocity: Vector
    spin: float

    def moved(self, command: Command, limits: Limits, lapse: float) -> "Body":
        target = command.velocity.turned(self.heading).capped(limits.speed)
        velocity = self.velocity.plus(
            target.minus(self.velocity).capped(limits.push * lapse)
        )
        wanted = max(-limits.spin, min(limits.spin, command.spin))
        reach = limits.twist * lapse
        spin = self.spin + max(-reach, min(reach, wanted - self.spin))
        return Body(
            self.position.plus(velocity.times(lapse)),
            (self.heading + spin * lapse) % tau,
            velocity,
            spin,
        )
