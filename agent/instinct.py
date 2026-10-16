from dataclasses import dataclass
from functools import reduce
from typing import final

from agent.bond import Bond
from agent.command import Command
from agent.tow import Tow
from agent.tuning import Cloud, Limits
from agent.vector import Vector


@final
@dataclass(frozen=True)
class Instinct:
    """What one follower wants: its place among the nearest few, near the leader, clear of walls.

    A follower flies along with its leader and only corrects its place on
    top of that, never faster than the leader can pull it, unless it stands
    in the way of the leader and steps aside. The turn its pilot asks of the
    leader reaches the follower too and bends that way. This is the
    velocity matching of Reynolds 1987 and Olfati-Saber 2006, kept to the
    leader alone. It lets the pulls and the shoves stay gentle, which a drone
    that answers late needs in order not to sway.

    Counting only the nearest few peers instead of everyone in range follows
    the topological neighbourhood that Ballerini 2008 measured in starlings.
    """

    cloud: Cloud
    limits: Limits

    def command(self, neighbours: tuple, obstacles: tuple, turn: float) -> Command:
        return Command(
            reduce(
                Vector.plus,
                [
                    Tow(self.cloud.leader, self.limits, turn).carry(neighbour)
                    for neighbour in neighbours
                    if neighbour.leader
                ],
                reduce(
                    Vector.plus,
                    [
                        Tow(self.cloud.leader, self.limits, turn).hold(neighbour)
                        for neighbour in neighbours
                        if neighbour.leader
                    ]
                    + [
                        Bond(self.cloud.peers).velocity(neighbour.offset)
                        for neighbour in sorted(
                            (peer for peer in neighbours if not peer.leader),
                            key=lambda peer: peer.offset.length(),
                        )[: self.cloud.crowd]
                    ]
                    + [Bond(self.cloud.walls).velocity(offset) for offset in obstacles],
                    Vector(0.0, 0.0),
                ).capped(self.cloud.leader.spring.pull * self.cloud.leader.spring.reach),
            ).capped(self.limits.speed),
            0.0,
        )
