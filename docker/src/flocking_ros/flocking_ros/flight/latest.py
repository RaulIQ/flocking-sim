from collections import deque
from collections.abc import Callable
from dataclasses import dataclass, field
from threading import Condition
from typing import Any, final

from flocking_ros.flight.refusal import Refusal


@final
@dataclass(frozen=True)
class Latest:
    """
    Latest message of one kind from the autopilot, awaited for a bounded time.

    The state of the autopilot and the position it estimates for itself are
    both kept this way.
    """

    timeout: float
    latest: deque = field(default_factory=lambda: deque(maxlen=1))
    change: Condition = field(default_factory=Condition)

    def record(self, message: Any) -> None:
        with self.change:
            self.latest.append(message)
            self.change.notify_all()

    def expect(self, check: Callable[[Any], bool], reason: str) -> None:
        with self.change:
            if not self.change.wait_for(lambda: any(map(check, self.latest)), self.timeout):
                raise Refusal(reason)
