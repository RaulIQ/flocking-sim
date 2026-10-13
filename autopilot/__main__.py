from pathlib import Path
from signal import pause

from autopilot.hangar import Hangar
from config import defaults, fleet

if __name__ == "__main__":
    hangar = Hangar(fleet(), defaults().swarm.spacing)
    with hangar.opened(Path(__file__).parent / "logs"):
        for copter in hangar.copters():
            print(f"Copter {copter.number} listens on port {copter.port()}")
        try:
            pause()
        except KeyboardInterrupt:
            print("Every copter is stopped")
