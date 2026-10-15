from dataclasses import dataclass
from time import monotonic, sleep
from typing import final

from flocking_ros.flight.maneuver import Maneuver
from flocking_ros.flight.refusal import Refusal


@final
@dataclass(frozen=True)
class Persistent(Maneuver):
    """
    Maneuver flown again from its first step until it is flown or its seconds run out.

    ArduCopter in Gazebo refuses a takeoff for a while after its checks
    before arming pass, with no sign of when it will accept one, and it
    disarms motors left idle on the ground, so the whole maneuver is flown
    again rather than its last step. The last refusal is raised once the
    seconds are over.
    """

    origin: Maneuver
    seconds: float
    pause: float

    def fly(self) -> None:
        end = monotonic() + self.seconds
        while True:
            try:
                self.origin.fly()
                return
            except Refusal:
                if monotonic() > end:
                    raise
                sleep(self.pause)
