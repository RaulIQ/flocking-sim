from dataclasses import dataclass
from typing import final

import pygame
from pygame import K_ESCAPE, KEYDOWN, QUIT

from agent.command import Command
from config import Settings
from simulator.aim import Aim
from simulator.baton import Baton
from simulator.control import Pilot
from simulator.stage import Stage
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
                (self.settings.picture.window.width, self.settings.picture.window.height)
            ),
            self.settings,
        )
        pilot = Pilot(self.settings.limits)
        aim = Aim(self.settings.limits, self.settings.picture.shape.radius)
        baton = Baton(view, self.settings.swarm.bubbles.soft)
        stage = Stage(self.settings)
        clock = pygame.time.Clock()
        flock = stage.flock()
        events = pygame.event.get()
        while self.alive(events):
            clock.tick(self.settings.picture.window.rate)
            flock = baton.passed(flock, events)
            flock = stage.after(
                flock,
                Command(
                    pilot.velocity(tuple(pygame.key.get_pressed())),
                    aim.spin(
                        flock.leader().body,
                        view.place(pygame.mouse.get_pos()),
                        stage.lapse(),
                    ),
                ),
            )
            view.show(flock, stage.walls())
            pygame.display.flip()
            events = pygame.event.get()
        pygame.quit()

    def alive(self, events) -> bool:
        return not [
            event
            for event in events
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE)
        ]
