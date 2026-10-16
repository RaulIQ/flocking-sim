from dataclasses import dataclass
from random import uniform

from pytest import approx

from agent.vector import Vector
from config import defaults
from scenarios.push import Push
from simulator.body import Body
from simulator.drone import Drone
from simulator.flock import Flock
from simulator.trail import Trail


@dataclass(frozen=True)
class Rail:
    """A trial in which the leader flies east at one metre a second and one follower moves as told."""

    follower: tuple
    seconds: int

    @property
    def scenario(self):
        return Rail.Scenario(defaults())

    @dataclass(frozen=True)
    class Scenario:
        settings: object

    def frames(self):
        for step in range(self.seconds * 10):
            time = step / 10
            yield time, Flock(
                (
                    Drone(Body(Vector(time, 0.0), 0.0, Vector(1.0, 0.0), 0.0), Trail((), 5), True),
                    Drone(
                        Body(
                            Vector(self.follower[0] + self.follower[2] * time, self.follower[1]),
                            0.0,
                            Vector(self.follower[2], 0.0),
                            0.0,
                        ),
                        Trail((), 5),
                        False,
                    ),
                )
            )


def test_measures_how_far_the_leader_drives_a_follower_in_its_way():
    seconds = 5
    assert Push(Rail((1.0, 0.1, 1.0), seconds)).distance() == approx(
        seconds - 0.1, abs=0.11
    ), "a follower driven ahead of the leader is not counted as pushed"


def test_cannot_count_a_follower_beside_the_way_as_pushed():
    assert Push(Rail((1.0, uniform(1.3, 3.0), 1.0), 5)).distance() == approx(
        0.0
    ), "a follower beside the way of the leader counts as pushed"


def test_cannot_count_a_follower_behind_the_leader_as_pushed():
    assert Push(Rail((-1.0, 0.0, 1.0), 5)).distance() == approx(
        0.0
    ), "a follower behind the leader counts as pushed"


def test_cannot_count_a_follower_the_leader_gets_past_as_pushed():
    assert Push(Rail((1.0, 0.0, 0.0), 5)).distance() == approx(
        0.0
    ), "a follower that stays put while the leader gets past it counts as pushed"
