from dataclasses import dataclass
from typing import final

from agent.tuning import Cloud, Limits, Spring


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
class Picture:
    """What the pilot looks at: the canvas and the look of one drone on it."""

    window: Window
    shape: Shape


@final
@dataclass(frozen=True)
class Bubbles:
    """How wide both bubbles around one drone reach, in metres."""

    hard: float
    soft: float


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
class Barrier:
    """A wall standing across the x axis: where it stands, how long it is, how wide its gaps are and where."""

    across: float
    span: float
    gap: float
    centres: tuple


@final
@dataclass(frozen=True)
class Settings:
    """Every tunable number of the simulation."""

    limits: Limits
    picture: Picture
    swarm: Swarm
    barrier: Barrier


def defaults() -> Settings:
    return Settings(
        Limits(2.0, 4.0, 1.8, 8.0),
        Picture(Window(1000, 700, 60.0, 60), Shape(0.1, 0.35, 600)),
        Swarm(
            8,
            1.2,
            Bubbles(0.25, 0.6),
            Cloud(
                Spring(1.2, 4.0, 0.5, 1.0),
                Spring(1.2, 4.0, 1.5, 1.5),
                Spring(0.6, 8.0, 0.0, 0.0),
                6,
            ),
        ),
        Barrier(4.0, 14.0, 1.2, (0.0,)),
    )
