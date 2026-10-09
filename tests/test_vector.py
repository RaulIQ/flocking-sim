from math import pi

from pytest import approx

from agent.vector import Vector


def test_adds_two_vectors():
    assert Vector(1.5, -2.25).plus(Vector(0.75, 3.5)) == Vector(
        approx(2.25), approx(1.25)
    ), "two vectors do not add up"


def test_subtracts_two_vectors():
    assert Vector(1.5, -2.25).minus(Vector(0.75, 3.5)) == Vector(
        approx(0.75), approx(-5.75)
    ), "two vectors do not subtract"


def test_scales_a_vector():
    assert Vector(1.5, -2.25).times(1.5) == Vector(
        approx(2.25), approx(-3.375)
    ), "a vector does not scale"


def test_turns_a_vector_a_quarter_circle():
    assert Vector(2.5, 0.0).turned(pi / 2) == Vector(
        approx(0.0, abs=1e-9), approx(2.5)
    ), "a vector does not turn counterclockwise"


def test_measures_the_length_of_a_vector():
    assert Vector(-3.0, 4.0).length() == approx(5.0), "a vector reports a wrong length"


def test_caps_a_long_vector_to_the_limit():
    assert Vector(-3.0, 4.0).capped(2.5).length() == approx(
        2.5
    ), "a long vector does not shrink to the limit"


def test_keeps_the_direction_of_a_capped_vector():
    assert Vector(-3.0, 4.0).capped(2.5) == Vector(
        approx(-1.5), approx(2.0)
    ), "a capped vector does not keep its direction"


def test_cannot_shrink_a_vector_already_inside_the_limit():
    assert Vector(0.3, -0.4).capped(2.5) == Vector(
        approx(0.3), approx(-0.4)
    ), "a short vector does not survive capping"


def test_caps_a_motionless_vector_without_dividing_by_zero():
    assert Vector(0.0, 0.0).capped(2.5) == Vector(
        approx(0.0), approx(0.0)
    ), "a zero vector does not survive capping"


def test_multiplies_two_vectors_into_a_number():
    assert Vector(1.5, -2.0).dot(Vector(0.5, 3.0)) == approx(
        -5.25
    ), "two vectors do not multiply into the right number"
