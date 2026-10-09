from functools import reduce
from itertools import accumulate, combinations
from math import pi

from pytest import approx, raises

from agent.command import Command
from agent.instinct import Instinct
from agent.neighbour import Neighbour
from agent.vector import Vector
from config import Cloud, Limits, Spring
from simulator.body import Body
from simulator.drone import Drone
from simulator.flock import Flock
from simulator.muster import Muster
from simulator.trail import Trail


def test_finds_its_leader():
    assert Flock(
        (
            Drone(Body(Vector(1.3, 0.2), 0.0, Vector(0.0, 0.0), 0.0), Trail((), 5), False),
            Drone(Body(Vector(-0.6, 0.9), 0.0, Vector(0.0, 0.0), 0.0), Trail((), 5), True),
        )
    ).leader().body.position == Vector(
        approx(-0.6), approx(0.9)
    ), "a flock does not find its leader"


def test_cannot_find_a_leader_among_followers_only():
    with raises(LookupError, match="no leader"):
        Flock(
            (Drone(Body(Vector(1.3, 0.2), 0.0, Vector(0.0, 0.0), 0.0), Trail((), 5), False),)
        ).leader()


def test_tells_a_drone_where_the_others_are_in_its_own_frame():
    assert Flock(
        (
            Drone(Body(Vector(1.0, 1.0), pi / 2, Vector(0.0, 0.0), 0.0), Trail((), 5), False),
            Drone(Body(Vector(1.0, 3.5), 0.0, Vector(0.0, 0.0), 0.0), Trail((), 5), True),
        )
    ).seen(
        Drone(Body(Vector(1.0, 1.0), pi / 2, Vector(0.0, 0.0), 0.0), Trail((), 5), False)
    ) == (
        Neighbour(Vector(approx(0.0, abs=1e-9), approx(0.0, abs=1e-9)), False),
        Neighbour(Vector(approx(2.5), approx(0.0, abs=1e-9)), True),
    ), "a drone is not told where the others are in its own frame"


def test_cannot_tell_a_drone_about_itself():
    flock = Flock(
        (
            Drone(Body(Vector(1.0, 1.0), pi / 2, Vector(0.0, 0.0), 0.0), Trail((), 5), False),
            Drone(Body(Vector(1.0, 3.5), 0.0, Vector(0.0, 0.0), 0.0), Trail((), 5), True),
        )
    )
    assert flock.seen(flock.drones[0]) == (
        Neighbour(Vector(approx(2.5), approx(0.0, abs=1e-9)), True),
    ), "a drone is told about itself"


def test_flies_the_leader_on_the_request_of_the_pilot():
    assert Flock(
        (
            Drone(Body(Vector(1.3, 0.2), 0.0, Vector(0.0, 0.0), 0.0), Trail((), 5), False),
            Drone(Body(Vector(-0.6, 0.9), 0.0, Vector(0.0, 0.0), 0.0), Trail((), 5), True),
        )
    ).moved(
        Command(Vector(2.0, 0.0), 0.0),
        Instinct(
            Cloud(Spring(1.2, 4.0, 0.5, 1.0), Spring(1.2, 4.0, 1.5, 1.5), 6),
            Limits(2.0, 100.0, 1.8, 8.0),
        ),
        Limits(2.0, 100.0, 1.8, 8.0),
        0.5,
    ).leader().body.position == Vector(
        approx(0.4), approx(0.9)
    ), "a flock does not fly its leader on the request of the pilot"


def test_cannot_fly_a_follower_on_the_request_of_the_pilot():
    assert Flock(
        (
            Drone(Body(Vector(1.2, 0.0), 0.0, Vector(0.0, 0.0), 0.0), Trail((), 5), False),
            Drone(Body(Vector(0.0, 0.0), 0.0, Vector(0.0, 0.0), 0.0), Trail((), 5), True),
        )
    ).moved(
        Command(Vector(0.0, 2.0), 1.2),
        Instinct(
            Cloud(Spring(1.2, 4.0, 0.5, 1.0), Spring(1.2, 4.0, 1.5, 1.5), 6),
            Limits(2.0, 100.0, 1.8, 8.0),
        ),
        Limits(2.0, 100.0, 1.8, 8.0),
        0.5,
    ).drones[0].body == Body(
        Vector(approx(1.2), approx(0.0)),
        approx(0.0),
        Vector(approx(0.0), approx(0.0)),
        approx(0.0),
    ), "a follower at rest obeys the pilot"


def test_flies_a_follower_toward_a_distant_leader_along_its_own_nose():
    assert Flock(
        (
            Drone(Body(Vector(0.0, 0.0), pi / 2, Vector(0.0, 0.0), 0.0), Trail((), 5), False),
            Drone(Body(Vector(0.0, 2.2), 0.0, Vector(0.0, 0.0), 0.0), Trail((), 5), True),
        )
    ).moved(
        Command(Vector(0.0, 0.0), 0.0),
        Instinct(
            Cloud(Spring(1.2, 4.0, 0.5, 1.0), Spring(1.2, 4.0, 1.5, 1.5), 6),
            Limits(2.0, 100.0, 1.8, 8.0),
        ),
        Limits(2.0, 100.0, 1.8, 8.0),
        0.5,
    ).drones[0].body.position == Vector(
        approx(0.0, abs=1e-9), approx(0.75)
    ), "a turned follower does not fly toward its leader"


def test_keeps_every_drone_after_a_move():
    assert len(
        Flock(
            (
                Drone(Body(Vector(1.3, 0.2), 0.0, Vector(0.0, 0.0), 0.0), Trail((), 5), False),
                Drone(Body(Vector(-0.6, 0.9), 0.0, Vector(0.0, 0.0), 0.0), Trail((), 5), True),
                Drone(Body(Vector(0.1, -1.4), 0.0, Vector(0.0, 0.0), 0.0), Trail((), 5), False),
            )
        )
        .moved(
            Command(Vector(2.0, 0.0), 0.0),
            Instinct(
                Cloud(Spring(1.2, 4.0, 0.5, 1.0), Spring(1.2, 4.0, 1.5, 1.5), 6),
                Limits(2.0, 4.0, 1.8, 8.0),
            ),
            Limits(2.0, 4.0, 1.8, 8.0),
            0.5,
        )
        .drones
    ) == 3, "a flock loses a drone during a move"


def test_follows_the_leader_as_a_cloud():
    flock = reduce(
        lambda cloud, frame: cloud.moved(
            Command(Vector(2.0 if frame < 360 else 0.0, 0.0), 0.0),
            Instinct(
                Cloud(Spring(1.2, 4.0, 0.5, 1.0), Spring(1.2, 4.0, 1.5, 1.5), 6),
                Limits(2.0, 4.0, 1.8, 8.0),
            ),
            Limits(2.0, 4.0, 1.8, 8.0),
            1.0 / 60,
        ),
        range(960),
        Flock(
            tuple(
                Drone(Body(place, 0.0, Vector(0.0, 0.0), 0.0), Trail((), 2), index == 0)
                for index, place in enumerate(Muster(8, 1.2).places())
            )
        ),
    )
    assert max(
        drone.body.position.minus(flock.leader().body.position).length()
        for drone in flock.drones
    ) < 2.5, "the cloud does not gather around the leader after a flight"


def test_cannot_let_two_drones_stick_together_in_flight():
    assert min(
        one.body.position.minus(other.body.position).length()
        for flock in accumulate(
            range(840),
            lambda cloud, frame: cloud.moved(
                Command(
                    Vector(
                        2.0 if frame < 360 else -2.0 if 540 <= frame < 720 else 0.0, 0.0
                    ),
                    0.0,
                ),
                Instinct(
                    Cloud(Spring(1.2, 4.0, 0.5, 1.0), Spring(1.2, 4.0, 1.5, 1.5), 6),
                    Limits(2.0, 4.0, 1.8, 8.0),
                ),
                Limits(2.0, 4.0, 1.8, 8.0),
                1.0 / 60,
            ),
            initial=Flock(
                tuple(
                    Drone(Body(place, 0.0, Vector(0.0, 0.0), 0.0), Trail((), 2), index == 0)
                    for index, place in enumerate(Muster(8, 1.2).places())
                )
            ),
        )
        for one, other in combinations(flock.drones, 2)
    ) > 0.5, "two drones come closer than two hard bubbles"


def test_comes_to_rest_once_the_leader_hovers():
    assert max(
        drone.body.velocity.length()
        for drone in reduce(
            lambda cloud, frame: cloud.moved(
                Command(Vector(0.0, 0.0), 0.0),
                Instinct(
                    Cloud(Spring(1.2, 4.0, 0.5, 1.0), Spring(1.2, 4.0, 1.5, 1.5), 6),
                    Limits(2.0, 4.0, 1.8, 8.0),
                ),
                Limits(2.0, 4.0, 1.8, 8.0),
                1.0 / 60,
            ),
            range(900),
            Flock(
                tuple(
                    Drone(Body(place, 0.0, Vector(0.0, 0.0), 0.0), Trail((), 2), index == 0)
                    for index, place in enumerate(Muster(8, 1.2).places())
                )
            ),
        ).drones
    ) < 0.01, "the cloud keeps trembling around a hovering leader"
