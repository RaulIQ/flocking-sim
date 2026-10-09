from dataclasses import dataclass
from typing import final

from agent.command import Command
from agent.instinct import Instinct
from agent.senses import Senses
from agent.shield import Shield


@final
@dataclass(frozen=True)
class Mind:
    """The whole algorithm of one drone: what it senses goes in, the velocity it asks for comes out.

    The lead is a state of the mind, not another kind of mind. A leader flies
    what its pilot asks, kept clear of walls; a follower flies by its instinct.
    """

    instinct: Instinct
    shield: Shield
    leader: bool

    def led(self, leader: bool) -> "Mind":
        return Mind(self.instinct, self.shield, leader)

    def command(self, senses: Senses) -> Command:
        if self.leader:
            return self.shield.command(
                senses.request, senses.velocity, senses.obstacles
            )
        return self.instinct.command(senses.neighbours, senses.obstacles)
