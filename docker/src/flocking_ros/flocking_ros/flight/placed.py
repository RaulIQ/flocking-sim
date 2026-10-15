from dataclasses import dataclass
from typing import final

from flocking_ros.flight.estimate import Estimate
from flocking_ros.flight.vehicle import Vehicle


@final
@dataclass(frozen=True)
class Placed(Vehicle):
    """
    Vehicle that knows where it is before it flies and counts a climb done only at its altitude.

    ArduCopter refuses GUIDED until its position estimate is ready, so a mode
    is asked for only once a position has come. A takeoff is accepted at
    once and flown afterwards, so it is done only when the estimate shows
    nine tenths and a half of the altitude.
    """

    origin: Vehicle
    estimate: Estimate

    def switch(self, mode: str) -> None:
        self.estimate.expect(lambda pose: True, 'Autopilot does not know where it is')
        self.origin.switch(mode)

    def arm(self) -> None:
        self.origin.arm()

    def ascend(self, altitude: float) -> None:
        self.origin.ascend(altitude)
        self.estimate.expect(
            lambda pose: pose.pose.position.z >= 0.95 * altitude,
            f'Autopilot did not reach {altitude} meters',
        )
