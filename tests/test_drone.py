from pytest import approx

from config import Limits
from simulator.body import Body, Command
from simulator.drone import Drone
from simulator.trail import Trail
from simulator.vector import Vector


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
