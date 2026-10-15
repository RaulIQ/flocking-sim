from dataclasses import dataclass
from typing import Any, final

from flocking_ros.flight.link import Link


@final
@dataclass(frozen=True)
class FakeLink(Link):
    """Link that records requests and answers them with one canned response."""

    response: Any
    requests: list[Any]

    def ask(self, request: Any) -> Any:
        self.requests.append(request)
        return self.response
