from contextlib import ExitStack, contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import final

from autopilot.fleet import Fleet
from autopilot.sitl import Sitl
from simulator.muster import Muster


@final
@dataclass(frozen=True)
class Hangar:
    """Every simulated copter of one fleet, each standing at its place in the muster.

    The copters run only while the hangar is open, so that none of them
    outlives the flight it was started for.
    """

    fleet: Fleet
    muster: Muster

    def copters(self) -> tuple:
        return tuple(
            Sitl(self.fleet, number, self.fleet.origin.shifted(place))
            for number, place in enumerate(self.muster.places())
        )

    @contextmanager
    def opened(self, folder: Path):
        with ExitStack() as stack:
            yield tuple(
                stack.enter_context(copter.running(folder))
                for copter in self.copters()
            )
