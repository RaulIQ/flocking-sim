from dataclasses import dataclass
from typing import final

from flocking_ros.flight.maneuver import Maneuver
from flocking_ros.flight.vehicle import Vehicle


@final
@dataclass(frozen=True)
class Takeoff(Maneuver):
    """Climb from the ground, each step taken only after the previous one succeeds."""

    vehicle: Vehicle
    altitude: float

    def fly(self) -> None:
        self.vehicle.switch('GUIDED')
        self.vehicle.arm()
        self.vehicle.ascend(self.altitude)
