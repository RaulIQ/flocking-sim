from pytest import approx

from agent.command import Command
from agent.instinct import Instinct
from agent.mind import Mind
from agent.senses import Motion, Senses
from agent.shield import Shield
from agent.signals import Bearing, Range, Role, Signals
from agent.tracker import Tracker
from agent.tracks import Track, Tracks
from agent.tuning import Cloud, Limits, Spring
from simulator.body import Body
from simulator.drone import Drone
from simulator.trail import Trail
from agent.vector import Vector


def test_flies_its_body_on_a_request():
    assert Drone(
        Body(Vector(0.4, -0.7), 0.0, Vector(0.0, 0.0), 0.0), Trail((), 5), False
    ).moved(
        Command(Vector(2.0, 0.0), 0.0), Limits(2.0, 100.0, 1.8, 8.0), 0.5
    ).body.position == Vector(
        approx(1.4), approx(-0.7)
    ), "a drone does not fly its body on a request"


def test_remembers_where_it_has_just_flown():
    assert Drone(
        Body(Vector(0.4, -0.7), 0.0, Vector(0.0, 0.0), 0.0), Trail((), 5), False
    ).moved(
        Command(Vector(2.0, 0.0), 0.0), Limits(2.0, 100.0, 1.8, 8.0), 0.5
    ).trail.points == (
        Vector(approx(1.4), approx(-0.7)),
    ), "a drone does not remember where it has just flown"


def test_stays_the_leader_after_a_move():
    assert Drone(
        Body(Vector(0.4, -0.7), 0.0, Vector(0.0, 0.0), 0.0), Trail((), 5), True
    ).moved(
        Command(Vector(2.0, 0.0), 0.0), Limits(2.0, 100.0, 1.8, 8.0), 0.5
    ).leader, "a leader does not stay the leader after a move"


def test_cannot_become_the_leader_by_moving():
    assert not Drone(
        Body(Vector(0.4, -0.7), 0.0, Vector(0.0, 0.0), 0.0), Trail((), 5), False
    ).moved(
        Command(Vector(2.0, 0.0), 0.0), Limits(2.0, 100.0, 1.8, 8.0), 0.5
    ).leader, "a follower turns into the leader by moving"


def test_starts_with_nothing_remembered():
    assert Drone(
        Body(Vector(0.4, -0.7), 0.0, Vector(0.0, 0.0), 0.0), Trail((), 5), False
    ).memory == Tracks(()), "a fresh drone remembers something"


def test_keeps_what_it_is_reminded_of():
    assert Drone(
        Body(Vector(0.4, -0.7), 0.0, Vector(0.0, 0.0), 0.0), Trail((), 5), False
    ).reminded(
        Tracks((Track(3, Vector(1.1, 0.2), True, False),))
    ).memory == Tracks(
        (Track(3, Vector(1.1, 0.2), True, False),)
    ), "a drone does not keep what it is reminded of"


def test_keeps_its_memory_through_a_move():
    assert Drone(
        Body(Vector(0.4, -0.7), 0.0, Vector(0.0, 0.0), 0.0),
        Trail((), 5),
        False,
        Tracks((Track(3, Vector(1.1, 0.2), True, False),)),
    ).moved(
        Command(Vector(2.0, 0.0), 0.0), Limits(2.0, 100.0, 1.8, 8.0), 0.5
    ).memory == Tracks(
        (Track(3, Vector(1.1, 0.2), True, False),)
    ), "a move wipes what a drone remembers"


def test_flies_by_its_mind_on_what_it_senses():
    assert Drone(
        Body(Vector(0.0, 0.0), 0.0, Vector(0.0, 0.0), 0.0), Trail((), 5), False
    ).flown(
        Mind(
            Instinct(Cloud(Spring(1.2, 4.0, 0.5, 1.0), Spring(1.2, 4.0, 1.5, 1.5), Spring(0.6, 8.0, 0.0, 0.0), 6), Limits(2.0, 100.0, 1.8, 8.0)),
            Shield(Limits(2.0, 100.0, 1.8, 8.0), 0.25, 0.5),
            Tracker(0.5),
            True,
        ),
        Senses(
            Motion(Vector(0.0, 0.0), 0.0),
            Signals((Range(1, 2.2),), (Bearing(1, 0.0),), (Role(1, True),)),
            (),
            Command(Vector(0.0, -2.0), 0.0),
        ),
        Limits(2.0, 100.0, 1.8, 8.0),
        0.5,
    ).body.position == Vector(
        approx(0.75), approx(0.0)
    ), "a follower handed a leading mind does not fly by its own role"


def test_remembers_what_it_sensed_while_flying():
    assert Drone(
        Body(Vector(0.0, 0.0), 0.0, Vector(0.0, 0.0), 0.0), Trail((), 5), False
    ).flown(
        Mind(
            Instinct(Cloud(Spring(1.2, 4.0, 0.5, 1.0), Spring(1.2, 4.0, 1.5, 1.5), Spring(0.6, 8.0, 0.0, 0.0), 6), Limits(2.0, 100.0, 1.8, 8.0)),
            Shield(Limits(2.0, 100.0, 1.8, 8.0), 0.25, 0.5),
            Tracker(0.5),
            False,
        ),
        Senses(
            Motion(Vector(0.0, 0.0), 0.0),
            Signals((Range(1, 2.2),), (Bearing(1, 0.0),), (Role(1, True),)),
            (),
            Command(Vector(0.0, 0.0), 0.0),
        ),
        Limits(2.0, 100.0, 1.8, 8.0),
        0.5,
    ).memory == Tracks(
        (Track(1, Vector(approx(2.2), approx(0.0)), True, True),)
    ), "a drone does not remember what it sensed while flying"
