from collections import deque
from collections.abc import Callable
from dataclasses import dataclass, field
from threading import Condition
from typing import final

from flocking_ros.flight.refusal import Refusal
from mavros_msgs.msg import State


@final
@dataclass(frozen=True)
class Status:
    """Latest state reported by the autopilot, awaited for a bounded time."""

    timeout: float
    latest: deque = field(default_factory=lambda: deque(maxlen=1))
    change: Condition = field(default_factory=Condition)

    def record(self, state: State) -> None:
        with self.change:
            self.latest.append(state)
            self.change.notify_all()

    def expect(self, check: Callable[[State], bool], reason: str) -> None:
        with self.change:
            if not self.change.wait_for(lambda: any(map(check, self.latest)), self.timeout):
                raise Refusal(reason)
