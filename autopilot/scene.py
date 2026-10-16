from abc import ABC, abstractmethod


class Scene(ABC):
    """A world of Gazebo, given as the text of its SDF file."""

    @abstractmethod
    def text(self) -> str:
        pass
