from dataclasses import dataclass
from typing import final

from agent.command import Command
from agent.instinct import Instinct
from agent.shield import Shield
from agent.vector import Vector
from config import Settings
from simulator.body import Body
from simulator.drone import Drone
from simulator.flock import Flock
from simulator.gate import Gate
from simulator.muster import Muster
from simulator.trail import Trail


@final
@dataclass(frozen=True)
class Stage:
    """The simulated world under one set of settings: who starts where and what one tick does.

    The window and every scripted scenario step the world through this one
    class, so that a scenario replays exactly what a pilot would see.
    """

    settings: Settings

    def lapse(self) -> float:
        return 1.0 / self.settings.picture.window.rate

    def walls(self) -> tuple:
        return Gate(self.settings.barrier).walls()

    def flock(self) -> Flock:
        return Flock(
            tuple(
                Drone(
                    Body(place, 0.0, Vector(0.0, 0.0), 0.0),
                    Trail((), self.settings.picture.shape.trail),
                    index == 0,
                )
                for index, place in enumerate(
                    Muster(
                        self.settings.swarm.count, self.settings.swarm.spacing
                    ).places()
                )
            )
        )

    def after(self, flock: Flock, command: Command) -> Flock:
        leader = flock.leader().body
        return flock.moved(
            Shield(
                self.settings.limits, self.settings.swarm.bubbles.hard, self.lapse()
            ).command(
                command,
                leader.velocity.turned(-leader.heading),
                flock.felt(flock.leader(), self.walls()),
            ),
            Instinct(self.settings.swarm.cloud, self.settings.limits),
            self.walls(),
            self.settings.limits,
            self.lapse(),
        )
