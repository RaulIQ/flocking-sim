from collections import deque
from dataclasses import dataclass, replace
from math import exp
from pathlib import Path
from typing import final

from agent.tuning import Cloud, Limits, Spring
from autopilot.fleet import Fleet
from autopilot.hangar import Hangar
from autopilot.hold import Hold
from autopilot.pulse import Pulse
from autopilot.sortie import Sortie
from autopilot.spot import Spot
from simulator.course import Course
from simulator.gate import Gate
from simulator.kinematics import Kinematics
from simulator.lag import Lag
from simulator.muster import Muster
from simulator.posts import Posts


@final
@dataclass(frozen=True)
class Window:
    """The canvas in pixels, the pixels that cover one metre and the frames per second."""

    width: int
    height: int
    scale: float
    rate: int


@final
@dataclass(frozen=True)
class Shape:
    """How one drone looks, in metres, with a trail counted in frames."""

    radius: float
    nose: float
    trail: int


@final
@dataclass(frozen=True)
class Picture:
    """What the pilot looks at: the canvas and the look of one drone on it."""

    window: Window
    shape: Shape


@final
@dataclass(frozen=True)
class Bubbles:
    """How wide both bubbles around one drone reach, in metres."""

    hard: float
    soft: float


@final
@dataclass(frozen=True)
class Swarm:
    """Where the drones start, their bubbles, their ties and how late they are taken to answer, in seconds."""

    muster: Muster
    bubbles: Bubbles
    cloud: Cloud
    reaction: float


@final
@dataclass(frozen=True)
class Settings:
    """Every tunable number of the simulation."""

    limits: Limits
    picture: Picture
    swarm: Swarm
    barrier: Course


def defaults() -> Settings:
    return Settings(
        Limits(2.0, 4.0, 1.8, 8.0),
        Picture(Window(1000, 700, 60.0, 60), Shape(0.1, 0.35, 600)),
        Swarm(
            Muster(8, 1.2),
            Bubbles(0.25, 0.6),
            Cloud(
                Spring(1.2, 0.5, 0.15, 1.0),
                Spring(1.2, 1.0, 0.4, 1.5),
                Spring(0.6, 1.0, 0.0, 0.0),
                6,
            ),
            0.5,
        ),
        Gate(4.0, 14.0, 1.2, (0.0,)),
    )


def pillars(settings: Settings) -> Settings:
    return replace(
        settings,
        barrier=Posts(4.0, 3.0 * settings.swarm.bubbles.soft, settings.swarm.bubbles.soft),
    )


def copters() -> Settings:
    return pillars(
        replace(
            defaults(),
            picture=Picture(Window(1000, 700, 60.0, 20), Shape(0.1, 0.35, 200)),
            swarm=replace(
                defaults().swarm, muster=replace(defaults().swarm.muster, count=4)
            ),
        )
    )


def frames() -> dict:
    return {
        "freestyle": copters(),
        "iris": replace(
            copters(),
            swarm=replace(
                copters().swarm,
                bubbles=Bubbles(0.4, 0.6),
                cloud=replace(
                    copters().swarm.cloud,
                    leader=replace(copters().swarm.cloud.leader, rest=2.0),
                ),
            ),
        ),
    }


def kinematics(settings: Settings) -> Lag:
    return Lag(
        Kinematics(settings.limits, 1.0 / settings.picture.window.rate),
        deque(),
        round(0.15 * settings.picture.window.rate),
        1.0 - exp(-1.0 / (0.33 * settings.picture.window.rate)),
    )


def sortie(settings: Settings) -> Sortie:
    return Sortie(
        Hangar(
            Fleet(
                5760,
                Spot(-35.3632607, 149.1652351),
                Path.home() / "code" / "ardupilot",
                Path(__file__).parent / "autopilot" / "freestyle",
            ),
            settings.swarm.muster,
        ),
        Hold(3.0, 1.0, 1.0),
        Pulse(settings.picture.window.rate),
    )
