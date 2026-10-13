from pytest import approx

from agent.command import Command
from agent.instinct import Instinct
from agent.mind import Mind
from agent.senses import Motion, Senses
from agent.shield import Shield
from agent.signals import Bearing, Range, Role, Signals
from agent.tracker import Tracker
from agent.neighbour import Neighbour
from agent.tracks import Track, Tracks
from agent.tuning import Cloud, Limits, Spring
from simulator.body import Body
from simulator.drone import Drone
from simulator.trail import Trail
from agent.vector import Vector


def test_takes_the_body_it_is_placed_in():
    assert Drone(
        Body(Vector(0.4, -0.7), 0.0, Vector(0.0, 0.0), 0.0), Trail((), 5), False
    ).placed(Body(Vector(1.4, -0.7), 0.0, Vector(2.0, 0.0), 0.0)).body.position == Vector(
        approx(1.4), approx(-0.7)
    ), "a drone does not take the body it is placed in"


def test_remembers_where_it_was_just_placed():
    assert Drone(
        Body(Vector(0.4, -0.7), 0.0, Vector(0.0, 0.0), 0.0), Trail((), 5), False
    ).placed(Body(Vector(1.4, -0.7), 0.0, Vector(2.0, 0.0), 0.0)).trail.points == (
        Vector(approx(1.4), approx(-0.7)),
    ), "a drone does not remember where it was just placed"


def test_stays_the_leader_once_placed():
    assert Drone(
        Body(Vector(0.4, -0.7), 0.0, Vector(0.0, 0.0), 0.0), Trail((), 5), True
    ).placed(Body(Vector(1.4, -0.7), 0.0, Vector(2.0, 0.0), 0.0)).leader, "a leader does not stay the leader once placed"


def test_cannot_become_the_leader_by_being_placed():
    assert not Drone(
        Body(Vector(0.4, -0.7), 0.0, Vector(0.0, 0.0), 0.0), Trail((), 5), False
    ).placed(Body(Vector(1.4, -0.7), 0.0, Vector(2.0, 0.0), 0.0)).leader, "a follower turns into the leader by being placed"


def test_starts_with_nothing_remembered():
    assert Drone(
        Body(Vector(0.4, -0.7), 0.0, Vector(0.0, 0.0), 0.0), Trail((), 5), False
    ).memory == Tracks(()), "a fresh drone remembers something"


def test_keeps_what_it_is_reminded_of():
    assert Drone(
        Body(Vector(0.4, -0.7), 0.0, Vector(0.0, 0.0), 0.0), Trail((), 5), False
    ).reminded(
        Tracks((Track(3, Neighbour(Vector(1.1, 0.2), Vector(0.0, 0.0), False), True),))
    ).memory == Tracks(
        (Track(3, Neighbour(Vector(1.1, 0.2), Vector(0.0, 0.0), False), True),)
    ), "a drone does not keep what it is reminded of"


def test_keeps_its_memory_once_placed():
    assert Drone(
        Body(Vector(0.4, -0.7), 0.0, Vector(0.0, 0.0), 0.0),
        Trail((), 5),
        False,
        Tracks((Track(3, Neighbour(Vector(1.1, 0.2), Vector(0.0, 0.0), False), True),)),
    ).placed(Body(Vector(1.4, -0.7), 0.0, Vector(2.0, 0.0), 0.0)).memory == Tracks(
        (Track(3, Neighbour(Vector(1.1, 0.2), Vector(0.0, 0.0), False), True),)
    ), "a new place wipes what a drone remembers"


def test_decides_by_its_mind_on_what_it_remembers_and_senses():
    assert Drone(
        Body(Vector(0.0, 0.0), 0.0, Vector(0.0, 0.0), 0.0),
        Trail((), 5),
        False,
        Tracks((Track(1, Neighbour(Vector(2.2, 0.0), Vector(0.0, 0.0), True), True),)),
    ).command(
        Mind(
            Instinct(Cloud(Spring(1.2, 4.0, 0.5, 1.0), Spring(1.2, 4.0, 1.5, 1.5), Spring(0.6, 8.0, 0.0, 0.0), 6), Limits(2.0, 100.0, 1.8, 8.0)),
            Shield(Limits(2.0, 100.0, 1.8, 8.0), 0.25, 0.5, 0.0),
            Tracker(0.5),
            True,
        ),
        Senses(
            Motion(Vector(0.0, 0.0), 0.0),
            Signals((Range(1, 2.2),), (Bearing(1, 0.0),), (Role(1, True),)),
            (),
            Command(Vector(0.0, -2.0), 0.0),
        ),
    ).velocity == Vector(
        approx(1.5), approx(0.0)
    ), "a follower handed a leading mind does not decide by its own role"


def test_remembers_what_it_sensed():
    assert Drone(
        Body(Vector(0.0, 0.0), 0.0, Vector(0.0, 0.0), 0.0), Trail((), 5), False
    ).recalled(
        Mind(
            Instinct(Cloud(Spring(1.2, 4.0, 0.5, 1.0), Spring(1.2, 4.0, 1.5, 1.5), Spring(0.6, 8.0, 0.0, 0.0), 6), Limits(2.0, 100.0, 1.8, 8.0)),
            Shield(Limits(2.0, 100.0, 1.8, 8.0), 0.25, 0.5, 0.0),
            Tracker(0.5),
            False,
        ),
        Senses(
            Motion(Vector(0.0, 0.0), 0.0),
            Signals((Range(1, 2.2),), (Bearing(1, 0.0),), (Role(1, True),)),
            (),
            Command(Vector(0.0, 0.0), 0.0),
        ),
    ).memory == Tracks(
        (Track(1, Neighbour(Vector(approx(2.2), approx(0.0)), Vector(0.0, 0.0), True), True),)
    ), "a drone does not remember what it sensed"
