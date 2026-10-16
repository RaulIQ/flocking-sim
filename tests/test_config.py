from random import choice

from pytest import approx

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


def test_makes_the_pillars_as_wide_as_the_soft_bubble_of_a_drone():
    frame = frames()[choice(("freestyle", "iris"))]
    assert frame.barrier.walls()[0].radius == frame.swarm.bubbles.soft, "a pillar is not as wide as the soft bubble"


def test_leaves_one_and_a_half_soft_bubbles_between_the_pillars():
    frame = frames()[choice(("freestyle", "iris"))]
    lower, upper = frame.barrier.walls()
    assert upper.nearest(lower.centre).minus(lower.nearest(upper.centre)).length() == approx(
        3.0 * frame.swarm.bubbles.soft
    ), "the pillars do not leave one and a half soft bubbles between them"
