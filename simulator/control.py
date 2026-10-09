from dataclasses import dataclass
from typing import final

from pygame import K_a, K_d, K_e, K_q, K_s, K_w

from config import Limits
from simulator.body import Command
from simulator.vector import Vector


@final
@dataclass(frozen=True)
class Pilot:
    """A human at the keyboard, asking one drone to fly in its own frame."""

    limits: Limits

    def command(self, keys) -> Command:
        return Command(
            Vector(
                self.limits.speed * (keys[K_w] - keys[K_s]),
                self.limits.speed * (keys[K_a] - keys[K_d]),
            ).capped(self.limits.speed),
            self.limits.spin * (keys[K_q] - keys[K_e]),
        )
