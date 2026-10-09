from pytest import approx

from agent.vector import Vector
from config import Barrier
from simulator.gate import Gate
from simulator.wall import Wall


def test_builds_a_wall_on_each_side_of_the_gap():
    assert len(Gate(Barrier(4.5, 14.0, 1.3, (0.0,))).walls()) == 2, (
        "a gate does not build a wall on each side of its gap"
    )


def test_builds_the_lower_wall_up_to_the_gap():
    assert Gate(Barrier(4.5, 14.0, 1.3, (0.0,))).walls()[0] == Wall(
        Vector(approx(4.5), approx(-7.0)), Vector(approx(4.5), approx(-0.65))
    ), "the lower wall does not reach up to the gap"


def test_builds_the_upper_wall_from_the_gap():
    assert Gate(Barrier(4.5, 14.0, 1.3, (0.0,))).walls()[1] == Wall(
        Vector(approx(4.5), approx(0.65)), Vector(approx(4.5), approx(7.0))
    ), "the upper wall does not start at the gap"


def test_leaves_a_gap_as_wide_as_asked():
    assert Gate(Barrier(4.5, 14.0, 1.3, (0.0,))).walls()[1].nearest(Vector(4.5, 0.0)).minus(
        Gate(Barrier(4.5, 14.0, 1.3, (0.0,))).walls()[0].nearest(Vector(4.5, 0.0))
    ).length() == approx(1.3), "a gate does not leave a gap as wide as asked"


def test_builds_three_walls_around_two_gaps():
    assert len(Gate(Barrier(4.5, 14.0, 1.3, (2.0, -2.5))).walls()) == 3, (
        "a gate does not build three walls around two gaps"
    )


def test_builds_the_middle_wall_between_two_gaps():
    assert Gate(Barrier(4.5, 14.0, 1.3, (2.0, -2.5))).walls()[1] == Wall(
        Vector(approx(4.5), approx(-1.85)), Vector(approx(4.5), approx(1.35))
    ), "the middle wall does not stand between the two gaps"


def test_builds_one_solid_wall_without_gaps():
    assert Gate(Barrier(4.5, 14.0, 1.3, ())).walls() == (
        Wall(Vector(approx(4.5), approx(-7.0)), Vector(approx(4.5), approx(7.0))),
    ), "a gate without gaps does not build one solid wall"
