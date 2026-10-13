from collections import deque
from dataclasses import dataclass
from typing import final

from agent.command import Command
from agent.vector import Vector


@final
@dataclass(frozen=True)
class Lag:
    """An air that answers late, the way an autopilot does: a command is eased in and waits its turn.

    Each tick a command closes a share of the gap to what was asked, as a
    first-order lag does, and then stands in a line for a few ticks, as a
    dead time does. The line of commands on their way is the one thing here
    that changes: it is the memory of the air, as a wire is of a link.
    """

    air: object
    line: deque
    wait: int
    ease: float

    def moved(self, bodies: tuple, commands: tuple) -> tuple:
        self.line.append(
            tuple(
                Command(
                    old.velocity.plus(
                        new.velocity.minus(old.velocity).times(self.ease)
                    ),
                    old.spin + (new.spin - old.spin) * self.ease,
                )
                for old, new in zip(
                    self.line[-1]
                    if self.line
                    else (Command(Vector(0.0, 0.0), 0.0),) * len(commands),
                    commands,
                    strict=True,
                )
            )
        )
        if len(self.line) > self.wait + 1:
            self.line.popleft()
        return self.air.moved(
            bodies,
            self.line[0]
            if len(self.line) > self.wait
            else (Command(Vector(0.0, 0.0), 0.0),) * len(commands),
        )
