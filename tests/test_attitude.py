from math import cos, pi, sin, tau
from random import uniform

from pytest import approx

from agent.vector import Vector
from autopilot.attitude import Attitude


def test_heads_a_quarter_turn_with_the_nose_to_the_north():
    assert Attitude(0.0, uniform(-2.0, 2.0)).heading() == approx(
        pi / 2
    ), "a nose to the north does not head a quarter turn from x"


def test_heads_along_x_with_the_nose_to_the_east():
    assert Attitude(pi / 2, uniform(-2.0, 2.0)).heading() == approx(
        0.0
    ), "a nose to the east does not head along x"


def test_points_the_nose_where_the_autopilot_points_it():
    yaw = uniform(-pi, pi)
    assert Vector(1.0, 0.0).turned(Attitude(yaw, uniform(-2.0, 2.0)).heading()) == Vector(
        approx(sin(yaw)), approx(cos(yaw))
    ), "the heading does not point the nose where the autopilot points it"


def test_cannot_head_beyond_one_full_turn():
    assert (
        0.0 <= Attitude(uniform(-pi, pi), uniform(-2.0, 2.0)).heading() < tau
    ), "the heading leaves the range of one full turn"


def test_spins_against_the_yaw_rate():
    rate = uniform(-2.0, 2.0)
    assert Attitude(uniform(-pi, pi), rate).spin() == approx(
        -rate
    ), "the spin does not oppose the yaw rate"
