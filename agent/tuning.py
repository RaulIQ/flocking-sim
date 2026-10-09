from dataclasses import dataclass
from typing import final


@final
@dataclass(frozen=True)
class Limits:
    """How briskly one drone may fly, in metres, seconds and radians."""

    speed: float
    push: float
    spin: float
    twist: float


@final
@dataclass(frozen=True)
class Spring:
    """A rest distance in metres, the gains of the shove and the pull, and where the pull saturates."""

    rest: float
    shove: float
    pull: float
    reach: float


@final
@dataclass(frozen=True)
class Cloud:
    """How a follower is tied to its peers and its leader, shoved by walls, and how many peers it counts."""

    peers: Spring
    leader: Spring
    walls: Spring
    crowd: int
