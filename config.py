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
class Window:
    """The canvas in pixels, the pixels that cover one metre and the frames per second."""

    width: int
    height: int
    scale: float
    rate: int


@final
@dataclass(frozen=True)
class Shape:
    """How one drone looks, in metres, with a trail counted in frames."""

    radius: float
    nose: float
    trail: int


@final
@dataclass(frozen=True)
class Bubbles:
    """How wide both bubbles around one drone reach, in metres."""

    hard: float
    soft: float


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
    """How a follower is tied to its peers and to its leader, and how many peers it counts."""

    peers: Spring
    leader: Spring
    crowd: int


@final
@dataclass(frozen=True)
class Swarm:
    """How many drones fly, how far apart they start, their bubbles and their ties."""

    count: int
    spacing: float
    bubbles: Bubbles
    cloud: Cloud


@final
@dataclass(frozen=True)
class Settings:
    """Every tunable number of the simulation."""

    limits: Limits
    window: Window
    shape: Shape
    swarm: Swarm


def defaults() -> Settings:
    return Settings(
        Limits(2.0, 4.0, 1.8, 8.0),
        Window(1000, 700, 60.0, 60),
        Shape(0.1, 0.35, 600),
        Swarm(
            8,
            1.2,
            Bubbles(0.25, 0.6),
            Cloud(Spring(1.2, 4.0, 0.5, 1.0), Spring(1.2, 4.0, 1.5, 1.5), 6),
        ),
    )
