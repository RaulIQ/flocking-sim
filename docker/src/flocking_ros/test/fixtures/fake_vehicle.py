from dataclasses import dataclass
from typing import final

from flocking_ros.flight.refusal import Refusal
from flocking_ros.flight.vehicle import Vehicle


@final
@dataclass(frozen=True)
class FakeVehicle(Vehicle):
    """Vehicle that records obeyed steps and refuses the chosen ones."""

    refused: frozenset[str]
    steps: list[str]

    def switch(self, mode: str) -> None:
        self.obey('switch', f'switch {mode}')

    def arm(self) -> None:
        self.obey('arm', 'arm')

    def ascend(self, altitude: float) -> None:
        self.obey('ascend', f'ascend {altitude}')

    def obey(self, step: str, record: str) -> None:
        if step in self.refused:
            raise Refusal(f'Fake vehicle refused to {step}')
        self.steps.append(record)
