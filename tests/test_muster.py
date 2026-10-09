from itertools import combinations

from pytest import approx

from simulator.muster import Muster
from simulator.vector import Vector


def test_places_as_many_drones_as_asked():
    assert len(Muster(7, 1.3).places()) == 7, "a muster does not place every drone"


def test_puts_the_first_drone_in_the_middle():
    assert Muster(7, 1.3).places()[0] == Vector(
        approx(0.0), approx(0.0)
    ), "the first drone does not start in the middle"


def test_cannot_start_two_drones_closer_than_the_spacing():
    assert min(
        one.minus(other).length() for one, other in combinations(Muster(9, 1.3).places(), 2)
    ) == approx(1.3), "two drones start closer than the spacing"


def test_cannot_place_anything_for_an_empty_swarm():
    assert Muster(0, 1.3).places() == (), "an empty muster still places a drone"
