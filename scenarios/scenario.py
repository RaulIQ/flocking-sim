from dataclasses import dataclass
from typing import final

from config import Settings
from scenarios.route import Route


@final
@dataclass(frozen=True)
class Scenario:
    """One repeatable experiment: what it is for, the world, the route of the leader and its length."""

    story: str
    settings: Settings
    route: Route
    seconds: float
