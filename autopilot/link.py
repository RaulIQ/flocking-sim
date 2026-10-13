from dataclasses import dataclass
from typing import final

from pymavlink import mavutil

from autopilot.attitude import Attitude
from autopilot.fix import Fix
from autopilot.spot import Spot
from autopilot.telemetry import Telemetry


@final
@dataclass(frozen=True)
class Link:
    """One MAVLink conversation with one copter over a wire of its own.

    The wire keeps the latest message of every kind from every system with the
    time it arrived, so the link only reads what its own copter has said and
    turns the autopilot's whole numbers into degrees and metres a second. A
    copter drops what it is asked before its first heartbeat, so the link
    refuses to ask that early.
    """

    wire: object
    system: int

    def subscribe(self, rate: float) -> None:
        if "HEARTBEAT" not in self.heard():
            raise LookupError(f"Copter {self.system} has not sent a heartbeat yet")
        for kind in (
            mavutil.mavlink.MAVLINK_MSG_ID_GLOBAL_POSITION_INT,
            mavutil.mavlink.MAVLINK_MSG_ID_ATTITUDE,
        ):
            self.wire.mav.command_long_send(
                self.system,
                mavutil.mavlink.MAV_COMP_ID_AUTOPILOT1,
                mavutil.mavlink.MAV_CMD_SET_MESSAGE_INTERVAL,
                0,
                kind,
                1e6 / rate,
                0,
                0,
                0,
                0,
                0,
            )

    def heard(self) -> dict:
        while self.wire.recv_msg() is not None:
            continue
        if self.system not in self.wire.sysid_state:
            return {}
        return self.wire.sysid_state[self.system].messages

    def telemetry(self) -> Telemetry:
        heard = self.heard()
        if not {"GLOBAL_POSITION_INT", "ATTITUDE"} <= set(heard):
            raise LookupError(
                f"Copter {self.system} has not told its position and attitude yet"
            )
        return Telemetry(
            Fix(
                Spot(
                    heard["GLOBAL_POSITION_INT"].lat / 1e7,
                    heard["GLOBAL_POSITION_INT"].lon / 1e7,
                ),
                heard["GLOBAL_POSITION_INT"].vx / 100,
                heard["GLOBAL_POSITION_INT"].vy / 100,
            ),
            Attitude(heard["ATTITUDE"].yaw, heard["ATTITUDE"].yawspeed),
        )
