from dataclasses import dataclass
from typing import final

from agent.command import Command
from agent.mind import Mind
from agent.senses import Senses
from agent.tracks import Tracks
from simulator.body import Body
from simulator.trail import Trail


@final
@dataclass(frozen=True)
class Drone:
    """One member of the swarm: its state, its recent path, whether it leads and what it remembers.

    The memory belongs to the mind on board; the simulator only carries it
    from one tick to the next. A drone starts with nothing remembered.
    """

    body: Body
    trail: Trail
    leader: bool
    memory: Tracks = Tracks(())

    def reminded(self, memory: Tracks) -> "Drone":
        return Drone(self.body, self.trail, self.leader, memory)

    def recalled(self, mind: Mind, senses: Senses) -> "Drone":
        return self.reminded(mind.led(self.leader).recalled(self.memory, senses))

    def command(self, mind: Mind, senses: Senses) -> Command:
        return mind.led(self.leader).command(self.memory, senses)

    def placed(self, body: Body) -> "Drone":
        return Drone(
            body, self.trail.extended(body.position), self.leader, self.memory
        )
