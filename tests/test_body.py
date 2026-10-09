from math import pi

from pytest import approx

from agent.command import Command
from agent.tuning import Limits
from simulator.body import Body
from agent.vector import Vector


def test_accelerates_toward_the_request():
    assert Body(Vector(0.0, 0.0), 0.0, Vector(0.0, 0.0), 0.0).moved(
        Command(Vector(2.0, 0.0), 0.0),
        Limits(2.0, 4.0, 1.5, 6.0),
        0.25,
    ).velocity == Vector(approx(1.0), approx(0.0)), "a resting drone does not speed up"


def test_cannot_gain_speed_faster_than_the_limit():
    assert Body(Vector(0.0, 0.0), 0.0, Vector(0.0, 0.0), 0.0).moved(
        Command(Vector(5.0, 0.0), 0.0),
        Limits(5.0, 2.0, 1.5, 6.0),
        0.5,
    ).velocity.length() == approx(1.0), "a drone ignores its acceleration limit"


def test_cannot_fly_faster_than_the_top_speed():
    assert Body(Vector(0.0, 0.0), 0.0, Vector(0.0, 0.0), 0.0).moved(
        Command(Vector(9.0, 0.0), 0.0),
        Limits(1.5, 100.0, 1.5, 6.0),
        0.5,
    ).velocity.length() == approx(1.5), "a drone ignores its top speed"


def test_slows_down_when_the_request_stops():
    assert Body(Vector(0.0, 0.0), 0.0, Vector(2.0, 0.0), 0.0).moved(
        Command(Vector(0.0, 0.0), 0.0),
        Limits(2.0, 4.0, 1.5, 6.0),
        0.25,
    ).velocity == Vector(approx(1.0), approx(0.0)), "a drone does not coast to a stop"


def test_flies_sideways_in_its_own_frame():
    assert Body(Vector(0.0, 0.0), pi / 2, Vector(0.0, 0.0), 0.0).moved(
        Command(Vector(2.0, 0.0), 0.0),
        Limits(2.0, 100.0, 1.5, 6.0),
        0.5,
    ).position == Vector(
        approx(0.0, abs=1e-9), approx(1.0)
    ), "a turned drone does not fly along its own nose"


def test_turns_with_the_requested_spin():
    assert Body(Vector(0.0, 0.0), 0.0, Vector(0.0, 0.0), 0.0).moved(
        Command(Vector(0.0, 0.0), 1.0),
        Limits(2.0, 4.0, 1.5, 100.0),
        0.5,
    ).heading == approx(0.5), "a drone does not turn as asked"


def test_cannot_turn_faster_than_the_spin_limit():
    assert Body(Vector(0.0, 0.0), 0.0, Vector(0.0, 0.0), 0.0).moved(
        Command(Vector(0.0, 0.0), 9.0),
        Limits(2.0, 4.0, 1.5, 100.0),
        0.5,
    ).spin == approx(1.5), "a drone ignores its spin limit"


def test_cannot_change_spin_faster_than_the_twist_limit():
    assert Body(Vector(0.0, 0.0), 0.0, Vector(0.0, 0.0), 0.0).moved(
        Command(Vector(0.0, 0.0), 1.5),
        Limits(2.0, 4.0, 1.5, 2.0),
        0.5,
    ).spin == approx(1.0), "a drone ignores its twist limit"


def test_keeps_still_without_a_request():
    assert Body(Vector(0.4, -0.7), 0.3, Vector(0.0, 0.0), 0.0).moved(
        Command(Vector(0.0, 0.0), 0.0),
        Limits(2.0, 4.0, 1.5, 6.0),
        0.25,
    ).position == Vector(
        approx(0.4), approx(-0.7)
    ), "an idle drone does not hold its place"


def test_keeps_the_heading_inside_one_turn():
    assert Body(Vector(0.0, 0.0), 2 * pi - 0.1, Vector(0.0, 0.0), 0.0).moved(
        Command(Vector(0.0, 0.0), 1.0),
        Limits(2.0, 4.0, 1.5, 100.0),
        0.5,
    ).heading == approx(0.4), "a heading does not wrap around a full turn"
