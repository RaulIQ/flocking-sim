from dataclasses import dataclass
from typing import final

from flocking_ros.flight.maneuver import Maneuver
from flocking_ros.flight.vehicle import Vehicle


@final
@dataclass(frozen=True)
class Transition(Maneuver):
    """Handover of the flight to one autopilot mode, such as LAND or RTL."""

    vehicle: Vehicle
    mode: str

    def fly(self) -> None:
        self.vehicle.switch(self.mode)
