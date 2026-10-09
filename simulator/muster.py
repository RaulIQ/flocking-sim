from dataclasses import dataclass
from math import pi, sqrt
from typing import final

from simulator.vector import Vector


@final
@dataclass(frozen=True)
class Muster:
    """The starting places of a swarm, a loose cloud with its first drone in the middle.

    The places follow the sunflower of Vogel 1979, which packs any number of
    points evenly without rows or slots.
    """

    count: int
    spacing: float

    def places(self) -> tuple:
        return tuple(
            Vector(self.spacing * sqrt(index), 0.0).turned(index * pi * (3.0 - sqrt(5.0)))
            for index in range(self.count)
        )
