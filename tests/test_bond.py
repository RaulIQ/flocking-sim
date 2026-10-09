from pytest import approx

from agent.bond import Bond
from agent.tuning import Spring
from agent.vector import Vector


def test_cannot_move_a_drone_at_the_rest_distance():
    assert Bond(Spring(1.2, 2.0, 0.5, 1.0)).velocity(Vector(1.2, 0.0)) == Vector(
        approx(0.0), approx(0.0)
    ), "a neighbour at the rest distance still moves a drone"


def test_pulls_toward_a_distant_neighbour():
    assert Bond(Spring(1.2, 2.0, 0.5, 1.0)).velocity(Vector(1.7, 0.0)) == Vector(
        approx(0.25), approx(0.0)
    ), "a distant neighbour does not pull a drone"


def test_cannot_pull_harder_beyond_its_reach():
    assert Bond(Spring(1.2, 2.0, 0.5, 1.0)).velocity(Vector(9.2, 0.0)) == Vector(
        approx(0.5), approx(0.0)
    ), "a straggler pulls without saturation"


def test_shoves_away_from_a_close_neighbour():
    assert Bond(Spring(1.2, 2.0, 0.5, 1.0)).velocity(Vector(0.6, 0.0)) == Vector(
        approx(-2.0), approx(0.0)
    ), "a close neighbour does not shove a drone away"


def test_shoves_harder_the_closer_a_neighbour_gets():
    assert Bond(Spring(1.2, 2.0, 0.5, 1.0)).velocity(Vector(0.3, 0.0)) == Vector(
        approx(-6.0), approx(0.0)
    ), "a very close neighbour does not shove harder"


def test_pulls_along_the_line_to_a_neighbour():
    assert Bond(Spring(1.2, 2.0, 0.5, 1.0)).velocity(Vector(-1.02, -1.36)) == Vector(
        approx(-0.15), approx(-0.2)
    ), "a pull does not follow the line to the neighbour"


def test_cannot_shove_away_from_a_neighbour_in_the_same_place():
    assert Bond(Spring(1.2, 2.0, 0.5, 1.0)).velocity(Vector(0.0, 0.0)) == Vector(
        approx(0.0), approx(0.0)
    ), "a neighbour in the same place shoves in a made-up direction"
