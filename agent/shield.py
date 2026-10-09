from dataclasses import dataclass
from functools import reduce
from math import sqrt
from typing import final

from agent.command import Command
from agent.tuning import Limits
from agent.vector import Vector


@final
@dataclass(frozen=True)
class Shield:
    """The last word on a request: it may not close on a wall faster than the drone can brake.

    Each wall leaves a half-plane of allowed velocities, as in the ORCA of
    van den Berg 2011, and the bound on the closing speed is the braking
    barrier of Ames 2017: the square root of twice the deceleration times the
    room left before the margin. The drone carries the whole duty, a wall
    cannot give way. Our own choices are to count on half of the deceleration
    only, and never to allow more than the room left in one tick, so that a
    drone that thinks in ticks cannot step over the margin between two of them.

    A drone that already closes faster than the bound brakes first: of the
    change in velocity it can make in one tick, braking takes what it needs and
    the request gets the rest. The share shrinks smoothly, with no threshold
    for a rounding error to tip, so the answer does not depend on which way
    the drone happens to face.
    """

    limits: Limits
    margin: float
    lapse: float

    def command(self, command: Command, velocity: Vector, obstacles: tuple) -> Command:
        return Command(
            reduce(
                lambda wanted, offset: self.clipped(wanted, velocity, offset),
                obstacles,
                command.velocity,
            ),
            command.spin,
        )

    def clipped(self, wanted: Vector, velocity: Vector, offset: Vector) -> Vector:
        distance = offset.length()
        if distance == 0.0:
            return wanted
        room = max(0.0, distance - self.margin)
        bound = min(sqrt(self.limits.push * room), room / self.lapse)
        allowed = wanted.minus(
            offset.times(max(0.0, wanted.dot(offset) / distance - bound) / distance)
        )
        excess = velocity.dot(offset) / distance - bound
        if excess <= 0.0:
            return allowed
        braked = velocity.minus(offset.times(excess / distance))
        return braked.plus(
            allowed.minus(braked).capped(
                max(0.0, self.limits.push * self.lapse - excess)
            )
        )
