from pytest import approx, raises

from config import Limits
from simulator.body import Body, Command
from simulator.drone import Drone
from simulator.flock import Flock
from simulator.trail import Trail
from simulator.vector import Vector


def test_finds_its_leader():
    assert Flock(
        (
            Drone(Body(Vector(1.3, 0.2), 0.0, Vector(0.0, 0.0), 0.0), Trail((), 5), False),
            Drone(Body(Vector(-0.6, 0.9), 0.0, Vector(0.0, 0.0), 0.0), Trail((), 5), True),
        )
    ).leader().body.position == Vector(
        approx(-0.6), approx(0.9)
    ), "a flock does not find its leader"


def test_flies_the_leader_on_a_request():
    assert Flock(
        (
            Drone(Body(Vector(1.3, 0.2), 0.0, Vector(0.0, 0.0), 0.0), Trail((), 5), False),
            Drone(Body(Vector(-0.6, 0.9), 0.0, Vector(0.0, 0.0), 0.0), Trail((), 5), True),
        )
    ).moved(
        Command(Vector(2.0, 0.0), 0.0), Limits(2.0, 100.0, 1.8, 8.0), 0.5
    ).leader().body.position == Vector(
        approx(0.4), approx(0.9)
    ), "a flock does not fly its leader on a request"


def test_cannot_fly_a_follower_on_the_request_of_the_pilot():
    assert Flock(
        (
            Drone(Body(Vector(1.3, 0.2), 0.0, Vector(0.0, 0.0), 0.0), Trail((), 5), False),
            Drone(Body(Vector(-0.6, 0.9), 0.0, Vector(0.0, 0.0), 0.0), Trail((), 5), True),
        )
    ).moved(
        Command(Vector(2.0, 0.0), 1.2), Limits(2.0, 100.0, 1.8, 8.0), 0.5
    ).drones[0].body == Body(
        Vector(approx(1.3), approx(0.2)), approx(0.0), Vector(approx(0.0), approx(0.0)), approx(0.0)
    ), "a follower obeys the pilot"


def test_keeps_every_drone_after_a_move():
    assert len(
        Flock(
            (
                Drone(Body(Vector(1.3, 0.2), 0.0, Vector(0.0, 0.0), 0.0), Trail((), 5), False),
                Drone(Body(Vector(-0.6, 0.9), 0.0, Vector(0.0, 0.0), 0.0), Trail((), 5), True),
                Drone(Body(Vector(0.1, -1.4), 0.0, Vector(0.0, 0.0), 0.0), Trail((), 5), False),
            )
        )
        .moved(Command(Vector(2.0, 0.0), 0.0), Limits(2.0, 100.0, 1.8, 8.0), 0.5)
        .drones
    ) == 3, "a flock loses a drone during a move"


def test_cannot_find_a_leader_among_followers_only():
    with raises(LookupError, match="no leader"):
        Flock(
            (Drone(Body(Vector(1.3, 0.2), 0.0, Vector(0.0, 0.0), 0.0), Trail((), 5), False),)
        ).leader()
