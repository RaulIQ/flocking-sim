from abc import ABC, abstractmethod


class Maneuver(ABC):
    """Change of the flight phase that a vehicle carries out as a whole."""

    @abstractmethod
    def fly(self) -> None:
        pass
