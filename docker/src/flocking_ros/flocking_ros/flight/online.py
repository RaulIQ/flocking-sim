from dataclasses import dataclass
from typing import final

from flocking_ros.flight.status import Status
from flocking_ros.flight.vehicle import Vehicle


@final
@dataclass(frozen=True)
class Online(Vehicle):
    """Vehicle that obeys only while the autopilot stays connected."""

    origin: Vehicle
    status: Status

    def switch(self, mode: str) -> None:
        self.status.expect(lambda state: state.connected, 'Autopilot is not connected')
        self.origin.switch(mode)

    def arm(self) -> None:
        self.status.expect(lambda state: state.connected, 'Autopilot is not connected')
        self.origin.arm()

    def ascend(self, altitude: float) -> None:
        self.status.expect(lambda state: state.connected, 'Autopilot is not connected')
        self.origin.ascend(altitude)
