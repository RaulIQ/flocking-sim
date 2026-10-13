from dataclasses import dataclass
from logging import getLogger
from time import monotonic
from typing import final

from autopilot.hold import Hold
from autopilot.pulse import Pulse
from autopilot.squad import Squad


@final
@dataclass(frozen=True)
class Air:
    """The air the drones fly in: commands go up to the copters, one beat passes, telemetry comes down.

    Nothing here computes how a drone moves. Where the drones were is not
    even looked at, since each copter knows that better by itself.
    """

    squad: Squad
    hold: Hold
    pulse: Pulse

    def moved(self, bodies: tuple, commands: tuple) -> tuple:
        self.squad.fly(commands, self.hold)
        self.pulse.wait()
        getLogger(__name__).debug("Tick at %.3f seconds", monotonic())
        return self.squad.bodies()
