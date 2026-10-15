from autopilot.sitl import Sitl
from config import copters, sortie


def main() -> None:
    words = Sitl(
        sortie(copters()).hangar.fleet, 0, sortie(copters()).hangar.fleet.origin
    ).words()
    print(words[words.index('--home') + 1])
