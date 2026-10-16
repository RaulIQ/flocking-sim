import sys
from pathlib import Path

from autopilot.arena import Arena
from autopilot.columns import Columns
from config import copters


def main() -> None:
    print(
        Columns(
            Arena(Path(sys.argv[1]), Path(sys.argv[2]), copters().swarm.muster, 9002),
            copters().barrier,
            6.0,
        ).text()
    )


if __name__ == "__main__":
    main()
