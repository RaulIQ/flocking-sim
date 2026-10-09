from dataclasses import dataclass
from typing import final

from pygame import Surface, display, draw

from config import Settings
from simulator.body import Body
from simulator.trail import Trail
from simulator.vector import Vector


@final
@dataclass(frozen=True)
class View:
    """The top-down picture of the world, drawn on a pygame surface."""

    surface: Surface
    settings: Settings

    def show(self, body: Body, trail: Trail) -> None:
        shape = self.settings.shape
        self.surface.fill((18, 19, 24))
        if len(trail.points) > 1:
            draw.aalines(
                self.surface,
                (64, 82, 112),
                False,
                [self.spot(point) for point in trail.points],
            )
        draw.circle(
            self.surface,
            (232, 238, 248),
            self.spot(body.position),
            max(3.0, shape.radius * self.settings.window.scale),
        )
        draw.line(
            self.surface,
            (247, 168, 58),
            self.spot(body.position),
            self.spot(body.position.plus(Vector(shape.nose, 0.0).turned(body.heading))),
            2,
        )
        display.flip()

    def spot(self, place: Vector) -> tuple:
        window = self.settings.window
        return (
            window.width / 2 + place.x * window.scale,
            window.height / 2 - place.y * window.scale,
        )
