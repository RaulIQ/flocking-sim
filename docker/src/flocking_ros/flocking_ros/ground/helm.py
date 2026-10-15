from abc import ABC, abstractmethod

from agent.command import Command
from scenarios.tally import Tally
from simulator.body import Body
from simulator.flock import Flock


class Helm(ABC):
    """Whoever flies the leader: what it asks of the leader and what it reports of the run."""

    @abstractmethod
    def rest(self, body: Body) -> 'Helm':
        pass

    @abstractmethod
    def command(self, body: Body) -> Command:
        pass

    @abstractmethod
    def told(self, frame: int, tally: Tally, flock: Flock) -> tuple:
        pass
