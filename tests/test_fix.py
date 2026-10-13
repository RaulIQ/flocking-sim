from random import uniform

from pytest import approx

from agent.vector import Vector
from autopilot.fix import Fix
from autopilot.spot import Spot


def test_moves_east_along_x_and_north_along_y():
    north = uniform(-5.0, 5.0)
    east = uniform(-5.0, 5.0)
    assert Fix(
        Spot(uniform(-60.0, 60.0), uniform(-170.0, 170.0)), north, east
    ).velocity() == Vector(
        east, north
    ), "the east speed does not go along x or the north speed along y"


def test_stands_at_the_metres_from_the_origin():
    origin = Spot(uniform(-60.0, 60.0), uniform(-170.0, 170.0))
    place = Vector(uniform(-50.0, 50.0), uniform(-50.0, 50.0))
    assert Fix(
        origin.shifted(place), uniform(-5.0, 5.0), uniform(-5.0, 5.0)
    ).place(origin) == Vector(
        approx(place.x), approx(place.y)
    ), "a fix does not stand at its metres from the origin"


def test_cannot_stand_away_from_an_origin_at_its_own_spot():
    spot = Spot(uniform(-60.0, 60.0), uniform(-170.0, 170.0))
    assert Fix(spot, uniform(-5.0, 5.0), uniform(-5.0, 5.0)).place(spot) == Vector(
        0.0, 0.0
    ), "a fix stands away from an origin at its own spot"
