from functools import reduce
from itertools import accumulate
from math import pi, sqrt

from pytest import approx

from agent.command import Command
from agent.neighbour import Neighbour
from agent.shield import Shield
from agent.tuning import Limits
from agent.vector import Vector
from simulator.body import Body
from simulator.wall import Wall


def test_lets_a_request_through_far_from_any_wall():
    assert Shield(Limits(2.0, 2.0, 1.8, 8.0), 0.25, 1.0 / 60, 0.0).command(
        Command(Vector(1.7, -0.4), 0.0), Vector(0.0, 0.0), (Vector(6.0, 0.0),)
    ).velocity == Vector(
        approx(1.7), approx(-0.4)
    ), "a distant wall changes a request"


def test_lets_a_request_through_with_no_walls_around():
    assert Shield(Limits(2.0, 2.0, 1.8, 8.0), 0.25, 1.0 / 60, 0.0).command(
        Command(Vector(1.7, -0.4), 0.0), Vector(0.0, 0.0), ()
    ).velocity == Vector(
        approx(1.7), approx(-0.4)
    ), "an empty sky changes a request"


def test_slows_the_approach_to_a_wall():
    assert Shield(Limits(2.0, 2.0, 1.8, 8.0), 0.25, 1.0 / 60, 0.0).command(
        Command(Vector(2.0, 0.0), 0.0), Vector(0.0, 0.0), (Vector(0.75, 0.0),)
    ).velocity == Vector(
        approx(1.0), approx(0.0)
    ), "a drone approaches a wall faster than it can brake"


def test_cannot_approach_a_wall_at_the_margin():
    assert Shield(Limits(2.0, 2.0, 1.8, 8.0), 0.25, 1.0 / 60, 0.0).command(
        Command(Vector(2.0, 0.0), 0.0), Vector(0.0, 0.0), (Vector(0.25, 0.0),)
    ).velocity == Vector(
        approx(0.0), approx(0.0)
    ), "a drone at the margin still approaches a wall"


def test_cannot_approach_a_wall_from_inside_the_margin():
    assert Shield(Limits(2.0, 2.0, 1.8, 8.0), 0.25, 1.0 / 60, 0.0).command(
        Command(Vector(0.0, -1.3), 0.0), Vector(0.0, 0.0), (Vector(0.0, -0.1),)
    ).velocity == Vector(
        approx(0.0), approx(0.0)
    ), "a drone inside the margin still approaches a wall"


def test_slides_along_a_wall_at_full_speed():
    assert Shield(Limits(2.0, 2.0, 1.8, 8.0), 0.25, 1.0 / 60, 0.0).command(
        Command(Vector(1.2, 1.6), 0.0), Vector(0.0, 0.0), (Vector(0.25, 0.0),)
    ).velocity == Vector(
        approx(0.0), approx(1.6)
    ), "a drone does not slide along a wall"


def test_retreats_from_a_wall_at_full_speed():
    assert Shield(Limits(2.0, 2.0, 1.8, 8.0), 0.25, 1.0 / 60, 0.0).command(
        Command(Vector(-2.0, 0.0), 0.0), Vector(0.0, 0.0), (Vector(0.1, 0.0),)
    ).velocity == Vector(
        approx(-2.0), approx(0.0)
    ), "a drone cannot retreat from a wall"


def test_stops_in_a_corner_between_two_walls():
    assert Shield(Limits(2.0, 2.0, 1.8, 8.0), 0.25, 1.0 / 60, 0.0).command(
        Command(Vector(1.2, 1.6), 0.0), Vector(0.0, 0.0), (Vector(0.25, 0.0), Vector(0.0, 0.25))
    ).velocity == Vector(
        approx(0.0), approx(0.0)
    ), "a drone does not stop in a corner between two walls"


def test_brakes_before_anything_else_when_it_closes_too_fast():
    assert Shield(Limits(2.0, 2.0, 1.8, 8.0), 0.25, 1.0 / 60, 0.0).command(
        Command(Vector(0.0, 2.0), 0.0), Vector(2.0, 0.0), (Vector(0.75, 0.0),)
    ).velocity == Vector(
        approx(1.0), approx(0.0)
    ), "a drone closing too fast does not spend its whole request on braking"


def test_obeys_a_sideways_request_while_it_closes_slowly_enough():
    assert Shield(Limits(2.0, 2.0, 1.8, 8.0), 0.25, 1.0 / 60, 0.0).command(
        Command(Vector(0.0, 2.0), 0.0), Vector(0.6, 0.0), (Vector(0.75, 0.0),)
    ).velocity == Vector(
        approx(0.0), approx(2.0)
    ), "a drone closing slowly enough does not obey a sideways request"


def test_cannot_cover_more_than_the_room_left_in_one_tick():
    assert Shield(Limits(2.0, 2.0, 1.8, 8.0), 0.25, 0.5, 0.0).command(
        Command(Vector(2.0, 0.0), 0.0), Vector(0.0, 0.0), (Vector(0.35, 0.0),)
    ).velocity == Vector(
        approx(0.2), approx(0.0)
    ), "a drone may step over the margin within one tick"


def test_spends_on_the_request_what_braking_leaves_of_one_tick():
    assert Shield(Limits(2.0, 2.0, 1.8, 8.0), 0.25, 0.5, 0.0).command(
        Command(Vector(0.0, 2.0), 0.0), Vector(1.4, 0.0), (Vector(0.75, 0.0),)
    ).velocity == Vector(
        approx(0.7317, abs=1e-4), approx(0.5367, abs=1e-4)
    ), "a drone that brakes a little spends nothing on the request"


def test_cannot_go_deaf_to_a_sideways_request_over_a_rounding_error():
    assert Shield(Limits(2.0, 2.0, 1.8, 8.0), 0.25, 1.0 / 60, 0.0).command(
        Command(Vector(0.0, 1.5), 0.0), Vector(1e-17, 0.0), (Vector(0.25, 0.0),)
    ).velocity == Vector(
        approx(0.0), approx(2.0 / 60)
    ), "a rounding error makes a drone deaf to a sideways request"


def test_lets_a_request_through_with_every_neighbour_placed():
    assert Shield(Limits(2.0, 4.0, 1.8, 8.0), 0.25, 1.0 / 60, 0.0).slowed(
        Command(Vector(1.7, -0.4), 0.3), ()
    ) == Command(
        Vector(approx(1.7), approx(-0.4)), approx(0.3)
    ), "a drone slows down with no unplaced neighbour around"


def test_slows_down_near_a_neighbour_known_by_distance_alone():
    assert Shield(Limits(2.0, 4.0, 1.8, 8.0), 0.25, 1.0 / 60, 0.0).slowed(
        Command(Vector(1.2, -1.6), 0.0), (0.7,)
    ).velocity == Vector(
        approx(0.3795, abs=1e-4), approx(-0.5060, abs=1e-4)
    ), "a drone does not slow down near a neighbour known by distance alone"


def test_slows_down_for_the_closest_of_the_neighbours_it_cannot_place():
    assert Shield(Limits(2.0, 4.0, 1.8, 8.0), 0.25, 1.0 / 60, 0.0).slowed(
        Command(Vector(2.0, 0.0), 0.0), (3.0, 0.7, 1.5)
    ).velocity == Vector(
        approx(0.6325, abs=1e-4), approx(0.0)
    ), "a drone does not slow down for the closest unplaced neighbour"


def test_cannot_slow_down_for_a_distant_neighbour_known_by_distance_alone():
    assert Shield(Limits(2.0, 4.0, 1.8, 8.0), 0.25, 1.0 / 60, 0.0).slowed(
        Command(Vector(2.0, 0.0), 0.0), (3.0,)
    ).velocity == Vector(
        approx(2.0), approx(0.0)
    ), "a distant unplaced neighbour slows a drone down"


def test_stops_when_two_margins_touch_a_neighbour_known_by_distance_alone():
    assert Shield(Limits(2.0, 4.0, 1.8, 8.0), 0.25, 1.0 / 60, 0.0).slowed(
        Command(Vector(1.2, -1.6), 0.7), (0.5,)
    ) == Command(
        Vector(approx(0.0), approx(0.0)), approx(0.7)
    ), "a drone keeps flying when its margin touches that of an unplaced neighbour"


def test_cannot_change_the_turn_of_a_request():
    assert Shield(Limits(2.0, 2.0, 1.8, 8.0), 0.25, 1.0 / 60, 0.0).command(
        Command(Vector(2.0, 0.0), 1.3), Vector(0.0, 0.0), (Vector(0.25, 0.0),)
    ).spin == approx(1.3), "a wall changes the turn of a request"


def test_cannot_let_a_drone_fly_into_a_wall_at_full_speed():
    assert min(
        Wall(Vector(4.0, -7.0), Vector(4.0, 7.0)).nearest(body.position).minus(body.position).length()
        for body in accumulate(
            range(600),
            lambda body, frame: body.moved(
                Shield(Limits(2.0, 4.0, 1.8, 8.0), 0.25, 1.0 / 60, 0.0).command(
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


def test_slides_along_a_wall_to_where_the_pilot_asks_whichever_way_it_faces():
    assert max(
        abs(
            reduce(
                lambda body, frame: body.moved(
                    Shield(Limits(2.0, 4.0, 1.8, 8.0), 0.25, 1.0 / 60, 0.0).command(
                        Command(
                            Vector(8.0, 3.0)
                            .minus(body.position)
                            .times(2.0 / 0.3)
                            .capped(2.0)
                            .turned(-body.heading),
                            0.0,
                        ),
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
                range(1200),
                Body(Vector(0.0, 0.0), heading, Vector(0.0, 0.0), 0.0),
            ).position.y
            - 3.0
        )
        for heading in (0.7, 1.0, 1.9, 3.3, 4.4, 5.5)
    ) < 0.01, "a turned drone pressed against a wall does not stop where the pilot asks"


def test_slows_the_last_stretch_for_a_drone_that_answers_late():
    assert Shield(Limits(2.0, 4.0, 1.8, 8.0), 0.25, 0.05, 0.7).bound(0.3) == approx(
        0.4
    ), "a drone that answers late may close as fast as one that answers at once"


def test_counts_out_the_room_a_late_drone_covers_before_it_answers():
    assert Shield(Limits(2.0, 4.0, 1.8, 8.0), 0.25, 0.05, 0.5).command(
        Command(Vector(2.0, 0.0), 0.0), Vector(1.0, 0.0), (Vector(1.25, 0.0),)
    ).velocity == Vector(
        approx(0.5 / 0.55), approx(0.0)
    ), "the room a late drone covers before it answers is not counted out"


def test_cannot_count_out_any_room_for_a_drone_flying_away():
    assert Shield(Limits(2.0, 4.0, 1.8, 8.0), 0.25, 0.05, 0.5).command(
        Command(Vector(2.0, 0.0), 0.0), Vector(-1.0, 0.0), (Vector(1.25, 0.0),)
    ).velocity == Vector(
        approx(1.0 / 0.55), approx(0.0)
    ), "a drone flying away from a wall loses room to its own retreat"


def test_cannot_close_on_a_neighbour_faster_than_half_the_room_allows():
    assert Shield(Limits(2.0, 4.0, 1.8, 8.0), 0.25, 0.05, 0.0).kept(
        Command(Vector(2.0, 0.3), 0.0),
        Vector(0.0, 0.0),
        (Neighbour(Vector(1.5, 0.0), Vector(0.0, 0.0), False),),
    ).velocity == Vector(
        approx(sqrt(2.0)), approx(0.3)
    ), "a drone closes on a neighbour faster than half the room allows"


def test_follows_a_neighbour_that_flies_away_as_fast_as_it_goes():
    assert Shield(Limits(2.0, 4.0, 1.8, 8.0), 0.25, 0.05, 0.0).kept(
        Command(Vector(2.0, 0.0), 0.0),
        Vector(0.0, 0.0),
        (Neighbour(Vector(1.5, 0.0), Vector(1.0, 0.0), True),),
    ).velocity == Vector(
        approx(2.0), approx(0.0)
    ), "a drone is held back behind a neighbour that flies away"


def test_stops_two_margins_short_of_a_neighbour():
    assert Shield(Limits(2.0, 4.0, 1.8, 8.0), 0.25, 0.05, 0.0).kept(
        Command(Vector(2.0, 0.0), 0.0),
        Vector(0.0, 0.0),
        (Neighbour(Vector(0.5, 0.0), Vector(0.0, 0.0), False),),
    ).velocity == Vector(
        approx(0.0), approx(0.0)
    ), "a drone still closes on a neighbour two margins away"


def test_gives_way_to_a_neighbour_that_comes_at_it():
    assert Shield(Limits(2.0, 4.0, 1.8, 8.0), 0.25, 0.05, 0.0).kept(
        Command(Vector(0.0, 0.0), 0.0),
        Vector(0.0, 0.0),
        (Neighbour(Vector(0.5, 0.0), Vector(-1.0, 0.0), False),),
    ).velocity == Vector(
        approx(-1.0), approx(0.0)
    ), "a drone does not give way to a neighbour that comes at it"


def test_counts_out_the_room_two_late_drones_close_before_they_answer():
    assert Shield(Limits(2.0, 4.0, 1.8, 8.0), 0.25, 0.05, 0.5).kept(
        Command(Vector(2.0, 0.0), 0.0),
        Vector(1.0, 0.0),
        (Neighbour(Vector(1.5, 0.0), Vector(0.0, 0.0), False),),
    ).velocity == Vector(
        approx(0.25 / 0.55), approx(0.0)
    ), "the room two late drones close before they answer is not counted out"


def test_cannot_change_a_request_with_no_neighbours_around():
    assert Shield(Limits(2.0, 4.0, 1.8, 8.0), 0.25, 0.05, 0.5).kept(
        Command(Vector(1.3, -0.4), 0.7), Vector(1.0, 0.0), ()
    ) == Command(
        Vector(1.3, -0.4), 0.7
    ), "a drone with no neighbours around does not fly what it asks"


def test_leaves_a_late_drone_that_closes_too_fast_a_share_of_its_request():
    assert Shield(Limits(2.0, 4.0, 1.8, 8.0), 0.25, 0.05, 0.5).command(
        Command(Vector(0.0, 1.0), 0.0), Vector(2.0, 0.0), (Vector(1.25, 0.0),)
    ).velocity == Vector(
        approx(0.0), approx(0.2)
    ), "a late drone that closes too fast gets no share of its request"
