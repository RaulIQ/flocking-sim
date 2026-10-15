from dataclasses import dataclass
from typing import final

from flocking_ros.flight.latest import Latest
from flocking_ros.flight.vehicle import Vehicle
from pymavlink.dialects.v20 import ardupilotmega as mavlink


@final
@dataclass(frozen=True)
class Placed(Vehicle):
    """
    Vehicle that knows where it is before it flies and counts a climb done only at its altitude.

    ArduCopter refuses GUIDED until its position estimate is ready, so a mode
    is asked for only once a position has come, and it refuses to arm until
    its checks before arming pass, which its health tells, so arming waits for
    them. A takeoff is accepted at
    once and flown afterwards, so it is done only when the estimate shows
    nine tenths and a half of the altitude.
    """

    origin: Vehicle
    estimate: Latest
    health: Latest

    def switch(self, mode: str) -> None:
        self.estimate.expect(lambda pose: True, 'Autopilot does not know where it is')
        self.origin.switch(mode)

    def arm(self) -> None:
        self.health.expect(
            lambda status: bool(status.sensors_health & mavlink.MAV_SYS_STATUS_PREARM_CHECK),
            'Autopilot did not pass its checks before arming',
        )
        self.origin.arm()

    def ascend(self, altitude: float) -> None:
        self.origin.ascend(altitude)
        self.estimate.expect(
            lambda pose: pose.pose.position.z >= 0.95 * altitude,
            f'Autopilot did not reach {altitude} meters',
        )
