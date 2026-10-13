from itertools import count
from pathlib import Path
from time import sleep

from agent.command import Command
from agent.vector import Vector
from autopilot.hangar import Hangar
from autopilot.squad import Squad
from config import defaults, fleet, hold

if __name__ == "__main__":
    hangar = Hangar(fleet(), defaults().swarm.spacing)
    with hangar.opened(Path(__file__).parent / "logs"):
        squad = Squad(tuple(copter.link() for copter in hangar.copters()), fleet().origin)
        try:
            squad.tune(20.0, 90.0)
            squad.lift(hold().altitude, 30.0)
            for tick in count():
                squad.fly((Command(Vector(0.5, 0.0), 0.3),) * fleet().count, hold())
                if tick % 20 == 0:
                    print(
                        "   ".join(
                            f"{body.position.x:+8.2f} {body.position.y:+8.2f}"
                            for body in squad.bodies()
                        )
                    )
                sleep(0.05)
        except KeyboardInterrupt:
            print("Every copter is stopped")
