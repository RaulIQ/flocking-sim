import csv
from dataclasses import dataclass
from math import inf
from pathlib import Path
from typing import final

from scenarios.report import Report
from scenarios.scenario import Scenario
from scenarios.tally import Passage, Tally
from simulator.stage import Stage


@final
@dataclass(frozen=True)
class Trial:
    """One run of a scenario, written down as a trace of every drone and a summary.

    The trace keeps one frame out of every stride. Nothing in a run is random,
    so the same scenario always writes the same two files.
    """

    name: str
    scenario: Scenario
    stride: int

    def frames(self):
        stage = Stage(self.scenario.settings)
        route = self.scenario.route
        flock = stage.flock()
        for frame in range(round(self.scenario.seconds / stage.lapse())):
            route = route.rest(flock.leader().body)
            flock = stage.after(flock, route.command(flock.leader().body))
            yield (frame + 1) * stage.lapse(), flock

    def run(self, folder: Path) -> Report:
        folder.mkdir(parents=True, exist_ok=True)
        tally = Tally(inf, inf, 0, Passage(0, 0.0))
        flock = Stage(self.scenario.settings).flock()
        with open(folder / f"{self.name}.csv", "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(("time", "drone", "leader", "x", "y", "heading", "vx", "vy"))
            for frame, (time, flock) in enumerate(self.frames()):
                tally = tally.after(time, flock, self.scenario.settings)
                if frame % self.stride == 0:
                    writer.writerows(
                        (
                            f"{time:.3f}",
                            index,
                            int(drone.leader),
                            f"{drone.body.position.x:.4f}",
                            f"{drone.body.position.y:.4f}",
                            f"{drone.body.heading:.4f}",
                            f"{drone.body.velocity.x:.4f}",
                            f"{drone.body.velocity.y:.4f}",
                        )
                        for index, drone in enumerate(flock.drones)
                    )
        report = Report(self.name, self.scenario, tally, flock)
        (folder / f"{self.name}.txt").write_text("\n".join(report.lines()) + "\n")
        return report
