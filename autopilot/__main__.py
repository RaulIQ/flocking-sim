from pathlib import Path
from time import sleep

from autopilot.hangar import Hangar
from autopilot.squad import Squad
from config import defaults, fleet

if __name__ == "__main__":
    hangar = Hangar(fleet(), defaults().swarm.spacing)
    with hangar.opened(Path(__file__).parent / "logs"):
        squad = Squad(tuple(copter.link() for copter in hangar.copters()), fleet().origin)
        try:
            squad.tune(20.0, 30.0)
            while True:
                print(
                    "   ".join(
                        f"{body.position.x:+8.2f} {body.position.y:+8.2f}"
                        for body in squad.bodies()
                    )
                )
                sleep(1.0)
        except KeyboardInterrupt:
            print("Every copter is stopped")
