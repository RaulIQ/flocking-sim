from dataclasses import dataclass
from typing import final

import pygame
from pygame import K_ESCAPE, KEYDOWN, QUIT

from scenarios.trial import Trial
from simulator.stage import Stage
from simulator.view import View


@final
@dataclass(frozen=True)
class Screening:
    """A trial played in a window at its true pace, for a person to watch."""

    trial: Trial

    def run(self) -> None:
        settings = self.trial.scenario.settings
        pygame.init()
        pygame.display.set_caption(f"flocking-sim: {self.trial.name}")
        view = View(
            pygame.display.set_mode(
                (settings.picture.window.width, settings.picture.window.height)
            ),
            settings,
        )
        clock = pygame.time.Clock()
        for time, flock in self.trial.frames():
            if [
                event
                for event in pygame.event.get()
                if event.type == QUIT
                or (event.type == KEYDOWN and event.key == K_ESCAPE)
            ]:
                break
            clock.tick(settings.picture.window.rate)
            view.show(flock, Stage(settings).walls())
            pygame.display.flip()
        pygame.quit()
