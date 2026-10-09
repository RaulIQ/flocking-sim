from itertools import accumulate
from math import pi

from pytest import approx

from agent.command import Command
from agent.shield import Shield
from agent.tuning import Limits
from agent.vector import Vector
from simulator.body import Body
from simulator.wall import Wall


def test_lets_a_request_through_far_from_any_wall():
    assert Shield(Limits(2.0, 2.0, 1.8, 8.0), 0.25, 1.0 / 60).command(
        Command(Vector(1.7, -0.4), 0.0), Vector(0.0, 0.0), (Vector(6.0, 0.0),)
    ).velocity == Vector(
        approx(1.7), approx(-0.4)
    ), "a distant wall changes a request"


def test_lets_a_request_through_with_no_walls_around():
    assert Shield(Limits(2.0, 2.0, 1.8, 8.0), 0.25, 1.0 / 60).command(
        Command(Vector(1.7, -0.4), 0.0), Vector(0.0, 0.0), ()
    ).velocity == Vector(
        approx(1.7), approx(-0.4)
    ), "an empty sky changes a request"


def test_slows_the_approach_to_a_wall():
    assert Shield(Limits(2.0, 2.0, 1.8, 8.0), 0.25, 1.0 / 60).command(
        Command(Vector(2.0, 0.0), 0.0), Vector(0.0, 0.0), (Vector(0.75, 0.0),)
    ).velocity == Vector(
        approx(1.0), approx(0.0)
    ), "a drone approaches a wall faster than it can brake"


def test_cannot_approach_a_wall_at_the_margin():
    assert Shield(Limits(2.0, 2.0, 1.8, 8.0), 0.25, 1.0 / 60).command(
        Command(Vector(2.0, 0.0), 0.0), Vector(0.0, 0.0), (Vector(0.25, 0.0),)
    ).velocity == Vector(
        approx(0.0), approx(0.0)
    ), "a drone at the margin still approaches a wall"


def test_cannot_approach_a_wall_from_inside_the_margin():
    assert Shield(Limits(2.0, 2.0, 1.8, 8.0), 0.25, 1.0 / 60).command(
        Command(Vector(0.0, -1.3), 0.0), Vector(0.0, 0.0), (Vector(0.0, -0.1),)
    ).velocity == Vector(
        approx(0.0), approx(0.0)
    ), "a drone inside the margin still approaches a wall"


def test_slides_along_a_wall_at_full_speed():
    assert Shield(Limits(2.0, 2.0, 1.8, 8.0), 0.25, 1.0 / 60).command(
        Command(Vector(1.2, 1.6), 0.0), Vector(0.0, 0.0), (Vector(0.25, 0.0),)
    ).velocity == Vector(
        approx(0.0), approx(1.6)
    ), "a drone does not slide along a wall"


def test_retreats_from_a_wall_at_full_speed():
    assert Shield(Limits(2.0, 2.0, 1.8, 8.0), 0.25, 1.0 / 60).command(
        Command(Vector(-2.0, 0.0), 0.0), Vector(0.0, 0.0), (Vector(0.1, 0.0),)
    ).velocity == Vector(
        approx(-2.0), approx(0.0)
    ), "a drone cannot retreat from a wall"


def test_stops_in_a_corner_between_two_walls():
    assert Shield(Limits(2.0, 2.0, 1.8, 8.0), 0.25, 1.0 / 60).command(
        Command(Vector(1.2, 1.6), 0.0), Vector(0.0, 0.0), (Vector(0.25, 0.0), Vector(0.0, 0.25))
    ).velocity == Vector(
        approx(0.0), approx(0.0)
    ), "a drone does not stop in a corner between two walls"


def test_brakes_before_anything_else_when_it_closes_too_fast():
    assert Shield(Limits(2.0, 2.0, 1.8, 8.0), 0.25, 1.0 / 60).command(
        Command(Vector(0.0, 2.0), 0.0), Vector(2.0, 0.0), (Vector(0.75, 0.0),)
    ).velocity == Vector(
        approx(1.0), approx(0.0)
    ), "a drone closing too fast does not spend its whole request on braking"


def test_obeys_a_sideways_request_while_it_closes_slowly_enough():
    assert Shield(Limits(2.0, 2.0, 1.8, 8.0), 0.25, 1.0 / 60).command(
        Command(Vector(0.0, 2.0), 0.0), Vector(0.6, 0.0), (Vector(0.75, 0.0),)
    ).velocity == Vector(
        approx(0.0), approx(2.0)
    ), "a drone closing slowly enough does not obey a sideways request"


def test_cannot_cover_more_than_the_room_left_in_one_tick():
    assert Shield(Limits(2.0, 2.0, 1.8, 8.0), 0.25, 0.5).command(
        Command(Vector(2.0, 0.0), 0.0), Vector(0.0, 0.0), (Vector(0.35, 0.0),)
    ).velocity == Vector(
        approx(0.2), approx(0.0)
    ), "a drone may step over the margin within one tick"


def test_cannot_change_the_turn_of_a_request():
    assert Shield(Limits(2.0, 2.0, 1.8, 8.0), 0.25, 1.0 / 60).command(
        Command(Vector(2.0, 0.0), 1.3), Vector(0.0, 0.0), (Vector(0.25, 0.0),)
    ).spin == approx(1.3), "a wall changes the turn of a request"


def test_cannot_let_a_drone_fly_into_a_wall_at_full_speed():
    assert min(
        Wall(Vector(4.0, -7.0), Vector(4.0, 7.0)).nearest(body.position).minus(body.position).length()
        for body in accumulate(
            range(600),
            lambda body, frame: body.moved(
                Shield(Limits(2.0, 4.0, 1.8, 8.0), 0.25, 1.0 / 60).command(
                    Command(Vector(2.0, 0.0), 0.0),
                    body.velocity.turned(-body.heading),
                    (
                        Wall(Vector(4.0, -7.0), Vector(4.0, 7.0))
                        .nearest(body.position)
                        .minus(body.position)
                        .turned(-body.heading),
                    ),
                ),
                Limits(2.0, 4.0, 1.8, 8.0),
                1.0 / 60,
            ),
            initial=Body(Vector(0.0, 0.3), pi / 7, Vector(0.0, 0.0), 0.0),
        )
    ) > 0.2, "a drone flown at a wall at full speed comes too close to it"
