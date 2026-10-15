from dataclasses import dataclass
from typing import Any, final

from flocking_ros.flight.link import Link
from flocking_ros.flight.refusal import Refusal
from rclpy.client import Client


@final
@dataclass(frozen=True)
class ClientLink(Link):
    """
    Link through a ROS service client that never waits beyond its timeout.

    The client of ROS 2 Jazzy answers a call that timed out with nothing
    rather than with an error, so silence is told apart by the empty answer.
    """

    client: Client
    timeout: float

    def ask(self, request: Any) -> Any:
        if not self.client.wait_for_service(self.timeout):
            raise Refusal(f'Service {self.client.srv_name} is absent')
        response = self.client.call(request, self.timeout)
        if response is None:
            raise Refusal(
                f'Service {self.client.srv_name} kept silent for {self.timeout} seconds'
            )
        return response
