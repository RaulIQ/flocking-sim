from dataclasses import dataclass
from typing import final


@final
@dataclass(frozen=True)
class Range:
    """How far a neighbour is, as the radio ranging tells it, with no direction."""

    tag: int
    distance: float


@final
@dataclass(frozen=True)
class Bearing:
    """Where the camera sees a neighbour, as an angle from the nose, with no distance."""

    tag: int
    angle: float


@final
@dataclass(frozen=True)
class Role:
    """What a neighbour says of itself over the radio: whether it leads."""

    tag: int
    leader: bool


@final
@dataclass(frozen=True)
class Signals:
    """Everything one drone learns about its neighbours in one tick, each kind on its own.

    A range, a bearing and a role of the same neighbour come from different
    devices and need not arrive together.
    """

    ranges: tuple
    bearings: tuple
    roles: tuple
