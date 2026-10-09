from pytest import approx

from agent.neighbour import Neighbour
from agent.tracks import Track, Tracks
from agent.vector import Vector


def test_names_the_neighbours_it_can_place():
    assert Tracks(
        (
            Track(4, Vector(1.5, -0.4), True, False),
            Track(7, Vector(2.0, 0.0), False, False),
            Track(9, Vector(-0.3, 2.2), True, True),
        )
    ).sighted() == (
        Neighbour(Vector(1.5, -0.4), False),
        Neighbour(Vector(-0.3, 2.2), True),
    ), "a memory does not name the neighbours it can place"


def test_tells_how_far_the_neighbours_it_cannot_place_are():
    assert Tracks(
        (
            Track(4, Vector(1.5, -0.4), True, False),
            Track(7, Vector(1.2, 0.0), False, False),
            Track(9, Vector(3.4, 0.0), False, True),
        )
    ).blind() == (
        approx(1.2),
        approx(3.4),
    ), "a memory does not tell how far its unplaced neighbours are"


def test_cannot_name_anybody_when_it_remembers_nothing():
    assert Tracks(()).sighted() == (), "an empty memory names a neighbour"
