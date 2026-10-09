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
from agent.vector import Vector


def test_flies_a_follower_after_its_leader():
    assert Mind(
        Instinct(
            Cloud(Spring(1.2, 4.0, 0.5, 1.0), Spring(1.2, 4.0, 1.5, 1.5), Spring(0.6, 8.0, 0.0, 0.0), 6),
            Limits(2.0, 4.0, 1.8, 8.0),
        ),
        Shield(Limits(2.0, 4.0, 1.8, 8.0), 0.25, 1.0 / 60),
        Tracker(1.0 / 60),
        False,
    ).command(
        Tracks((Track(0, Vector(2.2, 0.0), True, True),)),
        Senses(Motion(Vector(0.0, 0.0), 0.0), Signals((), (), ()), (), Command(Vector(0.0, 0.0), 0.0)),
    ).velocity == Vector(approx(1.5), approx(0.0)), "a follower does not fly after its leader"


def test_cannot_fly_a_follower_on_the_request_of_the_pilot():
    assert Mind(
        Instinct(
            Cloud(Spring(1.2, 4.0, 0.5, 1.0), Spring(1.2, 4.0, 1.5, 1.5), Spring(0.6, 8.0, 0.0, 0.0), 6),
            Limits(2.0, 4.0, 1.8, 8.0),
        ),
        Shield(Limits(2.0, 4.0, 1.8, 8.0), 0.25, 1.0 / 60),
        Tracker(1.0 / 60),
        False,
    ).command(
        Tracks(()),
        Senses(Motion(Vector(0.0, 0.0), 0.0), Signals((), (), ()), (), Command(Vector(-1.3, 0.7), 0.9)),
    ) == Command(Vector(approx(0.0), approx(0.0)), approx(0.0)), "a follower obeys the pilot"


def test_keeps_a_follower_clear_of_a_wall():
    assert Mind(
        Instinct(
            Cloud(Spring(1.2, 4.0, 0.5, 1.0), Spring(1.2, 4.0, 1.5, 1.5), Spring(0.6, 8.0, 0.0, 0.0), 6),
            Limits(2.0, 4.0, 1.8, 8.0),
        ),
        Shield(Limits(2.0, 4.0, 1.8, 8.0), 0.25, 1.0 / 60),
        Tracker(1.0 / 60),
        False,
    ).command(
        Tracks(()),
        Senses(Motion(Vector(0.0, 0.0), 0.0), Signals((), (), ()), (Vector(0.0, 0.5),), Command(Vector(0.0, 0.0), 0.0)),
    ).velocity == Vector(approx(0.0), approx(-1.6)), "a follower does not back away from a close wall"


def test_cannot_pull_a_follower_toward_a_leader_it_has_never_sighted():
    assert Mind(
        Instinct(
            Cloud(Spring(1.2, 4.0, 0.5, 1.0), Spring(1.2, 4.0, 1.5, 1.5), Spring(0.6, 8.0, 0.0, 0.0), 6),
            Limits(2.0, 4.0, 1.8, 8.0),
        ),
        Shield(Limits(2.0, 4.0, 1.8, 8.0), 0.25, 1.0 / 60),
        Tracker(1.0 / 60),
        False,
    ).command(
        Tracks((Track(0, Vector(5.0, 0.0), False, True),)),
        Senses(Motion(Vector(0.0, 0.0), 0.0), Signals((), (), ()), (), Command(Vector(0.0, 0.0), 0.0)),
    ).velocity == Vector(approx(0.0), approx(0.0)), "a follower flies toward a leader it cannot place"


def test_cannot_shove_a_follower_away_from_a_peer_it_has_never_sighted():
    assert Mind(
        Instinct(
            Cloud(Spring(1.2, 4.0, 0.5, 1.0), Spring(1.2, 4.0, 1.5, 1.5), Spring(0.6, 8.0, 0.0, 0.0), 6),
            Limits(2.0, 4.0, 1.8, 8.0),
        ),
        Shield(Limits(2.0, 4.0, 1.8, 8.0), 0.25, 1.0 / 60),
        Tracker(1.0 / 60),
        False,
    ).command(
        Tracks((Track(4, Vector(0.9, 0.0), False, False),)),
        Senses(Motion(Vector(0.0, 0.0), 0.0), Signals((), (), ()), (), Command(Vector(0.0, 0.0), 0.0)),
    ).velocity == Vector(approx(0.0), approx(0.0)), "a follower backs away from a peer it cannot place"


def test_slows_a_follower_near_a_neighbour_it_has_never_sighted():
    assert Mind(
        Instinct(
            Cloud(Spring(1.2, 4.0, 0.5, 1.0), Spring(1.2, 4.0, 1.5, 1.5), Spring(0.6, 8.0, 0.0, 0.0), 6),
            Limits(2.0, 4.0, 1.8, 8.0),
        ),
        Shield(Limits(2.0, 4.0, 1.8, 8.0), 0.25, 1.0 / 60),
        Tracker(1.0 / 60),
        False,
    ).command(
        Tracks((Track(0, Vector(9.0, 0.0), True, True), Track(4, Vector(0.7, 0.0), False, False))),
        Senses(Motion(Vector(0.0, 0.0), 0.0), Signals((), (), ()), (), Command(Vector(0.0, 0.0), 0.0)),
    ).velocity == Vector(approx(0.6325, abs=1e-4), approx(0.0)), "a follower does not slow down near a neighbour it cannot place"


def test_stops_a_follower_two_margins_from_a_neighbour_it_has_never_sighted():
    assert Mind(
        Instinct(
            Cloud(Spring(1.2, 4.0, 0.5, 1.0), Spring(1.2, 4.0, 1.5, 1.5), Spring(0.6, 8.0, 0.0, 0.0), 6),
            Limits(2.0, 4.0, 1.8, 8.0),
        ),
        Shield(Limits(2.0, 4.0, 1.8, 8.0), 0.25, 1.0 / 60),
        Tracker(1.0 / 60),
        False,
    ).command(
        Tracks((Track(0, Vector(9.0, 0.0), True, True), Track(4, Vector(0.5, 0.0), False, False))),
        Senses(Motion(Vector(0.0, 0.0), 0.0), Signals((), (), ()), (), Command(Vector(0.0, 0.0), 0.0)),
    ).velocity == Vector(approx(0.0), approx(0.0)), "a follower keeps flying two margins from a neighbour it cannot place"


def test_flies_a_leader_on_the_request_of_the_pilot():
    assert Mind(
        Instinct(
            Cloud(Spring(1.2, 4.0, 0.5, 1.0), Spring(1.2, 4.0, 1.5, 1.5), Spring(0.6, 8.0, 0.0, 0.0), 6),
            Limits(2.0, 4.0, 1.8, 8.0),
        ),
        Shield(Limits(2.0, 4.0, 1.8, 8.0), 0.25, 1.0 / 60),
        Tracker(1.0 / 60),
        True,
    ).command(
        Tracks(()),
        Senses(Motion(Vector(0.0, 0.0), 0.0), Signals((), (), ()), (), Command(Vector(-1.3, 0.7), 0.9)),
    ) == Command(Vector(approx(-1.3), approx(0.7)), approx(0.9)), "a leader does not obey the pilot"


def test_cannot_pull_a_leader_toward_its_followers():
    assert Mind(
        Instinct(
            Cloud(Spring(1.2, 4.0, 0.5, 1.0), Spring(1.2, 4.0, 1.5, 1.5), Spring(0.6, 8.0, 0.0, 0.0), 6),
            Limits(2.0, 4.0, 1.8, 8.0),
        ),
        Shield(Limits(2.0, 4.0, 1.8, 8.0), 0.25, 1.0 / 60),
        Tracker(1.0 / 60),
        True,
    ).command(
        Tracks((Track(1, Vector(2.2, 0.0), True, False), Track(2, Vector(0.0, 0.4), True, False))),
        Senses(Motion(Vector(0.0, 0.0), 0.0), Signals((), (), ()), (), Command(Vector(0.0, 0.0), 0.0)),
    ).velocity == Vector(approx(0.0), approx(0.0)), "a leader is moved by its followers"


def test_cannot_fly_a_leader_into_a_wall():
    assert Mind(
        Instinct(
            Cloud(Spring(1.2, 4.0, 0.5, 1.0), Spring(1.2, 4.0, 1.5, 1.5), Spring(0.6, 8.0, 0.0, 0.0), 6),
            Limits(2.0, 4.0, 1.8, 8.0),
        ),
        Shield(Limits(2.0, 4.0, 1.8, 8.0), 0.25, 1.0 / 60),
        Tracker(1.0 / 60),
        True,
    ).command(
        Tracks(()),
        Senses(Motion(Vector(0.0, 0.0), 0.0), Signals((), (), ()), (Vector(0.25, 0.0),), Command(Vector(2.0, 0.0), 0.0)),
    ).velocity == Vector(approx(0.0), approx(0.0)), "a leader is flown into a wall"


def test_brakes_a_leader_by_its_own_velocity():
    assert Mind(
        Instinct(
            Cloud(Spring(1.2, 4.0, 0.5, 1.0), Spring(1.2, 4.0, 1.5, 1.5), Spring(0.6, 8.0, 0.0, 0.0), 6),
            Limits(2.0, 2.0, 1.8, 8.0),
        ),
        Shield(Limits(2.0, 2.0, 1.8, 8.0), 0.25, 1.0 / 60),
        Tracker(1.0 / 60),
        True,
    ).command(
        Tracks(()),
        Senses(Motion(Vector(2.0, 0.0), 0.0), Signals((), (), ()), (Vector(0.75, 0.0),), Command(Vector(0.0, 2.0), 0.0)),
    ).velocity == Vector(approx(1.0), approx(0.0)), "a leader closing on a wall too fast does not brake first"


def test_slows_a_leader_near_a_neighbour_it_has_never_sighted():
    assert Mind(
        Instinct(
            Cloud(Spring(1.2, 4.0, 0.5, 1.0), Spring(1.2, 4.0, 1.5, 1.5), Spring(0.6, 8.0, 0.0, 0.0), 6),
            Limits(2.0, 4.0, 1.8, 8.0),
        ),
        Shield(Limits(2.0, 4.0, 1.8, 8.0), 0.25, 1.0 / 60),
        Tracker(1.0 / 60),
        True,
    ).command(
        Tracks((Track(4, Vector(0.7, 0.0), False, False),)),
        Senses(Motion(Vector(0.0, 0.0), 0.0), Signals((), (), ()), (), Command(Vector(0.0, -2.0), 0.4)),
    ) == Command(Vector(approx(0.0), approx(-0.6325, abs=1e-4)), approx(0.4)), "a leader does not slow down near a neighbour it cannot place"


def test_takes_the_lead():
    assert Mind(
        Instinct(
            Cloud(Spring(1.2, 4.0, 0.5, 1.0), Spring(1.2, 4.0, 1.5, 1.5), Spring(0.6, 8.0, 0.0, 0.0), 6),
            Limits(2.0, 4.0, 1.8, 8.0),
        ),
        Shield(Limits(2.0, 4.0, 1.8, 8.0), 0.25, 1.0 / 60),
        Tracker(1.0 / 60),
        False,
    ).led(True).command(
        Tracks(()),
        Senses(Motion(Vector(0.0, 0.0), 0.0), Signals((), (), ()), (), Command(Vector(-1.3, 0.7), 0.0)),
    ).velocity == Vector(approx(-1.3), approx(0.7)), "a mind that takes the lead does not obey the pilot"


def test_gives_the_lead_away():
    assert Mind(
        Instinct(
            Cloud(Spring(1.2, 4.0, 0.5, 1.0), Spring(1.2, 4.0, 1.5, 1.5), Spring(0.6, 8.0, 0.0, 0.0), 6),
            Limits(2.0, 4.0, 1.8, 8.0),
        ),
        Shield(Limits(2.0, 4.0, 1.8, 8.0), 0.25, 1.0 / 60),
        Tracker(1.0 / 60),
        True,
    ).led(False).command(
        Tracks(()),
        Senses(Motion(Vector(0.0, 0.0), 0.0), Signals((), (), ()), (), Command(Vector(-1.3, 0.7), 0.0)),
    ).velocity == Vector(approx(0.0), approx(0.0)), "a mind that gives the lead away still obeys the pilot"


def test_remembers_a_neighbour_it_is_told_of():
    assert Mind(
        Instinct(
            Cloud(Spring(1.2, 4.0, 0.5, 1.0), Spring(1.2, 4.0, 1.5, 1.5), Spring(0.6, 8.0, 0.0, 0.0), 6),
            Limits(2.0, 4.0, 1.8, 8.0),
        ),
        Shield(Limits(2.0, 4.0, 1.8, 8.0), 0.25, 1.0 / 60),
        Tracker(1.0 / 60),
        False,
    ).recalled(
        Tracks(()),
        Senses(Motion(Vector(0.0, 0.0), 0.0), Signals((Range(3, 2.5),), (Bearing(3, 0.0),), (Role(3, True),)), (), Command(Vector(0.0, 0.0), 0.0)),
    ) == Tracks((Track(3, Vector(approx(2.5), approx(0.0)), True, True),)), "a mind does not remember a neighbour it is told of"


def test_remembers_the_same_whether_it_leads_or_follows():
    assert Mind(
        Instinct(
            Cloud(Spring(1.2, 4.0, 0.5, 1.0), Spring(1.2, 4.0, 1.5, 1.5), Spring(0.6, 8.0, 0.0, 0.0), 6),
            Limits(2.0, 4.0, 1.8, 8.0),
        ),
        Shield(Limits(2.0, 4.0, 1.8, 8.0), 0.25, 1.0 / 60),
        Tracker(1.0 / 60),
        True,
    ).recalled(
        Tracks(()),
        Senses(Motion(Vector(0.0, 0.0), 0.0), Signals((Range(3, 2.5),), (), ()), (), Command(Vector(0.0, 0.0), 0.0)),
    ).blind() == (approx(2.5),), "a leader does not remember a neighbour it is told of"


def test_asks_the_same_of_a_follower_whichever_way_it_faces():
    wanted = (
        Mind(
        Instinct(
            Cloud(Spring(1.2, 4.0, 0.5, 1.0), Spring(1.2, 4.0, 1.5, 1.5), Spring(0.6, 8.0, 0.0, 0.0), 6),
            Limits(2.0, 4.0, 1.8, 8.0),
        ),
        Shield(Limits(2.0, 4.0, 1.8, 8.0), 0.25, 1.0 / 60),
        Tracker(1.0 / 60),
        False,
    )
        .command(
            Tracks((Track(0, Vector(2.2, 0.4), True, True), Track(1, Vector(-0.7, 0.5), True, False), Track(2, Vector(0.2, -1.9), True, False),)),
            Senses(Motion(Vector(0.3, -0.2), 0.0), Signals((), (), ()), (Vector(0.1, -0.5),), Command(Vector(0.0, 0.0), 0.0)),
        )
        .velocity.turned(1.1)
    )
    assert Mind(
        Instinct(
            Cloud(Spring(1.2, 4.0, 0.5, 1.0), Spring(1.2, 4.0, 1.5, 1.5), Spring(0.6, 8.0, 0.0, 0.0), 6),
            Limits(2.0, 4.0, 1.8, 8.0),
        ),
        Shield(Limits(2.0, 4.0, 1.8, 8.0), 0.25, 1.0 / 60),
        Tracker(1.0 / 60),
        False,
    ).command(
        Tracks((Track(0, Vector(2.2, 0.4).turned(1.1), True, True), Track(1, Vector(-0.7, 0.5).turned(1.1), True, False), Track(2, Vector(0.2, -1.9).turned(1.1), True, False),)),
        Senses(Motion(Vector(0.3, -0.2).turned(1.1), 0.0), Signals((), (), ()), (Vector(0.1, -0.5).turned(1.1),), Command(Vector(0.0, 0.0).turned(1.1), 0.0)),
    ).velocity == Vector(
        approx(wanted.x), approx(wanted.y)
    ), "a follower asks for something else when all it knows is turned"


def test_asks_the_same_of_a_leader_whichever_way_it_faces():
    wanted = (
        Mind(
        Instinct(
            Cloud(Spring(1.2, 4.0, 0.5, 1.0), Spring(1.2, 4.0, 1.5, 1.5), Spring(0.6, 8.0, 0.0, 0.0), 6),
            Limits(2.0, 4.0, 1.8, 8.0),
        ),
        Shield(Limits(2.0, 4.0, 1.8, 8.0), 0.25, 1.0 / 60),
        Tracker(1.0 / 60),
        True,
    )
        .command(
            Tracks((Track(1, Vector(-0.7, 0.5), True, False),)),
            Senses(Motion(Vector(1.6, 0.3), 0.0), Signals((), (), ()), (Vector(0.4, 0.1), Vector(-0.2, 0.6),), Command(Vector(1.8, -0.6), 0.0)),
        )
        .velocity.turned(-2.3)
    )
    assert Mind(
        Instinct(
            Cloud(Spring(1.2, 4.0, 0.5, 1.0), Spring(1.2, 4.0, 1.5, 1.5), Spring(0.6, 8.0, 0.0, 0.0), 6),
            Limits(2.0, 4.0, 1.8, 8.0),
        ),
        Shield(Limits(2.0, 4.0, 1.8, 8.0), 0.25, 1.0 / 60),
        Tracker(1.0 / 60),
        True,
    ).command(
        Tracks((Track(1, Vector(-0.7, 0.5).turned(-2.3), True, False),)),
        Senses(Motion(Vector(1.6, 0.3).turned(-2.3), 0.0), Signals((), (), ()), (Vector(0.4, 0.1).turned(-2.3), Vector(-0.2, 0.6).turned(-2.3),), Command(Vector(1.8, -0.6).turned(-2.3), 0.0)),
    ).velocity == Vector(
        approx(wanted.x), approx(wanted.y)
    ), "a leader asks for something else when all it knows is turned"
