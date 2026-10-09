from dataclasses import dataclass
from typing import final

from agent.command import Command
from agent.signals import Signals
from agent.vector import Vector


@final
@dataclass(frozen=True)
class Motion:
    """How one drone itself moves: its velocity in its own frame and how fast it turns."""

    velocity: Vector
    spin: float


@final
@dataclass(frozen=True)
class Senses:
    """Everything one drone is told in one tick, all of it in its own frame.

    Its own motion, the separate measurements of its neighbours, the nearest
    points of the walls around it, and what the pilot asks of it. No place on
    a map and no shared direction ever get in here.
    """

    motion: Motion
    signals: Signals
    obstacles: tuple
    request: Command
