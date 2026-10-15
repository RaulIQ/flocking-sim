from abc import ABC, abstractmethod
from typing import Any


class Link(ABC):
    """Conversation with one service of the autopilot."""

    @abstractmethod
    def ask(self, request: Any) -> Any:
        pass
