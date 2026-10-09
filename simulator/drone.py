from dataclasses import dataclass
from typing import final

from agent.command import Command
from agent.tuning import Limits
from simulator.body import Body
from simulator.trail import Trail


@final
@dataclass(frozen=True)
class Drone:
    """One member of the swarm: its true state, its recent path and whether it leads."""

    body: Body
    trail: Trail
    leader: bool

    def moved(self, command: Command, limits: Limits, lapse: float) -> "Drone":
        body = self.body.moved(command, limits, lapse)
        return Drone(body, self.trail.extended(body.position), self.leader)
