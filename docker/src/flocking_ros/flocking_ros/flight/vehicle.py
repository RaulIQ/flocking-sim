from abc import ABC, abstractmethod


class Vehicle(ABC):
    """Aircraft that either obeys a flight step or refuses it."""

    @abstractmethod
    def switch(self, mode: str) -> None:
        pass

    @abstractmethod
    def arm(self) -> None:
        pass

    @abstractmethod
    def ascend(self, altitude: float) -> None:
        pass
