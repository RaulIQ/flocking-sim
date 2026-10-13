from dataclasses import dataclass
from math import cos, radians
from typing import final

from agent.vector import Vector


@final
@dataclass(frozen=True)
class Spot:
    """A point on the globe in degrees, around which the ground is taken as flat.

    The flat frame has x to the east and y to the north. The globe is a sphere
    of the radius ArduPilot itself uses, which is exact enough for the few
    hundred metres a swarm covers.
    """

    latitude: float
    longitude: float

    def scale(self) -> Vector:
        return Vector(cos(radians(self.latitude)), 1.0).times(radians(6378100.0))

    def offset(self, other: "Spot") -> Vector:
        return Vector(
            (other.longitude - self.longitude) * self.scale().x,
            (other.latitude - self.latitude) * self.scale().y,
        )

    def shifted(self, offset: Vector) -> "Spot":
        return Spot(
            self.latitude + offset.y / self.scale().y,
            self.longitude + offset.x / self.scale().x,
        )
