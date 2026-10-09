from dataclasses import dataclass
from typing import final

from agent.command import Command
from agent.instinct import Instinct
from agent.senses import Senses
from agent.shield import Shield
from agent.tracker import Tracker
from agent.tracks import Tracks


@final
@dataclass(frozen=True)
class Mind:
    """The whole algorithm of one drone: what it senses goes in, the velocity it asks for comes out.

    The lead is a state of the mind, not another kind of mind. A leader flies
    what its pilot asks, kept clear of walls; a follower flies by its instinct
    among the neighbours it can place. Either one slows down near a neighbour
    it knows only by distance. What a drone remembers of its neighbours lives
    outside the mind, in the tracks it is handed and hands back.
    """

    instinct: Instinct
    shield: Shield
    tracker: Tracker
    leader: bool

    def led(self, leader: bool) -> "Mind":
        return Mind(self.instinct, self.shield, self.tracker, leader)

    def recalled(self, tracks: Tracks, senses: Senses) -> Tracks:
        return self.tracker.after(tracks, senses)

    def command(self, tracks: Tracks, senses: Senses) -> Command:
        return self.shield.slowed(
            self.shield.command(
                senses.request, senses.motion.velocity, senses.obstacles
            )
            if self.leader
            else self.instinct.command(tracks.sighted(), senses.obstacles),
            tracks.blind(),
        )
