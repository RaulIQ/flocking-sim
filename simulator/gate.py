from dataclasses import dataclass
from typing import final

from agent.vector import Vector
from config import Barrier
from simulator.wall import Wall


@final
@dataclass(frozen=True)
class Gate:
    """A wall across the flight path, split into pieces by the gaps in it."""

    barrier: Barrier

    def walls(self) -> tuple:
        edges = (
            -self.barrier.span / 2,
            *(
                centre + side * self.barrier.gap / 2
                for centre in sorted(self.barrier.centres)
                for side in (-1, 1)
            ),
            self.barrier.span / 2,
        )
        return tuple(
            Wall(Vector(self.barrier.across, low), Vector(self.barrier.across, high))
            for low, high in zip(edges[::2], edges[1::2])
        )
