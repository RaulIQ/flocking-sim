from contextlib import ExitStack, contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import final

from autopilot.sitl import Sitl
from config import Fleet
from simulator.muster import Muster


@final
@dataclass(frozen=True)
class Hangar:
    """Every simulated copter of one fleet, each standing where its kinematic twin starts.

    The copters run only while the hangar is open, so that none of them
    outlives the flight it was started for.
    """

    fleet: Fleet
    spacing: float

    def copters(self) -> tuple:
        return tuple(
            Sitl(
                self.fleet.source,
                number,
                self.fleet.origin.shifted(place),
                self.fleet.port,
            )
            for number, place in enumerate(
                Muster(self.fleet.count, self.spacing).places()
            )
        )

    @contextmanager
    def opened(self, folder: Path):
        with ExitStack() as stack:
            yield tuple(
                stack.enter_context(copter.running(folder))
                for copter in self.copters()
            )
