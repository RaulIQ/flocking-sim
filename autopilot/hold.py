from dataclasses import dataclass
from typing import final


@final
@dataclass(frozen=True)
class Hold:
    """The one altitude every copter keeps: how high, how hard it is pulled back and how fast at most."""

    altitude: float
    gain: float
    cap: float

    def climb(self, height: float) -> float:
        return max(-self.cap, min(self.cap, (self.altitude - height) * self.gain))
