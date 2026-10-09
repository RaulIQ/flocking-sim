from dataclasses import dataclass
from typing import final

from agent.vector import Vector


@final
@dataclass(frozen=True)
class Neighbour:
    """Another drone as one drone knows it: where it is in the own frame and whether it leads."""

    offset: Vector
    leader: bool
