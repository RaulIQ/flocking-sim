from dataclasses import dataclass
from typing import final

from agent.command import Command
from agent.instinct import Instinct
from agent.neighbour import Neighbour
from config import Limits
from simulator.drone import Drone


@final
@dataclass(frozen=True)
class Flock:
    """Every drone in the air, the leader flown by the pilot and the rest by their instinct.

    Until the sensors are built, each follower is told the true places of the
    others, already turned into its own frame, and nothing else.
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

    def moved(
        self, command: Command, instinct: Instinct, limits: Limits, lapse: float
    ) -> "Flock":
        return Flock(
            tuple(
                drone.moved(
                    command if drone.leader else instinct.command(self.seen(drone)),
                    limits,
                    lapse,
                )
                for drone in self.drones
            )
        )
