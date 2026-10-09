from dataclasses import dataclass
from typing import final

from pygame import K_DOWN, K_LEFT, K_RIGHT, K_UP, K_a, K_d, K_s, K_w

from config import Limits
from simulator.vector import Vector


@final
@dataclass(frozen=True)
class Pilot:
    """A human at the keyboard, sliding one drone around in its own frame."""

    limits: Limits

    def velocity(self, keys) -> Vector:
        return Vector(
            keys[K_w] + keys[K_UP] - keys[K_s] - keys[K_DOWN],
            keys[K_a] + keys[K_LEFT] - keys[K_d] - keys[K_RIGHT],
        ).capped(1.0).times(self.limits.speed)
