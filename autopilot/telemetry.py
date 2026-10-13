from dataclasses import dataclass
from typing import final

from autopilot.attitude import Attitude
from autopilot.fix import Fix
from autopilot.spot import Spot
from simulator.body import Body


@final
@dataclass(frozen=True)
class Telemetry:
    """The latest an autopilot told about one copter: where it is and how it is turned."""

    fix: Fix
    attitude: Attitude

    def body(self, origin: Spot) -> Body:
        return Body(
            self.fix.place(origin),
            self.attitude.heading(),
            self.fix.velocity(),
            self.attitude.spin(),
        )
