from pytest import approx

from agent.vector import Vector
from simulator.wall import Wall


def test_finds_the_foot_of_a_place_beside_it():
    assert Wall(Vector(4.0, -3.0), Vector(4.0, 2.0)).nearest(Vector(1.5, 0.7)) == Vector(
        approx(4.0), approx(0.7)
    ), "a wall does not find the foot of a place beside it"


def test_finds_its_end_for_a_place_beyond_it():
    assert Wall(Vector(4.0, -3.0), Vector(4.0, 2.0)).nearest(Vector(1.5, 5.1)) == Vector(
        approx(4.0), approx(2.0)
    ), "a wall does not find its end for a place beyond it"


def test_finds_its_start_for_a_place_before_it():
    assert Wall(Vector(4.0, -3.0), Vector(4.0, 2.0)).nearest(Vector(6.2, -7.5)) == Vector(
        approx(4.0), approx(-3.0)
    ), "a wall does not find its start for a place before it"


def test_finds_the_foot_on_a_slanted_wall():
    assert Wall(Vector(0.0, 0.0), Vector(3.0, 3.0)).nearest(Vector(2.0, 0.0)) == Vector(
        approx(1.0), approx(1.0)
    ), "a slanted wall does not find the foot of a place"


def test_finds_a_place_that_lies_on_it():
    assert Wall(Vector(4.0, -3.0), Vector(4.0, 2.0)).nearest(Vector(4.0, 1.3)) == Vector(
        approx(4.0), approx(1.3)
    ), "a wall does not find a place that lies on it"
