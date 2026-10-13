from dataclasses import dataclass
from pathlib import Path
from typing import final

from autopilot.spot import Spot


@final
@dataclass(frozen=True)
class Fleet:
    """What every simulated copter shares: the first port, the spot under the first copter, where ArduPilot is built and the folder with the frame and the parameters of the copter."""

    port: int
    origin: Spot
    source: Path
    tuning: Path
