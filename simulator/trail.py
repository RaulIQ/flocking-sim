from dataclasses import dataclass
from typing import final

from simulator.vector import Vector


@final
@dataclass(frozen=True)
class Trail:
    """The recent path of one drone, oldest place first, forgetting the rest."""

    points: tuple
    limit: int

    def extended(self, point: Vector) -> "Trail":
        points = self.points + (point,)
        return Trail(points[max(0, len(points) - self.limit) :], self.limit)
