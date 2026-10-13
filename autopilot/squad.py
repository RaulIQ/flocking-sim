from dataclasses import dataclass
from typing import final

from autopilot.spot import Spot


@final
@dataclass(frozen=True)
class Squad:
    """Every copter of one flight, each on a link of its own, seen in one flat frame around the origin."""

    links: tuple
    origin: Spot

    def tune(self, rate: float, patience: float) -> None:
        for link in self.links:
            link.expect("HEARTBEAT", patience)
            link.subscribe(rate)
            link.expect("GLOBAL_POSITION_INT", patience)
            link.expect("ATTITUDE", patience)

    def bodies(self) -> tuple:
        return tuple(link.telemetry().body(self.origin) for link in self.links)
