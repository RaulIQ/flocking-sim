from dataclasses import dataclass
from typing import final

from scenarios.scenario import Scenario
from scenarios.tally import Tally
from simulator.flock import Flock


@final
@dataclass(frozen=True)
class Report:
    """The summary of one finished run, in lines a person reads and a diff compares."""

    name: str
    scenario: Scenario
    tally: Tally
    flock: Flock

    def lines(self) -> tuple:
        return (
            f"scenario: {self.name}",
            f"story: {self.scenario.story}",
            f"simulated, s: {self.scenario.seconds:.1f}",
            f"drones: {len(self.flock.drones)}",
            f"closest pair of drones, m: {self.tally.pair:.3f}",
            f"closest drone to a wall, m: {self.tally.wall:.3f}",
            f"frames with a hard bubble breached: {self.tally.breaches}",
            f"drones beyond the wall at the end: {self.tally.passage.count}"
            f" of {len(self.flock.drones)}",
            f"last change beyond the wall at, s: {self.tally.passage.time:.1f}",
            "farthest drone from the leader at the end, m: {:.3f}".format(
                max(
                    drone.body.position.minus(self.flock.leader().body.position).length()
                    for drone in self.flock.drones
                )
            ),
            "fastest follower at the end, m/s: {:.3f}".format(
                max(
                    (
                        drone.body.velocity.length()
                        for drone in self.flock.drones
                        if not drone.leader
                    ),
                    default=0.0,
                )
            ),
            f"settings: {self.scenario.settings}",
        )
