from dataclasses import dataclass
from typing import final

from agent.tuning import Limits


@final
@dataclass(frozen=True)
class Kinematics:
    """The air as a formula: every drone obeys its command within its limits, one exact step at a time."""

    limits: Limits
    lapse: float

    def moved(self, bodies: tuple, commands: tuple) -> tuple:
        return tuple(
            body.moved(command, self.limits, self.lapse)
            for body, command in zip(bodies, commands, strict=True)
        )
