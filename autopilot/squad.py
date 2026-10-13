from dataclasses import dataclass
from typing import final

from autopilot.copter import Copter
from autopilot.hold import Hold
from autopilot.patience import Patience
from autopilot.spot import Spot
from autopilot.target import Target


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
            Patience(patience, 0.05).until(
                Copter(link).steady,
                f"Copter {link.system} has no steady position estimate",
            )

    def bodies(self) -> tuple:
        return tuple(link.telemetry().body(self.origin) for link in self.links)

    def lift(self, altitude: float, patience: float) -> None:
        for link in self.links:
            Copter(link).guide()
            Patience(patience, 0.05).until(
                Copter(link).guided, f"Copter {link.system} is not guided"
            )
            Copter(link).arm()
            Patience(patience, 0.05).until(
                Copter(link).armed, f"Copter {link.system} is not armed"
            )
            Copter(link).rise(altitude)
        for link in self.links:
            Patience(patience, 0.05).until(
                lambda: Copter(link).height() >= 0.95 * altitude,
                f"Copter {link.system} is not at {altitude} metres",
            )

    def fly(self, commands: tuple, hold: Hold) -> None:
        for link, command in zip(self.links, commands, strict=True):
            link.steer(Target(command), hold.climb(Copter(link).height()))
