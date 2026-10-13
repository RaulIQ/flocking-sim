from logging import INFO, basicConfig
from pathlib import Path

from config import copters, sortie
from simulator.loop import Flight

if __name__ == "__main__":
    basicConfig(level=INFO, format="%(message)s")
    with sortie(copters()).flown(Path(__file__).parent / "logs") as air:
        Flight(copters(), air).run()
