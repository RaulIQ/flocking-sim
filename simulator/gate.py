from dataclasses import dataclass
from typing import final

from agent.vector import Vector
from config import Barrier
from simulator.wall import Wall


@final
@dataclass(frozen=True)
class Gate:
    """A wall across the flight path, split in two by one gap in its middle."""

    barrier: Barrier

    def walls(self) -> tuple:
        return (
            Wall(
                Vector(self.barrier.across, -self.barrier.span / 2),
                Vector(self.barrier.across, -self.barrier.gap / 2),
            ),
            Wall(
                Vector(self.barrier.across, self.barrier.gap / 2),
                Vector(self.barrier.across, self.barrier.span / 2),
            ),
        )
