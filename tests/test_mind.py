from pytest import approx

from agent.command import Command
from agent.instinct import Instinct
from agent.mind import Mind
from agent.neighbour import Neighbour
from agent.senses import Senses
from agent.shield import Shield
from agent.vector import Vector
from config import Cloud, Limits, Spring


def test_flies_a_follower_after_its_leader():
    assert Mind(
        Instinct(
            Cloud(Spring(1.2, 4.0, 0.5, 1.0), Spring(1.2, 4.0, 1.5, 1.5), Spring(0.6, 8.0, 0.0, 0.0), 6),
            Limits(2.0, 4.0, 1.8, 8.0),
        ),
        Shield(Limits(2.0, 4.0, 1.8, 8.0), 0.25, 1.0 / 60),
        False,
    ).command(
        Senses(
            Vector(0.0, 0.0),
            (Neighbour(Vector(2.2, 0.0), True),),
            (),
            Command(Vector(0.0, 0.0), 0.0),
        )
    ).velocity == Vector(
        approx(1.5), approx(0.0)
    ), "a follower does not fly after its leader"


def test_cannot_fly_a_follower_on_the_request_of_the_pilot():
    assert Mind(
        Instinct(
            Cloud(Spring(1.2, 4.0, 0.5, 1.0), Spring(1.2, 4.0, 1.5, 1.5), Spring(0.6, 8.0, 0.0, 0.0), 6),
            Limits(2.0, 4.0, 1.8, 8.0),
        ),
        Shield(Limits(2.0, 4.0, 1.8, 8.0), 0.25, 1.0 / 60),
        False,
    ).command(
        Senses(Vector(0.0, 0.0), (), (), Command(Vector(-1.3, 0.7), 0.9))
    ) == Command(
        Vector(approx(0.0), approx(0.0)), approx(0.0)
    ), "a follower obeys the pilot"


def test_keeps_a_follower_clear_of_a_wall():
    assert Mind(
        Instinct(
            Cloud(Spring(1.2, 4.0, 0.5, 1.0), Spring(1.2, 4.0, 1.5, 1.5), Spring(0.6, 8.0, 0.0, 0.0), 6),
            Limits(2.0, 4.0, 1.8, 8.0),
        ),
        Shield(Limits(2.0, 4.0, 1.8, 8.0), 0.25, 1.0 / 60),
        False,
    ).command(
        Senses(
            Vector(0.0, 0.0), (), (Vector(0.0, 0.5),), Command(Vector(0.0, 0.0), 0.0)
        )
    ).velocity == Vector(
        approx(0.0), approx(-1.6)
    ), "a follower does not back away from a close wall"


def test_flies_a_leader_on_the_request_of_the_pilot():
    assert Mind(
        Instinct(
            Cloud(Spring(1.2, 4.0, 0.5, 1.0), Spring(1.2, 4.0, 1.5, 1.5), Spring(0.6, 8.0, 0.0, 0.0), 6),
            Limits(2.0, 4.0, 1.8, 8.0),
        ),
        Shield(Limits(2.0, 4.0, 1.8, 8.0), 0.25, 1.0 / 60),
        True,
    ).command(
        Senses(Vector(0.0, 0.0), (), (), Command(Vector(-1.3, 0.7), 0.9))
    ) == Command(
        Vector(approx(-1.3), approx(0.7)), approx(0.9)
    ), "a leader does not obey the pilot"


def test_cannot_pull_a_leader_toward_its_followers():
    assert Mind(
        Instinct(
            Cloud(Spring(1.2, 4.0, 0.5, 1.0), Spring(1.2, 4.0, 1.5, 1.5), Spring(0.6, 8.0, 0.0, 0.0), 6),
            Limits(2.0, 4.0, 1.8, 8.0),
        ),
        Shield(Limits(2.0, 4.0, 1.8, 8.0), 0.25, 1.0 / 60),
        True,
    ).command(
        Senses(
            Vector(0.0, 0.0),
            (Neighbour(Vector(2.2, 0.0), False), Neighbour(Vector(0.0, 0.4), False)),
            (),
            Command(Vector(0.0, 0.0), 0.0),
        )
    ).velocity == Vector(
        approx(0.0), approx(0.0)
    ), "a leader is moved by its followers"


def test_cannot_fly_a_leader_into_a_wall():
    assert Mind(
        Instinct(
            Cloud(Spring(1.2, 4.0, 0.5, 1.0), Spring(1.2, 4.0, 1.5, 1.5), Spring(0.6, 8.0, 0.0, 0.0), 6),
            Limits(2.0, 4.0, 1.8, 8.0),
        ),
        Shield(Limits(2.0, 4.0, 1.8, 8.0), 0.25, 1.0 / 60),
        True,
    ).command(
        Senses(
            Vector(0.0, 0.0), (), (Vector(0.25, 0.0),), Command(Vector(2.0, 0.0), 0.0)
        )
    ).velocity == Vector(
        approx(0.0), approx(0.0)
    ), "a leader is flown into a wall"


def test_brakes_a_leader_by_its_own_velocity():
    assert Mind(
        Instinct(
            Cloud(Spring(1.2, 4.0, 0.5, 1.0), Spring(1.2, 4.0, 1.5, 1.5), Spring(0.6, 8.0, 0.0, 0.0), 6),
            Limits(2.0, 2.0, 1.8, 8.0),
        ),
        Shield(Limits(2.0, 2.0, 1.8, 8.0), 0.25, 1.0 / 60),
        True,
    ).command(
        Senses(
            Vector(2.0, 0.0), (), (Vector(0.75, 0.0),), Command(Vector(0.0, 2.0), 0.0)
        )
    ).velocity == Vector(
        approx(1.0), approx(0.0)
    ), "a leader closing on a wall too fast does not brake first"


def test_takes_the_lead():
    assert Mind(
        Instinct(
            Cloud(Spring(1.2, 4.0, 0.5, 1.0), Spring(1.2, 4.0, 1.5, 1.5), Spring(0.6, 8.0, 0.0, 0.0), 6),
            Limits(2.0, 4.0, 1.8, 8.0),
        ),
        Shield(Limits(2.0, 4.0, 1.8, 8.0), 0.25, 1.0 / 60),
        False,
    ).led(True).command(
        Senses(Vector(0.0, 0.0), (), (), Command(Vector(-1.3, 0.7), 0.0))
    ).velocity == Vector(
        approx(-1.3), approx(0.7)
    ), "a mind that takes the lead does not obey the pilot"


def test_gives_the_lead_away():
    assert Mind(
        Instinct(
            Cloud(Spring(1.2, 4.0, 0.5, 1.0), Spring(1.2, 4.0, 1.5, 1.5), Spring(0.6, 8.0, 0.0, 0.0), 6),
            Limits(2.0, 4.0, 1.8, 8.0),
        ),
        Shield(Limits(2.0, 4.0, 1.8, 8.0), 0.25, 1.0 / 60),
        True,
    ).led(False).command(
        Senses(Vector(0.0, 0.0), (), (), Command(Vector(-1.3, 0.7), 0.0))
    ).velocity == Vector(
        approx(0.0), approx(0.0)
    ), "a mind that gives the lead away still obeys the pilot"
