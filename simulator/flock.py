from dataclasses import dataclass
from typing import final

from agent.command import Command
from agent.mind import Mind
from agent.neighbour import Neighbour
from agent.senses import Senses
from agent.vector import Vector
from config import Limits
from simulator.drone import Drone


@final
@dataclass(frozen=True)
class Flock:
    """Every drone in the air, each flown by its own mind on what it alone senses.

    Until the sensors are built, each drone is told its true velocity, the true
    places of the others and the nearest point of every wall, already turned
    into its own frame, and nothing else. The lead is a
    mark on a drone, not a kind of drone, so it can move from one to another.
    """

    drones: tuple

    def leader(self) -> Drone:
        for drone in self.drones:
            if drone.leader:
                return drone
        raise LookupError(f"There is no leader among {len(self.drones)} drones")

    def seen(self, drone: Drone) -> tuple:
        return tuple(
            Neighbour(
                other.body.position.minus(drone.body.position).turned(
                    -drone.body.heading
                ),
                other.leader,
            )
            for other in self.drones
            if other is not drone
        )

    def felt(self, drone: Drone, walls: tuple) -> tuple:
        return tuple(
            wall.nearest(drone.body.position)
            .minus(drone.body.position)
            .turned(-drone.body.heading)
            for wall in walls
        )

    def led(self, index: int) -> "Flock":
        return Flock(
            tuple(
                Drone(drone.body, drone.trail, place == index)
                for place, drone in enumerate(self.drones)
            )
        )

    def passed(self) -> "Flock":
        return self.led((self.drones.index(self.leader()) + 1) % len(self.drones))

    def picked(self, place: Vector, reach: float) -> "Flock":
        index = min(
            range(len(self.drones)),
            key=lambda index: self.drones[index].body.position.minus(place).length(),
        )
        if self.drones[index].body.position.minus(place).length() > reach:
            return self
        return self.led(index)

    def sensed(self, drone: Drone, request: Command, walls: tuple) -> Senses:
        return Senses(
            drone.body.velocity.turned(-drone.body.heading),
            self.seen(drone),
            self.felt(drone, walls),
            request,
        )

    def moved(
        self,
        request: Command,
        mind: Mind,
        walls: tuple,
        limits: Limits,
        lapse: float,
    ) -> "Flock":
        return Flock(
            tuple(
                drone.moved(
                    mind.led(drone.leader).command(
                        self.sensed(drone, request, walls)
                    ),
                    limits,
                    lapse,
                )
                for drone in self.drones
            )
        )
