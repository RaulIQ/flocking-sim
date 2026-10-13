from dataclasses import dataclass
from typing import final

from agent.vector import Vector
from autopilot.spot import Spot


@final
@dataclass(frozen=True)
class Fix:
    """Where the autopilot says a copter is and how fast it moves north and east."""

    spot: Spot
    north: float
    east: float

    def place(self, origin: Spot) -> Vector:
        return origin.offset(self.spot)

    def velocity(self) -> Vector:
        return Vector(self.east, self.north)
