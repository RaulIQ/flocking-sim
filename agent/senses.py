from dataclasses import dataclass
from typing import final

from agent.command import Command
from agent.vector import Vector


@final
@dataclass(frozen=True)
class Senses:
    """Everything one drone is told in one tick, all of it in its own frame.

    Its own velocity, the other drones it knows of, the nearest points of the
    walls around it, and what the pilot asks of it. No place on a map and no
    shared direction ever get in here.
    """

    velocity: Vector
    neighbours: tuple
    obstacles: tuple
    request: Command
