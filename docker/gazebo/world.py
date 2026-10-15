import sys
from pathlib import Path

from autopilot.arena import Arena
from config import copters


def main() -> None:
    print(Arena(Path(sys.argv[1]), Path(sys.argv[2]), copters().swarm.muster, 9002).text())


if __name__ == "__main__":
    main()
