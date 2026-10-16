from dataclasses import dataclass
from typing import final

from agent.vector import Vector
from simulator.course import Course
from simulator.wall import Wall


@final
@dataclass(frozen=True)
class Gate(Course):
    """A wall standing across the x axis, split into pieces by the gaps in it.

    It stands at x across, reaches span along y, and every gap is gap wide
    around one of the centres.
    """

    across: float
    span: float
    gap: float
    centres: tuple

    def walls(self) -> tuple:
        edges = (
            -self.span / 2,
            *(
                centre + side * self.gap / 2
                for centre in sorted(self.centres)
                for side in (-1, 1)
            ),
            self.span / 2,
        )
        return tuple(
            Wall(Vector(self.across, low), Vector(self.across, high))
            for low, high in zip(edges[::2], edges[1::2])
        )

    def passed(self, place: Vector) -> bool:
        return place.x > self.across
