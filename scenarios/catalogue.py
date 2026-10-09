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
        "two_gaps": Scenario(
            "The wall has two gaps 4 m apart and the leader takes the upper one",
            replace(defaults(), barrier=replace(defaults().barrier, centres=(-2.0, 2.0))),
            Route((Vector(3.0, 2.0), Vector(8.0, 2.0)), 1.0, 0.3),
            40.0,
        ),
        "wall": Scenario(
            "The leader is flown at full speed into the solid wall beside the gap",
            defaults(),
            Route((Vector(8.0, 3.0),), 2.0, 0.3),
            20.0,
        ),
    }
