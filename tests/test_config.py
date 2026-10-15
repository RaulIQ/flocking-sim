from random import choice

from config import copters, frames


def test_keeps_the_freestyle_frame_as_the_copters_fly():
    assert frames()["freestyle"] == copters(), "the freestyle frame does not fly the settings of the copters"


def test_covers_the_rotors_of_the_iris_with_its_hard_bubble():
    assert frames()["iris"].swarm.bubbles.hard > 0.355, "the hard bubble of the Iris does not cover its rotors"


def test_keeps_the_hard_bubble_inside_the_soft_one():
    frame = frames()[choice(("freestyle", "iris"))]
    assert frame.swarm.bubbles.hard < frame.swarm.bubbles.soft, "the hard bubble reaches beyond the soft one"


def test_keeps_the_hard_bubbles_apart_at_the_rest_distance():
    frame = frames()[choice(("freestyle", "iris"))]
    assert 2.0 * frame.swarm.bubbles.hard < frame.swarm.cloud.peers.rest, "two hard bubbles overlap at the rest distance"


def test_keeps_the_followers_of_the_iris_farther_from_its_leader():
    assert (
        frames()["iris"].swarm.cloud.leader.rest > frames()["freestyle"].swarm.cloud.leader.rest
    ), "the followers of the Iris keep no more room to give way to their leader"
