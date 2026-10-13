from dataclasses import dataclass
from typing import final

from agent.vector import Vector


@final
@dataclass(frozen=True)
class Neighbour:
    """Another drone as one drone knows it: where it is and how it flies in the own frame, and whether it leads."""

    offset: Vector
    velocity: Vector
    leader: bool
