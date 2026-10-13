from math import cos, radians
from random import uniform

from pytest import approx

from agent.vector import Vector
from autopilot.spot import Spot


def test_measures_a_spot_to_the_north_along_y():
    spot = Spot(uniform(-60.0, 60.0), uniform(-170.0, 170.0))
    assert spot.offset(Spot(spot.latitude + 0.001, spot.longitude)) == Vector(
        approx(0.0), approx(111.3, abs=0.1)
    ), "a spot to the north does not lie along y"


def test_measures_a_spot_to_the_east_along_x():
    spot = Spot(uniform(-60.0, 60.0), uniform(-170.0, 170.0))
    assert spot.offset(Spot(spot.latitude, spot.longitude + 0.001)) == Vector(
        approx(111.3 * cos(radians(spot.latitude)), abs=0.1), approx(0.0)
    ), "a spot to the east does not lie along x"


def test_measures_a_spot_to_the_south_west_as_negative():
    spot = Spot(uniform(-60.0, 60.0), uniform(-170.0, 170.0))
    assert (
        max(
            spot.offset(Spot(spot.latitude - 0.0007, spot.longitude - 0.0003)).x,
            spot.offset(Spot(spot.latitude - 0.0007, spot.longitude - 0.0003)).y,
        )
        < 0.0
    ), "a spot to the south west does not lie at negative metres"


def test_cannot_measure_any_metres_to_itself():
    spot = Spot(uniform(-60.0, 60.0), uniform(-170.0, 170.0))
    assert spot.offset(spot) == Vector(0.0, 0.0), "a spot lies some metres from itself"


def test_returns_the_metres_it_was_shifted_by():
    spot = Spot(uniform(-60.0, 60.0), uniform(-170.0, 170.0))
    offset = Vector(uniform(-50.0, 50.0), uniform(-50.0, 50.0))
    assert spot.offset(spot.shifted(offset)) == Vector(
        approx(offset.x), approx(offset.y)
    ), "a shifted spot does not lie at the metres it was shifted by"


def test_shifts_north_by_raising_the_latitude():
    spot = Spot(uniform(-60.0, 60.0), uniform(-170.0, 170.0))
    assert spot.shifted(Vector(0.0, 111.3)) == Spot(
        approx(spot.latitude + 0.001, abs=1e-6), approx(spot.longitude)
    ), "a shift to the north does not raise the latitude alone"
