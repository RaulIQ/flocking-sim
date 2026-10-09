from dataclasses import dataclass
from functools import reduce
from typing import final

from agent.bond import Bond
from agent.command import Command
from agent.tuning import Cloud, Limits
from agent.vector import Vector


@final
@dataclass(frozen=True)
class Instinct:
    """What one follower wants: its place among the nearest few, near the leader, clear of walls.

    Counting only the nearest few peers instead of everyone in range follows
    the topological neighbourhood that Ballerini 2008 measured in starlings.
    """

    cloud: Cloud
    limits: Limits

    def command(self, neighbours: tuple, obstacles: tuple) -> Command:
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
                ]
                + [Bond(self.cloud.walls).velocity(offset) for offset in obstacles],
                Vector(0.0, 0.0),
            ).capped(self.limits.speed),
            0.0,
        )
