from dataclasses import dataclass
from typing import final

from agent.command import Command
from agent.vector import Vector
from simulator.body import Body


@final
@dataclass(frozen=True)
class Route:
    """The path of a scripted pilot: places to visit in order at a cruising speed, then a hover.

    A place counts as visited once the drone comes within the reach of it.
    """

    places: tuple
    speed: float
    reach: float

    def rest(self, body: Body) -> "Route":
        if self.places and self.places[0].minus(body.position).length() < self.reach:
            return Route(self.places[1:], self.speed, self.reach)
        return self

    def command(self, body: Body) -> Command:
        if not self.places:
            return Command(Vector(0.0, 0.0), 0.0)
        return Command(
            self.places[0]
            .minus(body.position)
            .times(self.speed / self.reach)
            .capped(self.speed)
            .turned(-body.heading),
            0.0,
        )
