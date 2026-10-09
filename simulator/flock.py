from dataclasses import dataclass
from math import atan2
from typing import final

from agent.command import Command
from agent.mind import Mind
from agent.senses import Motion, Senses
from agent.signals import Bearing, Range, Role, Signals
from agent.tuning import Limits
from agent.vector import Vector
from simulator.drone import Drone


@final
@dataclass(frozen=True)
class Flock:
    """Every drone in the air, each flown by its own mind on what it alone senses.

    Each drone is told how it moves itself, how far every other drone is, at
    what angle from its nose it sees each of them, who says it leads, and the
    nearest point of every wall. For now every measurement is exact, arrives
    every tick and the camera sees all the way around. The lead is a
    mark on a drone, not a kind of drone, so it can move from one to another.
    """

    drones: tuple

    def leader(self) -> Drone:
        for drone in self.drones:
            if drone.leader:
                return drone
        raise LookupError(f"There is no leader among {len(self.drones)} drones")

    def heard(self, drone: Drone) -> Signals:
        others = tuple(
            (
                tag,
                other.body.position.minus(drone.body.position).turned(
                    -drone.body.heading
                ),
                other.leader,
            )
            for tag, other in enumerate(self.drones)
            if other is not drone
        )
        return Signals(
            tuple(Range(tag, offset.length()) for tag, offset, leader in others),
            tuple(
                Bearing(tag, atan2(offset.y, offset.x)) for tag, offset, leader in others
            ),
            tuple(Role(tag, leader) for tag, offset, leader in others),
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
                Drone(drone.body, drone.trail, place == index, drone.memory)
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
            Motion(drone.body.velocity.turned(-drone.body.heading), drone.body.spin),
            self.heard(drone),
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
                drone.flown(mind, self.sensed(drone, request, walls), limits, lapse)
                for drone in self.drones
            )
        )
