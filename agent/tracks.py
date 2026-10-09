from dataclasses import dataclass
from typing import final

from agent.neighbour import Neighbour
from agent.vector import Vector


@final
@dataclass(frozen=True)
class Track:
    """What one drone believes about one neighbour: where it is in the own frame and whether it leads.

    A neighbour never yet sighted by the camera has a distance but no
    direction: only the length of its offset means anything.
    """

    tag: int
    offset: Vector
    sighted: bool
    leader: bool


@final
@dataclass(frozen=True)
class Tracks:
    """The memory of one drone between two ticks: a track for every neighbour it has heard of."""

    items: tuple

    def sighted(self) -> tuple:
        return tuple(
            Neighbour(track.offset, track.leader)
            for track in self.items
            if track.sighted
        )

    def blind(self) -> tuple:
        return tuple(
            track.offset.length() for track in self.items if not track.sighted
        )
