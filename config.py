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
    """The canvas in pixels and how many pixels cover one metre."""

    width: int
    height: int
    scale: float


@final
@dataclass(frozen=True)
class Shape:
    """How one drone looks, in metres, with a trail counted in frames."""

    radius: float
    nose: float
    trail: int


@final
@dataclass(frozen=True)
class Settings:
    """Every tunable number of the simulation, with the frame rate in hertz."""

    limits: Limits
    window: Window
    shape: Shape
    rate: int


def defaults() -> Settings:
    return Settings(
        Limits(2.0, 4.0, 1.8, 8.0),
        Window(1000, 700, 60.0),
        Shape(0.1, 0.35, 600),
        60,
    )
