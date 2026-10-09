from dataclasses import dataclass
from math import cos, hypot, sin
from typing import final


@final
@dataclass(frozen=True)
class Vector:
    """A pair of metres on the horizontal plane, either a place or an offset."""

    x: float
    y: float

    def plus(self, other: "Vector") -> "Vector":
        return Vector(self.x + other.x, self.y + other.y)

    def minus(self, other: "Vector") -> "Vector":
        return Vector(self.x - other.x, self.y - other.y)

    def times(self, factor: float) -> "Vector":
        return Vector(self.x * factor, self.y * factor)

    def dot(self, other: "Vector") -> float:
        return self.x * other.x + self.y * other.y

    def turned(self, angle: float) -> "Vector":
        return Vector(
            self.x * cos(angle) - self.y * sin(angle),
            self.x * sin(angle) + self.y * cos(angle),
        )

    def length(self) -> float:
        return hypot(self.x, self.y)

    def capped(self, limit: float) -> "Vector":
        length = self.length()
        return self if length <= limit else self.times(limit / length)
