from functools import reduce
from math import pi

from pytest import approx

from agent.command import Command
from agent.senses import Motion, Senses
from agent.signals import Bearing, Range, Role, Signals
from agent.tracker import Tracker
from agent.tracks import Track, Tracks
from agent.tuning import Limits
from agent.vector import Vector
from simulator.body import Body


def test_places_a_neighbour_by_its_range_and_bearing():
    assert Tracker(0.5).after(
        Tracks(()),
        Senses(
            Motion(Vector(0.0, 0.0), 0.0),
            Signals((Range(3, 2.5),), (Bearing(3, pi / 2),), ()),
            (),
            Command(Vector(0.0, 0.0), 0.0),
        ),
    ) == Tracks(
        (Track(3, Vector(approx(0.0, abs=1e-9), approx(2.5)), True, False),)
    ), "a tracker does not place a neighbour by its range and bearing"


def test_learns_who_leads_over_the_radio():
    assert Tracker(0.5).after(
        Tracks(()),
        Senses(
            Motion(Vector(0.0, 0.0), 0.0),
            Signals((Range(3, 2.5),), (Bearing(3, 0.0),), (Role(3, True),)),
            (),
            Command(Vector(0.0, 0.0), 0.0),
        ),
    ).items[0].leader, "a tracker does not learn who leads over the radio"


def test_cannot_give_a_direction_to_a_neighbour_it_has_only_ranged():
    assert not Tracker(0.5).after(
        Tracks(()),
        Senses(
            Motion(Vector(0.0, 0.0), 0.0),
            Signals((Range(3, 2.5),), (), ()),
            (),
            Command(Vector(0.0, 0.0), 0.0),
        ),
    ).items[0].sighted, "a tracker gives a direction to a neighbour it has only ranged"


def test_remembers_how_far_a_neighbour_it_has_only_ranged_is():
    assert Tracker(0.5).after(
        Tracks(()),
        Senses(
            Motion(Vector(0.0, 0.0), 0.0),
            Signals((Range(3, 2.5),), (), ()),
            (),
            Command(Vector(0.0, 0.0), 0.0),
        ),
    ).blind() == (approx(2.5),), "a tracker forgets how far a ranged neighbour is"


def test_cannot_place_a_neighbour_it_has_sighted_but_never_ranged():
    assert Tracker(0.5).after(
        Tracks(()),
        Senses(
            Motion(Vector(0.0, 0.0), 0.0),
            Signals((), (Bearing(3, 0.4),), ()),
            (),
            Command(Vector(0.0, 0.0), 0.0),
        ),
    ) == Tracks(()), "a tracker places a neighbour without knowing how far it is"


def test_gives_a_direction_on_the_first_sighting():
    assert Tracker(0.5).after(
        Tracks((Track(3, Vector(2.5, 0.0), False, False),)),
        Senses(
            Motion(Vector(0.0, 0.0), 0.0),
            Signals((), (Bearing(3, pi),), ()),
            (),
            Command(Vector(0.0, 0.0), 0.0),
        ),
    ) == Tracks(
        (Track(3, Vector(approx(-2.5), approx(0.0, abs=1e-9)), True, False),)
    ), "a tracker does not give a direction on the first sighting"


def test_carries_a_neighbour_along_with_its_own_flight():
    assert Tracker(0.5).after(
        Tracks((Track(3, Vector(2.0, 0.7), True, False),)),
        Senses(
            Motion(Vector(1.2, -0.4), 0.0),
            Signals((), (), ()),
            (),
            Command(Vector(0.0, 0.0), 0.0),
        ),
    ).items[0].offset == Vector(
        approx(1.4), approx(0.9)
    ), "a tracker does not carry a neighbour along with its own flight"


def test_carries_a_neighbour_along_with_its_own_turn():
    assert Tracker(0.5).after(
        Tracks((Track(3, Vector(2.0, 0.0), True, False),)),
        Senses(
            Motion(Vector(0.0, 0.0), pi),
            Signals((), (), ()),
            (),
            Command(Vector(0.0, 0.0), 0.0),
        ),
    ).items[0].offset == Vector(
        approx(0.0, abs=1e-9), approx(-2.0)
    ), "a tracker does not carry a neighbour along with its own turn"


def test_cannot_carry_a_neighbour_it_has_never_sighted():
    assert Tracker(0.5).after(
        Tracks((Track(3, Vector(2.5, 0.0), False, False),)),
        Senses(
            Motion(Vector(1.2, -0.4), 0.9),
            Signals((), (), ()),
            (),
            Command(Vector(0.0, 0.0), 0.0),
        ),
    ).blind() == (approx(2.5),), "a tracker moves a neighbour it cannot place"


def test_corrects_the_distance_by_a_range_and_keeps_the_direction():
    assert Tracker(0.5).after(
        Tracks((Track(3, Vector(0.0, 2.0), True, False),)),
        Senses(
            Motion(Vector(0.0, 0.0), 0.0),
            Signals((Range(3, 3.2),), (), ()),
            (),
            Command(Vector(0.0, 0.0), 0.0),
        ),
    ).items[0].offset == Vector(
        approx(0.0), approx(3.2)
    ), "a range does not correct the distance alone"


def test_corrects_the_direction_by_a_bearing_and_keeps_the_distance():
    assert Tracker(0.5).after(
        Tracks((Track(3, Vector(2.0, 0.0), True, False),)),
        Senses(
            Motion(Vector(0.0, 0.0), 0.0),
            Signals((), (Bearing(3, pi / 2),), ()),
            (),
            Command(Vector(0.0, 0.0), 0.0),
        ),
    ).items[0].offset == Vector(
        approx(0.0, abs=1e-9), approx(2.0)
    ), "a bearing does not correct the direction alone"


def test_keeps_the_role_of_a_neighbour_while_the_radio_is_silent():
    assert Tracker(0.5).after(
        Tracks((Track(3, Vector(2.0, 0.0), True, True),)),
        Senses(
            Motion(Vector(0.0, 0.0), 0.0),
            Signals((Range(3, 2.0),), (), ()),
            (),
            Command(Vector(0.0, 0.0), 0.0),
        ),
    ).items[0].leader, "a silent radio takes the lead away from a neighbour"


def test_takes_the_lead_away_when_the_radio_says_so():
    assert not Tracker(0.5).after(
        Tracks((Track(3, Vector(2.0, 0.0), True, True),)),
        Senses(
            Motion(Vector(0.0, 0.0), 0.0),
            Signals((), (), (Role(3, False),)),
            (),
            Command(Vector(0.0, 0.0), 0.0),
        ),
    ).items[0].leader, "a tracker keeps a leader the radio has demoted"


def test_keeps_a_track_for_every_neighbour():
    assert [
        track.tag
        for track in Tracker(0.5)
        .after(
            Tracks((Track(8, Vector(2.0, 0.0), True, False),)),
            Senses(
                Motion(Vector(0.0, 0.0), 0.0),
                Signals((Range(5, 1.0), Range(2, 3.0)), (), ()),
                (),
                Command(Vector(0.0, 0.0), 0.0),
            ),
        )
        .items
    ] == [2, 5, 8], "a tracker does not keep a track for every neighbour"


def test_follows_a_still_neighbour_through_its_own_flight_with_no_new_measurements():
    step = lambda body: body.moved(
        Command(Vector(1.6, -0.7), 1.1), Limits(2.0, 4.0, 1.8, 8.0), 1.0 / 60
    )
    flown = reduce(
        lambda state, frame: (
            step(state[0]),
            Tracker(1.0 / 60).after(
                state[1],
                Senses(
                    Motion(
                        step(state[0]).velocity.turned(-step(state[0]).heading),
                        step(state[0]).spin,
                    ),
                    Signals((), (), ()),
                    (),
                    Command(Vector(0.0, 0.0), 0.0),
                ),
            ),
        ),
        range(300),
        (
            Body(Vector(0.4, -0.7), 0.3, Vector(0.0, 0.0), 0.0),
            Tracks(
                (
                    Track(
                        3,
                        Vector(5.0, 2.0).minus(Vector(0.4, -0.7)).turned(-0.3),
                        True,
                        False,
                    ),
                )
            ),
        ),
    )
    truth = Vector(5.0, 2.0).minus(flown[0].position).turned(-flown[0].heading)
    assert flown[1].items[0].offset == Vector(
        approx(truth.x, abs=1e-6), approx(truth.y, abs=1e-6)
    ), "a tracker loses a still neighbour during its own flight and turn"
