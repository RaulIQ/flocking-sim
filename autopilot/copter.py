from dataclasses import dataclass
from typing import final

from pymavlink import mavutil

from autopilot.link import Link


@final
@dataclass(frozen=True)
class Copter:
    """One copter as a pilot knows it: what state it is in and what it can be told to do."""

    link: Link

    def steady(self) -> bool:
        return bool(
            "EKF_STATUS_REPORT" in self.link.heard()
            and self.link.heard()["EKF_STATUS_REPORT"].flags
            & mavutil.mavlink.EKF_POS_HORIZ_ABS
        )
