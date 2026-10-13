from dataclasses import dataclass
from math import pi, tau
from typing import final


@final
@dataclass(frozen=True)
class Attitude:
    """How the autopilot says a copter is turned: its yaw and its yaw rate.

    The autopilot counts the yaw clockwise from the north, while the simulator
    counts the heading counterclockwise from the east.
    """

    yaw: float
    rate: float

    def heading(self) -> float:
        return (pi / 2 - self.yaw) % tau

    def spin(self) -> float:
        return -self.rate
