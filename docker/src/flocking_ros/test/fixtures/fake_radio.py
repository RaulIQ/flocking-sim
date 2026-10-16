from dataclasses import dataclass
from typing import final


@final
@dataclass(frozen=True)
class FakeRadio:
    """Publisher that keeps every message it is asked to send."""

    sent: list

    def publish(self, message: object) -> None:
        self.sent.append(message)
