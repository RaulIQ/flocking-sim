from dataclasses import dataclass
from typing import final

from pygame import (
    KSCAN_A,
    KSCAN_D,
    KSCAN_DOWN,
    KSCAN_LEFT,
    KSCAN_RIGHT,
    KSCAN_S,
    KSCAN_UP,
    KSCAN_W,
)

from config import Limits
from simulator.vector import Vector


@final
@dataclass(frozen=True)
class Pilot:
    """A human at the keyboard, sliding one drone around in its own frame.

    Keys arrive by scancode, one slot per physical place on the keyboard, so
    that a Cyrillic layout, under which no key prints a w, still flies.
    """

    limits: Limits

    def velocity(self, keys) -> Vector:
        return (
            Vector(
                keys[KSCAN_W] + keys[KSCAN_UP] - keys[KSCAN_S] - keys[KSCAN_DOWN],
                keys[KSCAN_A] + keys[KSCAN_LEFT] - keys[KSCAN_D] - keys[KSCAN_RIGHT],
            )
            .capped(1.0)
            .times(self.limits.speed)
        )
