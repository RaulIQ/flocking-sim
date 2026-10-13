from dataclasses import dataclass
from typing import final

from pymavlink import mavutil

from autopilot.link import Link


@final
@dataclass(frozen=True)
class Decoy:
    """A pretend copter on a free local port that says what it is told and repeats what it was asked."""

    wire: object

    def port(self) -> int:
        return self.wire.listen.getsockname()[1]

    def link(self, system: int) -> Link:
        return Link(
            mavutil.mavlink_connection(f"tcp:127.0.0.1:{self.port()}"), system
        )

    def beat(self) -> None:
        self.wire.recv_msg()
        self.wire.mav.heartbeat_send(
            mavutil.mavlink.MAV_TYPE_QUADROTOR,
            mavutil.mavlink.MAV_AUTOPILOT_ARDUPILOTMEGA,
            0,
            0,
            0,
        )

    def fix(self, latitude: int, longitude: int, north: int, east: int) -> None:
        self.wire.recv_msg()
        self.wire.mav.global_position_int_send(
            0, latitude, longitude, 0, 0, north, east, 0, 0
        )

    def attitude(self, yaw: float, rate: float) -> None:
        self.wire.recv_msg()
        self.wire.mav.attitude_send(0, 0.0, 0.0, yaw, 0.0, 0.0, rate)

    def asked(self):
        return self.wire.recv_match(type="COMMAND_LONG", blocking=True, timeout=5)
