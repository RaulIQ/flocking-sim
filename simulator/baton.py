from dataclasses import dataclass
from functools import reduce
from typing import final

from pygame import K_TAB, KEYDOWN, MOUSEBUTTONDOWN

from simulator.flock import Flock
from simulator.view import View


@final
@dataclass(frozen=True)
class Baton:
    """The lead as the pilot hands it around: Tab for the next drone, a click for the one under the pointer."""

    view: View
    reach: float

    def passed(self, flock: Flock, events) -> Flock:
        return reduce(self.after, events, flock)

    def after(self, flock: Flock, event) -> Flock:
        if event.type == KEYDOWN and event.key == K_TAB:
            return flock.passed()
        if event.type == MOUSEBUTTONDOWN and event.button == 1:
            return flock.picked(self.view.place(event.pos), self.reach)
        return flock
