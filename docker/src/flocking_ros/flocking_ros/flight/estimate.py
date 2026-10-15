from collections import deque
from collections.abc import Callable
from dataclasses import dataclass, field
from threading import Condition
from typing import final

from flocking_ros.flight.refusal import Refusal
from geometry_msgs.msg import PoseStamped


@final
@dataclass(frozen=True)
class Estimate:
    """Latest position the autopilot estimates for itself, awaited for a bounded time."""

    timeout: float
    latest: deque = field(default_factory=lambda: deque(maxlen=1))
    change: Condition = field(default_factory=Condition)

    def record(self, pose: PoseStamped) -> None:
        with self.change:
            self.latest.append(pose)
            self.change.notify_all()

    def expect(self, check: Callable[[PoseStamped], bool], reason: str) -> None:
        with self.change:
            if not self.change.wait_for(lambda: any(map(check, self.latest)), self.timeout):
                raise Refusal(reason)
