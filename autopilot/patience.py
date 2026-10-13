from dataclasses import dataclass
from time import monotonic, sleep
from typing import final


@final
@dataclass(frozen=True)
class Patience:
    """A bounded wait: the same question asked again and again until the answer is yes or the seconds run out."""

    seconds: float
    pause: float

    def until(self, check, story: str) -> None:
        end = monotonic() + self.seconds
        while not check():
            if monotonic() > end:
                raise TimeoutError(f"{story} after {self.seconds} seconds")
            sleep(self.pause)
