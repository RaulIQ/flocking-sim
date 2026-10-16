from dataclasses import dataclass
from typing import final

from pygame import Surface, draw

from agent.vector import Vector


@final
@dataclass(frozen=True)
class Wall:
    """A straight wall between two places, thin and solid along its whole length."""

    start: Vector
    end: Vector

    def nearest(self, place: Vector) -> Vector:
        span = self.end.minus(self.start)
        return self.start.plus(
            span.times(
                max(0.0, min(1.0, place.minus(self.start).dot(span) / span.dot(span)))
            )
        )

    def drawn(self, surface: Surface, spot, scale: float) -> None:
        draw.line(surface, (176, 182, 196), spot(self.start), spot(self.end), 3)
