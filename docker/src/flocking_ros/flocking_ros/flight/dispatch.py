from collections.abc import Mapping
from dataclasses import dataclass
from typing import final

from flocking_ros.flight.maneuver import Maneuver
from flocking_ros.flight.refusal import Refusal
from rclpy.impl.rcutils_logger import RcutilsLogger
from std_msgs.msg import String


@final
@dataclass(frozen=True)
class Dispatch:
    """Desk that answers each command word with its maneuver and logs the outcome."""

    maneuvers: Mapping[str, Maneuver]
    log: RcutilsLogger

    def receive(self, command: String) -> None:
        if command.data in self.maneuvers:
            try:
                self.maneuvers[command.data].fly()
                self.log.info(f'Command {command.data} succeeded')
            except Refusal as refusal:
                self.log.error(f'Command {command.data} failed: {refusal}')
        else:
            self.log.error(f'Command {command.data} is unknown')
