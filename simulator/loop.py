from dataclasses import dataclass
from typing import final

import pygame
from pygame import K_ESCAPE, KEYDOWN, QUIT

from config import Settings
from simulator.aim import Aim
from simulator.body import Body, Command
from simulator.control import Pilot
from simulator.drone import Drone
from simulator.flock import Flock
from simulator.muster import Muster
from simulator.trail import Trail
from simulator.vector import Vector
from simulator.view import View


@final
@dataclass(frozen=True)
class Flight:
    """One interactive run: a window, a keyboard and a swarm behind its leader."""

    settings: Settings

    def run(self) -> None:
        pygame.init()
        pygame.display.set_caption("flocking-sim")
        view = View(
            pygame.display.set_mode(
                (self.settings.window.width, self.settings.window.height)
            ),
            self.settings,
        )
        pilot = Pilot(self.settings.limits)
        aim = Aim(self.settings.limits, self.settings.shape.radius)
        clock = pygame.time.Clock()
        lapse = 1.0 / self.settings.window.rate
        flock = Flock(
            tuple(
                Drone(
                    Body(place, 0.0, Vector(0.0, 0.0), 0.0),
                    Trail((), self.settings.shape.trail),
                    index == 0,
                )
                for index, place in enumerate(
                    Muster(
                        self.settings.swarm.count, self.settings.swarm.spacing
                    ).places()
                )
            )
        )
        while self.alive():
            clock.tick(self.settings.window.rate)
            flock = flock.moved(
                Command(
                    pilot.velocity(tuple(pygame.key.get_pressed())),
                    aim.spin(
                        flock.leader().body, view.place(pygame.mouse.get_pos()), lapse
                    ),
                ),
                self.settings.limits,
                lapse,
            )
            view.show(flock)
            pygame.display.flip()
        pygame.quit()

    def alive(self) -> bool:
        return not [
            event
            for event in pygame.event.get()
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE)
        ]
