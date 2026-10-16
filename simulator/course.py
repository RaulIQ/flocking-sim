from abc import ABC, abstractmethod

from agent.vector import Vector


class Course(ABC):
    """What stands in the way of the cloud: the obstacles a drone feels, and the line it is to pass."""

    @abstractmethod
    def walls(self) -> tuple:
        pass

    @abstractmethod
    def passed(self, place: Vector) -> bool:
        pass
