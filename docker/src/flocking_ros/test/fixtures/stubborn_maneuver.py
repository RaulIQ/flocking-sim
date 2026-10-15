from dataclasses import dataclass
from typing import final

from flocking_ros.flight.maneuver import Maneuver
from flocking_ros.flight.refusal import Refusal


@final
@dataclass(frozen=True)
class StubbornManeuver(Maneuver):
    """Maneuver that fails a given number of times before it is flown, and counts its tries."""

    refusals: list[int]
    tries: list[int]

    def fly(self) -> None:
        self.tries.append(len(self.tries) + 1)
        if self.refusals[0] > 0:
            self.refusals[0] -= 1
            raise Refusal('Stubborn maneuver was refused')
