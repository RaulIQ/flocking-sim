from dataclasses import dataclass
from typing import final

from agent.senses import Senses
from flocking_msgs.msg import Bearing, Range, Role
from flocking_msgs.msg import Senses as Letter
from geometry_msgs.msg import Point, Twist, Vector3


@final
@dataclass(frozen=True)
class Post:
    """
    What the ground sends one drone in one tick.

    It tells the drone whether it leads, what its own sensors would measure
    and what the pilot asks.
    """

    senses: Senses
    leader: bool

    def message(self) -> Letter:
        return Letter(
            leader=self.leader,
            ranges=[
                Range(tag=echo.tag, distance=echo.distance)
                for echo in self.senses.signals.ranges
            ],
            bearings=[
                Bearing(tag=sight.tag, angle=sight.angle)
                for sight in self.senses.signals.bearings
            ],
            roles=[
                Role(tag=word.tag, leader=word.leader) for word in self.senses.signals.roles
            ],
            obstacles=[Point(x=offset.x, y=offset.y) for offset in self.senses.obstacles],
            request=Twist(
                linear=Vector3(
                    x=self.senses.request.velocity.x, y=self.senses.request.velocity.y
                ),
                angular=Vector3(z=self.senses.request.spin),
            ),
        )
