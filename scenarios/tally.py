from dataclasses import dataclass
from itertools import combinations
from math import inf
from typing import final

from config import Settings
from simulator.flock import Flock
from simulator.gate import Gate


@final
@dataclass(frozen=True)
class Passage:
    """How many drones are beyond the wall line and when that number last changed."""

    count: int
    time: float


@final
@dataclass(frozen=True)
class Tally:
    """The worst moments of a run so far: the closest pair, the closest wall, the breached frames.

    A frame counts as breached when two hard bubbles overlap or when a wall
    reaches into the hard bubble of a drone.
    """

    pair: float
    wall: float
    breaches: int
    passage: Passage

    def after(self, time: float, flock: Flock, settings: Settings) -> "Tally":
        pair = min(
            (
                one.body.position.minus(other.body.position).length()
                for one, other in combinations(flock.drones, 2)
            ),
            default=inf,
        )
        wall = min(
            (
                wall.nearest(drone.body.position).minus(drone.body.position).length()
                for drone in flock.drones
                for wall in Gate(settings.barrier).walls()
            ),
            default=inf,
        )
        count = sum(
            drone.body.position.x > settings.barrier.across for drone in flock.drones
        )
        return Tally(
            min(self.pair, pair),
            min(self.wall, wall),
            self.breaches
            + (
                pair < 2.0 * settings.swarm.bubbles.hard
                or wall < settings.swarm.bubbles.hard
            ),
            self.passage if count == self.passage.count else Passage(count, time),
        )
