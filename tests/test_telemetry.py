from math import pi
from random import uniform

from pytest import approx

from agent.vector import Vector
from autopilot.attitude import Attitude
from autopilot.fix import Fix
from autopilot.spot import Spot
from autopilot.telemetry import Telemetry


def test_places_the_body_at_its_metres_from_the_origin():
    origin = Spot(uniform(-60.0, 60.0), uniform(-170.0, 170.0))
    place = Vector(uniform(-50.0, 50.0), uniform(-50.0, 50.0))
    assert Telemetry(
        Fix(origin.shifted(place), uniform(-5.0, 5.0), uniform(-5.0, 5.0)),
        Attitude(uniform(-pi, pi), uniform(-2.0, 2.0)),
    ).body(origin).position == Vector(
        approx(place.x), approx(place.y)
    ), "the body does not stand at its metres from the origin"


def test_moves_the_body_east_along_x_and_north_along_y():
    origin = Spot(uniform(-60.0, 60.0), uniform(-170.0, 170.0))
    north = uniform(-5.0, 5.0)
    east = uniform(-5.0, 5.0)
    assert Telemetry(
        Fix(origin, north, east), Attitude(uniform(-pi, pi), uniform(-2.0, 2.0))
    ).body(origin).velocity == Vector(
        east, north
    ), "the body does not move east along x and north along y"


def test_heads_the_body_along_x_with_the_nose_to_the_east():
    origin = Spot(uniform(-60.0, 60.0), uniform(-170.0, 170.0))
    assert Telemetry(
        Fix(origin, uniform(-5.0, 5.0), uniform(-5.0, 5.0)),
        Attitude(pi / 2, uniform(-2.0, 2.0)),
    ).body(origin).heading == approx(
        0.0
    ), "the body does not head along x with the nose to the east"


def test_spins_the_body_against_the_yaw_rate():
    origin = Spot(uniform(-60.0, 60.0), uniform(-170.0, 170.0))
    rate = uniform(-2.0, 2.0)
    assert Telemetry(
        Fix(origin, uniform(-5.0, 5.0), uniform(-5.0, 5.0)),
        Attitude(uniform(-pi, pi), rate),
    ).body(origin).spin == approx(
        -rate
    ), "the body does not spin against the yaw rate"
