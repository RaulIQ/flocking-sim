from contextlib import contextmanager
from dataclasses import dataclass
from logging import getLogger
from pathlib import Path
from typing import final

from autopilot.air import Air
from autopilot.hangar import Hangar
from autopilot.hold import Hold
from autopilot.pulse import Pulse
from autopilot.squad import Squad


@final
@dataclass(frozen=True)
class Sortie:
    """One flight of simulated copters: started, readied and lifted on the way in, stopped on the way out.

    A copter needs about three quarters of a minute to learn where it is, so
    it is given a minute and a half, and half a minute for every step of the
    takeoff.
    """

    hangar: Hangar
    hold: Hold
    pulse: Pulse

    @contextmanager
    def flown(self, folder: Path):
        with self.hangar.opened(folder):
            squad = Squad(
                tuple(copter.link() for copter in self.hangar.copters()),
                self.hangar.fleet.origin,
            )
            getLogger(__name__).info(
                "Waiting for %d copters to learn where they are", len(squad.links)
            )
            squad.tune(self.pulse.rate, 90.0)
            getLogger(__name__).info(
                "Lifting %d copters to %.1f metres", len(squad.links), self.hold.altitude
            )
            squad.lift(self.hold.altitude, 30.0)
            getLogger(__name__).info("Flying %d copters", len(squad.links))
            yield Air(squad, self.hold, self.pulse)
