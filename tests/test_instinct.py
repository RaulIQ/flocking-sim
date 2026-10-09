from pytest import approx

from agent.instinct import Instinct
from agent.neighbour import Neighbour
from agent.vector import Vector
from config import Cloud, Limits, Spring


def test_cannot_want_to_fly_alone():
    assert Instinct(
        Cloud(Spring(1.2, 2.0, 0.5, 1.0), Spring(1.2, 2.0, 1.5, 1.5), 2),
        Limits(2.0, 4.0, 1.8, 8.0),
    ).command(()).velocity == Vector(
        approx(0.0), approx(0.0)
    ), "a lonely drone still wants to fly"


def test_follows_the_leader():
    assert Instinct(
        Cloud(Spring(1.2, 2.0, 0.5, 1.0), Spring(1.2, 2.0, 1.5, 1.5), 2),
        Limits(2.0, 4.0, 1.8, 8.0),
    ).command((Neighbour(Vector(2.2, 0.0), True),)).velocity == Vector(
        approx(1.5), approx(0.0)
    ), "a drone does not follow its leader"


def test_follows_the_leader_rather_than_a_peer():
    assert Instinct(
        Cloud(Spring(1.2, 2.0, 0.5, 1.0), Spring(1.2, 2.0, 1.5, 1.5), 2),
        Limits(2.0, 4.0, 1.8, 8.0),
    ).command(
        (Neighbour(Vector(2.2, 0.0), True), Neighbour(Vector(-2.2, 0.0), False))
    ).velocity == Vector(
        approx(1.0), approx(0.0)
    ), "a peer pulls as hard as the leader"


def test_backs_away_from_a_close_peer():
    assert Instinct(
        Cloud(Spring(1.2, 2.0, 0.5, 1.0), Spring(1.2, 2.0, 1.5, 1.5), 2),
        Limits(2.0, 4.0, 1.8, 8.0),
    ).command((Neighbour(Vector(0.0, 0.8), False),)).velocity == Vector(
        approx(0.0), approx(-1.0)
    ), "a drone does not back away from a close peer"


def test_cannot_feel_peers_beyond_its_nearest_few():
    assert Instinct(
        Cloud(Spring(1.2, 2.0, 0.5, 1.0), Spring(1.2, 2.0, 1.5, 1.5), 2),
        Limits(2.0, 4.0, 1.8, 8.0),
    ).command(
        (
            Neighbour(Vector(-5.0, 0.0), False),
            Neighbour(Vector(1.7, 0.0), False),
            Neighbour(Vector(0.0, 1.7), False),
        )
    ).velocity == Vector(
        approx(0.25), approx(0.25)
    ), "a drone feels a peer beyond its nearest few"


def test_feels_the_leader_however_crowded_it_gets():
    assert Instinct(
        Cloud(Spring(1.2, 2.0, 0.5, 1.0), Spring(1.2, 2.0, 1.5, 1.5), 0),
        Limits(2.0, 4.0, 1.8, 8.0),
    ).command((Neighbour(Vector(2.2, 0.0), True),)).velocity == Vector(
        approx(1.5), approx(0.0)
    ), "a crowd hides the leader from a drone"


def test_cannot_want_more_than_the_top_speed():
    assert Instinct(
        Cloud(Spring(1.2, 2.0, 0.5, 1.0), Spring(1.2, 2.0, 1.5, 1.5), 2),
        Limits(2.0, 4.0, 1.8, 8.0),
    ).command((Neighbour(Vector(0.0, -9.0), True),)).velocity == Vector(
        approx(0.0), approx(-2.0)
    ), "a drone wants more than its top speed"


def test_cannot_want_to_turn():
    assert Instinct(
        Cloud(Spring(1.2, 2.0, 0.5, 1.0), Spring(1.2, 2.0, 1.5, 1.5), 2),
        Limits(2.0, 4.0, 1.8, 8.0),
    ).command((Neighbour(Vector(2.2, 1.0), True),)).spin == approx(
        0.0
    ), "a drone wants to turn before turning is built"
