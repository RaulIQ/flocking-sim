from math import cos, pi, sin
from random import uniform

from pytest import approx

from agent.neighbour import Neighbour
from agent.tuning import Limits, Rope, Spring, Wedge
from agent.vector import Vector
from agent.wings import Wings


def rope():
    return Rope(Spring(1.2, 1.0, 0.4, 1.5), Wedge(pi / 4, 4.0, 0.6, 0.6), 1.5, 2.0)


def test_finds_a_drone_on_the_left_wing_of_a_flying_leader():
    along = uniform(1.3, 5.0)
    assert Wings(rope(), Limits(2.0, 4.0, 1.8, 8.0), 0.0).place(
        Neighbour(Vector(along * cos(pi / 4), -along * sin(pi / 4)), Vector(1.5, 0.0), True)
    ) == Vector(approx(0.0), approx(0.0)), "a drone on the left wing is not on the wedge"


def test_finds_a_drone_on_the_right_wing_of_a_flying_leader():
    along = uniform(1.3, 5.0)
    assert Wings(rope(), Limits(2.0, 4.0, 1.8, 8.0), 0.0).place(
        Neighbour(Vector(along * cos(pi / 4), along * sin(pi / 4)), Vector(1.5, 0.0), True)
    ) == Vector(approx(0.0), approx(0.0)), "a drone on the right wing is not on the wedge"


def test_starts_the_wings_a_spring_rest_behind_the_leader():
    assert Wings(rope(), Limits(2.0, 4.0, 1.8, 8.0), 0.0).place(
        Neighbour(Vector(0.5 * cos(pi / 4), -0.5 * sin(pi / 4)), Vector(1.5, 0.0), True)
    ) == Vector(approx(-0.7 * cos(pi / 4)), approx(0.7 * sin(pi / 4))), "the wings start closer to the leader than its spring rests"


def test_ends_the_wings_at_their_length():
    assert Wings(rope(), Limits(2.0, 4.0, 1.8, 8.0), 0.0).place(
        Neighbour(Vector(7.0 * cos(pi / 4), -7.0 * sin(pi / 4)), Vector(1.5, 0.0), True)
    ) == Vector(approx(1.8 * cos(pi / 4)), approx(-1.8 * sin(pi / 4))), "the wings run past their length"


def test_tucks_the_left_wing_behind_a_leader_turning_left_at_full_spin():
    assert Wings(rope(), Limits(2.0, 4.0, 1.8, 8.0), 1.8).place(
        Neighbour(Vector(uniform(1.3, 5.0), 0.0), Vector(1.5, 0.0), True)
    ) == Vector(approx(0.0), approx(0.0)), "the left wing does not tuck behind a leader turning left"


def test_tucks_the_right_wing_behind_a_leader_turning_right_at_full_spin():
    assert Wings(rope(), Limits(2.0, 4.0, 1.8, 8.0), -1.8).place(
        Neighbour(Vector(uniform(1.3, 5.0), 0.0), Vector(1.5, 0.0), True)
    ) == Vector(approx(0.0), approx(0.0)), "the right wing does not tuck behind a leader turning right"


def test_tucks_the_inner_wing_halfway_at_half_spin():
    along = uniform(1.3, 5.0)
    assert Wings(rope(), Limits(2.0, 4.0, 1.8, 8.0), 0.9).place(
        Neighbour(Vector(along * cos(pi / 8), -along * sin(pi / 8)), Vector(1.5, 0.0), True)
    ) == Vector(approx(0.0), approx(0.0)), "the inner wing does not tuck halfway at half spin"


def test_keeps_the_outer_wing_open_in_a_turn():
    along = uniform(1.3, 5.0)
    assert Wings(rope(), Limits(2.0, 4.0, 1.8, 8.0), 1.8).place(
        Neighbour(Vector(along * cos(pi / 4), along * sin(pi / 4)), Vector(1.5, 0.0), True)
    ) == Vector(approx(0.0), approx(0.0)), "the outer wing folds in a turn"
