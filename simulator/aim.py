from dataclasses import dataclass
from math import atan2, copysign, remainder, sqrt, tau
from typing import final

from config import Limits
from simulator.body import Body
from simulator.vector import Vector


@final
@dataclass(frozen=True)
class Aim:
    """A turn request that faces one drone toward a place, braking as it arrives."""

    limits: Limits
    radius: float

    def spin(self, body: Body, target: Vector, lapse: float) -> float:
        offset = target.minus(body.position)
        if offset.length() <= self.radius:
            return 0.0
        error = remainder(atan2(offset.y, offset.x) - body.heading, tau)
        return copysign(
            min(
                self.limits.spin,
                sqrt(2.0 * self.limits.twist * abs(error)),
                abs(error) / lapse,
            ),
            error,
        )
