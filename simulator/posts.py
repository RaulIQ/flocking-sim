from dataclasses import dataclass
from typing import final

from agent.vector import Vector
from simulator.course import Course
from simulator.pillar import Pillar


@final
@dataclass(frozen=True)
class Posts(Course):
    """Two round pillars standing across the x axis with a gap between their sides.

    They stand at x across, as wide as twice the radius each, and the gap is
    centred on the axis, so a cloud flying along it passes between them.
    """

    across: float
    gap: float
    radius: float

    def walls(self) -> tuple:
        return tuple(
            Pillar(Vector(self.across, side * (self.gap / 2 + self.radius)), self.radius)
            for side in (-1, 1)
        )

    def passed(self, place: Vector) -> bool:
        return place.x > self.across
