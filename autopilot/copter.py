from dataclasses import dataclass
from typing import final

from pymavlink import mavutil

from autopilot.link import Link


@final
@dataclass(frozen=True)
class Copter:
    """One copter as a pilot knows it: what state it is in and what it can be told to do.

    ArduCopter numbers its guided mode, the one that obeys targets, as four.
    """

    link: Link

    def steady(self) -> bool:
        return bool(
            "EKF_STATUS_REPORT" in self.link.heard()
            and self.link.heard()["EKF_STATUS_REPORT"].flags
            & mavutil.mavlink.EKF_POS_HORIZ_ABS
        )

    def guided(self) -> bool:
        return (
            "HEARTBEAT" in self.link.heard()
            and self.link.heard()["HEARTBEAT"].custom_mode == 4
        )

    def armed(self) -> bool:
        return bool(
            "HEARTBEAT" in self.link.heard()
            and self.link.heard()["HEARTBEAT"].base_mode
            & mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED
        )

    def height(self) -> float:
        return self.link.heard()["GLOBAL_POSITION_INT"].relative_alt / 1000

    def guide(self) -> None:
        self.link.order(
            mavutil.mavlink.MAV_CMD_DO_SET_MODE,
            mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
            4,
        )

    def arm(self) -> None:
        self.link.order(mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM, 1)

    def rise(self, altitude: float) -> None:
        self.link.order(mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, 0, 0, 0, 0, 0, 0, altitude)
