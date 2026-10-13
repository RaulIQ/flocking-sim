from dataclasses import dataclass
from time import monotonic, sleep
from typing import final


@final
@dataclass(frozen=True)
class Pulse:
    """The steady beat of real time that a flight ticks on, so many beats a second."""

    rate: float

    def wait(self) -> None:
        sleep(1.0 / self.rate - monotonic() % (1.0 / self.rate))
