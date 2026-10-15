from dataclasses import dataclass
from math import atan2, tau
from typing import final

from agent.vector import Vector
from autopilot.spot import Spot
from simulator.body import Body


@final
@dataclass(frozen=True)
class Census:
    """
    Where every copter truly is in the shared frame, from what its own MAVROS tells.

    Every copter counts its local position from its own home, so the place
    comes from its latitude and longitude around the shared origin. The
    heading, the velocity and the turn of the local frame are shared by all
    copters, east and north alike, and are taken as they are.
    """

    origin: Spot
    count: int

    def complete(self, heard: dict) -> bool:
        return all(
            {'fix', 'pose', 'motion'} <= set(heard.get(number, {}))
            for number in range(1, self.count + 1)
        )

    def airborne(self, heard: dict, altitude: float) -> bool:
        return all(
            heard[number]['pose'].pose.position.z >= 0.9 * altitude
            for number in range(1, self.count + 1)
        )

    def bodies(self, heard: dict) -> tuple:
        return tuple(
            Body(
                self.origin.offset(
                    Spot(heard[number]['fix'].latitude, heard[number]['fix'].longitude)
                ),
                atan2(
                    2.0
                    * (
                        heard[number]['pose'].pose.orientation.w
                        * heard[number]['pose'].pose.orientation.z
                        + heard[number]['pose'].pose.orientation.x
                        * heard[number]['pose'].pose.orientation.y
                    ),
                    1.0
                    - 2.0
                    * (
                        heard[number]['pose'].pose.orientation.y ** 2
                        + heard[number]['pose'].pose.orientation.z ** 2
                    ),
                )
                % tau,
                Vector(
                    heard[number]['motion'].twist.linear.x,
                    heard[number]['motion'].twist.linear.y,
                ),
                heard[number]['motion'].twist.angular.z,
            )
            for number in range(1, self.count + 1)
        )
