from dataclasses import dataclass
from typing import final

from flocking_ros.flight.link import Link
from flocking_ros.flight.refusal import Refusal
from flocking_ros.flight.status import Status
from flocking_ros.flight.vehicle import Vehicle
from mavros_msgs.srv import CommandBool, CommandTOL, SetMode


@final
@dataclass(frozen=True)
class MavrosVehicle(Vehicle):
    """ArduPilot aircraft that obeys through MAVROS and confirms through its state."""

    mode: Link
    arming: Link
    takeoff: Link
    status: Status

    def switch(self, mode: str) -> None:
        if not self.mode.ask(SetMode.Request(custom_mode=mode)).mode_sent:
            raise Refusal(f'Autopilot rejected the request for mode {mode}')
        self.status.expect(
            lambda state: state.mode == mode, f'Autopilot did not enter mode {mode}'
        )

    def arm(self) -> None:
        if not self.arming.ask(CommandBool.Request(value=True)).success:
            raise Refusal('Autopilot refused to arm')
        self.status.expect(lambda state: state.armed, 'Autopilot did not report armed motors')

    def ascend(self, altitude: float) -> None:
        if not self.takeoff.ask(CommandTOL.Request(altitude=altitude)).success:
            raise Refusal(f'Autopilot refused to take off to {altitude} meters')
