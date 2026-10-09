from dataclasses import dataclass
from typing import final

from pygame import Surface, draw

from agent.vector import Vector
from config import Settings
from simulator.flock import Flock


@final
@dataclass(frozen=True)
class View:
    """The top-down picture of the world, drawn on a pygame surface."""

    surface: Surface
    settings: Settings

    def show(self, flock: Flock, walls: tuple) -> None:
        shape = self.settings.picture.shape
        bubbles = self.settings.swarm.bubbles
        scale = self.settings.picture.window.scale
        self.surface.fill((18, 19, 24))
        for wall in walls:
            draw.line(
                self.surface, (176, 182, 196), self.spot(wall.start), self.spot(wall.end), 3
            )
        for drone in flock.drones:
            if len(drone.trail.points) > 1:
                draw.aalines(
                    self.surface,
                    (64, 82, 112),
                    False,
                    [self.spot(point) for point in drone.trail.points],
                )
        for drone in flock.drones:
            draw.circle(
                self.surface, (58, 110, 150), self.spot(drone.body.position), bubbles.soft * scale, 1
            )
            draw.circle(
                self.surface, (200, 80, 80), self.spot(drone.body.position), bubbles.hard * scale, 1
            )
        for drone in flock.drones:
            draw.line(
                self.surface,
                (247, 168, 58) if drone.leader else (150, 158, 172),
                self.spot(drone.body.position),
                self.spot(
                    drone.body.position.plus(
                        Vector(shape.nose, 0.0).turned(drone.body.heading)
                    )
                ),
                2,
            )
            draw.circle(
                self.surface,
                (247, 168, 58) if drone.leader else (232, 238, 248),
                self.spot(drone.body.position),
                max(3.0, shape.radius * scale),
            )

    def spot(self, place: Vector) -> tuple:
        window = self.settings.picture.window
        return (
            window.width / 2 + place.x * window.scale,
            window.height / 2 - place.y * window.scale,
        )

    def place(self, pixel) -> Vector:
        window = self.settings.picture.window
        return Vector(
            (pixel[0] - window.width / 2) / window.scale,
            (window.height / 2 - pixel[1]) / window.scale,
        )
