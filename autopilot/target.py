from dataclasses import dataclass
from typing import final

from agent.command import Command


@final
@dataclass(frozen=True)
class Target:
    """What an autopilot is asked to fly, in its own frame, for one command of the agent.

    The agent counts sideways to the left and turns counterclockwise, while
    the autopilot counts sideways to the right and turns clockwise.
    """

    command: Command

    def forward(self) -> float:
        return self.command.velocity.x

    def right(self) -> float:
        return -self.command.velocity.y

    def rate(self) -> float:
        return -self.command.spin
