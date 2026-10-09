from dataclasses import replace

from agent.vector import Vector
from config import defaults
from scenarios.route import Route
from scenarios.scenario import Scenario


def catalogue() -> dict:
    return {
        "hover": Scenario(
            "The leader hovers and the cloud settles around it",
            defaults(),
            Route((), 2.0, 0.3),
            20.0,
        ),
        "cruise": Scenario(
            "The leader flies 12 m at full speed away from the wall and stops",
            defaults(),
            Route((Vector(-12.0, 0.0),), 2.0, 0.3),
            25.0,
        ),
        "reverse": Scenario(
            "The leader flies 8 m away, then straight back through its own cloud",
            defaults(),
            Route((Vector(-8.0, 0.0), Vector(0.0, 0.0)), 2.0, 0.3),
            30.0,
        ),
        "gap": Scenario(
            "The leader flies straight through the gap and stops 4 m behind the wall",
            defaults(),
            Route((Vector(8.0, 0.0),), 1.0, 0.3),
            40.0,
        ),
        "gap_fast": Scenario(
            "The leader flies through the gap at full speed",
            defaults(),
            Route((Vector(8.0, 0.0),), 2.0, 0.3),
            40.0,
        ),
        "gap_ten": Scenario(
            "Ten drones follow the leader through the gap",
            replace(defaults(), swarm=replace(defaults().swarm, count=10)),
            Route((Vector(8.0, 0.0),), 1.0, 0.3),
            40.0,
        ),
        "gap_sideways": Scenario(
            "The leader passes the gap and at once slides 4 m along the wall",
            defaults(),
            Route((Vector(5.5, 0.0), Vector(5.5, 4.0)), 1.5, 0.3),
            60.0,
        ),
        "gap_back": Scenario(
            "The leader passes the gap at full speed, turns back at once and meets the cloud inside the gap",
            defaults(),
            Route((Vector(5.0, 0.0), Vector(0.0, 0.0)), 2.0, 0.3),
            25.0,
        ),
        "two_gaps": Scenario(
            "Two gaps 1.6 m apart: the leader takes the upper one, flies 7 m on, and the cloud splits",
            replace(
                defaults(),
                picture=replace(
                    defaults().picture,
                    window=replace(defaults().picture.window, scale=40.0),
                ),
                swarm=replace(defaults().swarm, count=10),
                barrier=replace(defaults().barrier, span=20.0, centres=(-0.8, 0.8)),
            ),
            Route(
                (
                    Vector(2.6, 0.0),
                    Vector(3.6, 0.8),
                    Vector(5.0, 0.8),
                    Vector(11.0, 0.0),
                ),
                1.0,
                0.3,
            ),
            25.0,
        ),
        "wall": Scenario(
            "The leader is flown at full speed into the solid wall beside the gap",
            defaults(),
            Route((Vector(8.0, 3.0),), 2.0, 0.3),
            20.0,
        ),
    }
