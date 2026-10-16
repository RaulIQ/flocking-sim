from dataclasses import dataclass
from typing import final

from agent.vector import Vector


@final
@dataclass(frozen=True)
class Pillar:
    """A round pillar standing upright, solid all through, felt by the point of its side nearest a drone."""

    centre: Vector
    radius: float

    def nearest(self, place: Vector) -> Vector:
        offset = place.minus(self.centre)
        if offset.length() == 0.0:
            return self.centre.plus(Vector(self.radius, 0.0))
        return self.centre.plus(offset.times(self.radius / offset.length()))

    def drawn(self, canvas) -> None:
        canvas.disc(self.centre, self.radius)
