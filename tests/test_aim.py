from math import cos, pi, sin, tau

from pytest import approx

from config import Limits
from simulator.aim import Aim
from simulator.body import Body
from simulator.vector import Vector


def test_cannot_turn_toward_a_place_it_already_faces():
    assert Aim(Limits(2.0, 4.0, 1.8, 0.5), 0.1).spin(
        Body(Vector(0.0, 0.0), 0.0, Vector(0.0, 0.0), 0.0), Vector(3.0, 0.0), 1.0 / 60
    ) == approx(0.0), "a drone turns although it already faces the place"


def test_turns_left_toward_a_place_on_its_left():
    assert Aim(Limits(2.0, 4.0, 1.8, 0.5), 0.1).spin(
        Body(Vector(0.0, 0.0), 0.0, Vector(0.0, 0.0), 0.0),
        Vector(3.0 * cos(0.25), 3.0 * sin(0.25)),
        1.0 / 60,
    ) == approx(0.5), "a drone does not turn left toward a place on its left"


def test_turns_right_toward_a_place_on_its_right():
    assert Aim(Limits(2.0, 4.0, 1.8, 0.5), 0.1).spin(
        Body(Vector(0.0, 0.0), 0.0, Vector(0.0, 0.0), 0.0),
        Vector(3.0 * cos(-0.25), 3.0 * sin(-0.25)),
        1.0 / 60,
    ) == approx(-0.5), "a drone does not turn right toward a place on its right"


def test_cannot_care_how_far_the_place_lies():
    assert Aim(Limits(2.0, 4.0, 1.8, 0.5), 0.1).spin(
        Body(Vector(0.0, 0.0), 0.0, Vector(0.0, 0.0), 0.0),
        Vector(30.0 * cos(0.25), 30.0 * sin(0.25)),
        1.0 / 60,
    ) == approx(0.5), "a distant place does not turn a drone like a near one"


def test_cannot_turn_faster_than_the_spin_limit():
    assert Aim(Limits(2.0, 4.0, 1.8, 100.0), 0.1).spin(
        Body(Vector(0.0, 0.0), 0.0, Vector(0.0, 0.0), 0.0), Vector(0.0, 3.0), 1.0 / 60
    ) == approx(1.8), "a drone ignores its spin limit while aiming"


def test_eases_the_turn_close_to_the_place():
    assert Aim(Limits(2.0, 4.0, 1.8, 0.5), 0.1).spin(
        Body(Vector(0.0, 0.0), 0.0, Vector(0.0, 0.0), 0.0),
        Vector(3.0 * cos(0.02), 3.0 * sin(0.02)),
        1.0 / 60,
    ) == approx(0.1414, abs=1e-4), "a drone does not ease its turn near the place"


def test_cannot_overshoot_the_place_within_one_frame():
    assert Aim(Limits(2.0, 4.0, 1.8, 100.0), 0.1).spin(
        Body(Vector(0.0, 0.0), 0.0, Vector(0.0, 0.0), 0.0),
        Vector(3.0 * cos(0.25), 3.0 * sin(0.25)),
        0.5,
    ) == approx(0.5), "a drone asks to turn past the place inside one frame"


def test_takes_the_short_way_around():
    assert Aim(Limits(2.0, 4.0, 1.8, 0.5), 0.1).spin(
        Body(Vector(0.0, 0.0), 0.25, Vector(0.0, 0.0), 0.0),
        Vector(3.0 * cos(tau - 0.25), 3.0 * sin(tau - 0.25)),
        1.0 / 60,
    ) == approx(-0.7071, abs=1e-4), "a drone takes the long way around"


def test_aims_from_wherever_it_hovers():
    assert Aim(Limits(2.0, 4.0, 1.8, 100.0), 0.1).spin(
        Body(Vector(1.5, -2.0), 0.0, Vector(0.0, 0.0), 0.0), Vector(1.5, 0.0), 1.0 / 60
    ) == approx(1.8), "a drone away from the origin does not aim correctly"


def test_cannot_turn_toward_a_place_under_its_own_body():
    assert Aim(Limits(2.0, 4.0, 1.8, 0.5), 0.1).spin(
        Body(Vector(1.5, -2.0), pi / 3, Vector(0.0, 0.0), 0.0),
        Vector(1.53, -2.04),
        1.0 / 60,
    ) == approx(0.0), "a drone chases a place under its own body"
