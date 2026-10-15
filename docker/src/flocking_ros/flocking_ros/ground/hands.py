from dataclasses import dataclass
from typing import final

from agent.command import Command
from flocking_ros.ground.helm import Helm
import pygame
from scenarios.tally import Tally
from simulator.body import Body
from simulator.control import Pilot
from simulator.flock import Flock


@final
@dataclass(frozen=True)
class Hands(Helm):
    """The pilot at the keyboard of the window, who reports nothing."""

    pilot: Pilot

    def rest(self, body: Body) -> 'Hands':
        return self

    def command(self, body: Body) -> Command:
        return Command(
            self.pilot.velocity(tuple(pygame.key.get_pressed())),
            self.pilot.spin(tuple(pygame.key.get_pressed())),
        )

    def told(self, frame: int, tally: Tally, flock: Flock) -> tuple:
        return ()
