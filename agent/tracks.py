from dataclasses import dataclass
from typing import final

from agent.neighbour import Neighbour


@final
@dataclass(frozen=True)
class Track:
    """What one drone believes about one neighbour, under the tag it is heard by.

    A neighbour never yet sighted by the camera has a distance but no
    direction: only the length of its offset means anything.
    """

    tag: int
    neighbour: Neighbour
    sighted: bool


@final
@dataclass(frozen=True)
class Tracks:
    """The memory of one drone between two ticks: a track for every neighbour it has heard of."""

    items: tuple

    def sighted(self) -> tuple:
        return tuple(track.neighbour for track in self.items if track.sighted)

    def blind(self) -> tuple:
        return tuple(
            track.neighbour.offset.length()
            for track in self.items
            if not track.sighted
        )
