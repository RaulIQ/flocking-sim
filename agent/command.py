from dataclasses import dataclass
from typing import final

from agent.vector import Vector


@final
@dataclass(frozen=True)
class Command:
    """A request in the frame of one drone, x along its nose and y to its left."""

    velocity: Vector
    spin: float
