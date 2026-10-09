from dataclasses import dataclass
from typing import final

from config import Limits
from simulator.body import Command
from simulator.drone import Drone
from simulator.vector import Vector


@final
@dataclass(frozen=True)
class Flock:
    """Every drone in the air, one of them led by the pilot and the rest hovering."""

    drones: tuple

    def leader(self) -> Drone:
        for drone in self.drones:
            if drone.leader:
                return drone
        raise LookupError(f"There is no leader among {len(self.drones)} drones")

    def moved(self, command: Command, limits: Limits, lapse: float) -> "Flock":
        return Flock(
            tuple(
                drone.moved(
                    command if drone.leader else Command(Vector(0.0, 0.0), 0.0),
                    limits,
                    lapse,
                )
                for drone in self.drones
            )
        )
