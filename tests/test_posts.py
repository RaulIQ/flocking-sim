from random import uniform

from pytest import approx

from agent.vector import Vector
from simulator.posts import Posts


def test_stands_two_pillars():
    assert len(Posts(4.0, 1.8, 0.6).walls()) == 2, "the posts are not two pillars"


def test_leaves_the_gap_between_the_sides_of_the_pillars():
    gap = uniform(1.0, 3.0)
    lower, upper = Posts(4.0, gap, 0.6).walls()
    assert upper.nearest(lower.centre).minus(
        lower.nearest(upper.centre)
    ).length() == approx(gap), "the posts do not leave the gap between their sides"


def test_stands_the_pillars_across_the_way():
    across = uniform(2.0, 6.0)
    assert [pillar.centre.x for pillar in Posts(across, 1.8, 0.6).walls()] == [
        approx(across),
        approx(across),
    ], "the pillars do not stand across the way"


def test_centres_the_gap_on_the_axis():
    lower, upper = Posts(4.0, uniform(1.0, 3.0), uniform(0.3, 1.0)).walls()
    assert lower.centre.y == approx(-upper.centre.y), "the gap between the posts is off the axis"


def test_counts_a_drone_beyond_the_pillars_as_passed():
    assert Posts(4.0, 1.8, 0.6).passed(
        Vector(uniform(4.01, 8.0), uniform(-3.0, 3.0))
    ), "a drone beyond the pillars does not count as passed"


def test_cannot_count_a_drone_short_of_the_pillars_as_passed():
    assert not Posts(4.0, 1.8, 0.6).passed(
        Vector(uniform(0.0, 3.99), uniform(-3.0, 3.0))
    ), "a drone short of the pillars counts as passed"
