from math import pi

from pytest import approx

from agent.vector import Vector
from scenarios.route import Route
from simulator.body import Body


def test_hovers_with_nowhere_to_go():
    assert Route((), 1.5, 0.3).command(
        Body(Vector(0.4, -0.7), 0.3, Vector(0.0, 0.0), 0.0)
    ).velocity == Vector(
        approx(0.0), approx(0.0)
    ), "a pilot with nowhere to go does not hover"


def test_flies_toward_the_first_place_at_the_cruising_speed():
    assert Route((Vector(4.4, 2.3), Vector(-9.0, 0.0)), 1.5, 0.3).command(
        Body(Vector(0.4, -0.7), 0.0, Vector(0.0, 0.0), 0.0)
    ).velocity == Vector(
        approx(1.2), approx(0.9)
    ), "a pilot does not fly toward the first place at the cruising speed"


def test_asks_in_the_frame_of_the_drone():
    assert Route((Vector(0.0, 5.0),), 1.5, 0.3).command(
        Body(Vector(0.0, 0.0), pi / 2, Vector(0.0, 0.0), 0.0)
    ).velocity == Vector(
        approx(1.5), approx(0.0, abs=1e-9)
    ), "a pilot does not ask in the frame of the drone"


def test_eases_off_within_reach_of_a_place():
    assert Route((Vector(0.15, 0.0),), 1.5, 0.3).command(
        Body(Vector(0.0, 0.0), 0.0, Vector(0.0, 0.0), 0.0)
    ).velocity == Vector(
        approx(0.75), approx(0.0)
    ), "a pilot does not ease off within reach of a place"


def test_cannot_ask_to_turn():
    assert Route((Vector(4.4, 2.3),), 1.5, 0.3).command(
        Body(Vector(0.4, -0.7), 0.0, Vector(0.0, 0.0), 0.0)
    ).spin == approx(0.0), "a scripted pilot asks to turn"


def test_forgets_a_place_it_has_reached():
    assert Route((Vector(4.4, 2.3), Vector(-9.0, 0.0)), 1.5, 0.3).rest(
        Body(Vector(4.3, 2.1), 0.0, Vector(0.0, 0.0), 0.0)
    ).places == (Vector(-9.0, 0.0),), "a pilot does not forget a place it has reached"


def test_remembers_a_place_it_has_not_reached():
    assert Route((Vector(4.4, 2.3), Vector(-9.0, 0.0)), 1.5, 0.3).rest(
        Body(Vector(3.9, 2.1), 0.0, Vector(0.0, 0.0), 0.0)
    ).places == (
        Vector(4.4, 2.3),
        Vector(-9.0, 0.0),
    ), "a pilot forgets a place it has not reached"


def test_rests_when_every_place_is_visited():
    assert Route((), 1.5, 0.3).rest(
        Body(Vector(3.9, 2.1), 0.0, Vector(0.0, 0.0), 0.0)
    ).places == (), "a finished route does not stay finished"
