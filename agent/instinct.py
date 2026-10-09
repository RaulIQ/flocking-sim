from dataclasses import dataclass
from functools import reduce
from typing import final

from agent.bond import Bond
from agent.command import Command
from agent.vector import Vector
from config import Cloud, Limits


@final
@dataclass(frozen=True)
class Instinct:
    """What one follower wants: to keep its place among the nearest few and near the leader.

    Counting only the nearest few peers instead of everyone in range follows
    the topological neighbourhood that Ballerini 2008 measured in starlings.
    """

    cloud: Cloud
    limits: Limits

    def command(self, neighbours: tuple) -> Command:
        return Command(
            reduce(
                Vector.plus,
                [
                    Bond(self.cloud.leader).velocity(neighbour.offset)
                    for neighbour in neighbours
                    if neighbour.leader
                ]
                + [
                    Bond(self.cloud.peers).velocity(neighbour.offset)
                    for neighbour in sorted(
                        (peer for peer in neighbours if not peer.leader),
                        key=lambda peer: peer.offset.length(),
                    )[: self.cloud.crowd]
                ],
                Vector(0.0, 0.0),
            ).capped(self.limits.speed),
            0.0,
        )
