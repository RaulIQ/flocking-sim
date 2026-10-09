from dataclasses import dataclass
from typing import final

from agent.vector import Vector
from config import Spring


@final
@dataclass(frozen=True)
class Bond:
    """The velocity one neighbour asks of a drone: away when close, toward when far.

    The pair of a shove and a pull around a rest distance follows the lattice
    of Olfati-Saber 2006 and the separation and cohesion of Reynolds 1987. Our
    own choices are the shove that grows without bound as the gap closes and
    the pull that stops growing past the reach, so that a straggler cannot drag
    the whole cloud back.
    """

    spring: Spring

    def velocity(self, offset: Vector) -> Vector:
        distance = offset.length()
        if distance == 0.0:
            return offset
        if distance < self.spring.rest:
            return offset.times(
                -self.spring.shove * (self.spring.rest / distance - 1.0) / distance
            )
        return offset.times(
            self.spring.pull
            * min(distance - self.spring.rest, self.spring.reach)
            / distance
        )
