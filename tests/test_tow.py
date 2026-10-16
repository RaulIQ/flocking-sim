from random import uniform

from pytest import approx

from agent.bond import Bond
from agent.neighbour import Neighbour
from agent.tow import Tow
from agent.tuning import Limits, Rope, Spring, Wedge
from agent.vector import Vector
from agent.wings import Wings


def rope():
    return Rope(Spring(1.2, 1.0, 0.4, 1.5), Wedge(0.8, 4.0, 0.6, 0.6), 1.5, 2.0)


def tow(turn=0.0):
    return Tow(rope(), Limits(2.0, 4.0, 1.8, 8.0), turn)


def test_carries_a_follower_behind_along_with_its_leader():
    velocity = Vector(uniform(0.5, 2.0), 0.0)
    assert tow().carry(Neighbour(Vector(1.0, 0.3), velocity, True)) == velocity, (
        "a follower behind its leader is not carried along with it"
    )


def test_carries_a_follower_beside_the_way_along_with_its_leader():
    velocity = Vector(1.0, 0.0)
    assert tow().carry(Neighbour(Vector(-1.0, -uniform(1.3, 3.0)), velocity, True)) == velocity, (
        "a follower beside the way of its leader is not carried along with it"
    )


def test_carries_a_follower_far_ahead_along_with_its_leader():
    velocity = Vector(1.0, 0.0)
    assert tow().carry(Neighbour(Vector(-uniform(4.5, 6.0), -0.2), velocity, True)) == velocity, (
        "a follower far ahead of its leader is not carried along with it"
    )


def test_cannot_carry_a_follower_in_the_way_ahead_of_its_leader():
    assert tow().carry(
        Neighbour(Vector(-uniform(0.5, 1.5), -0.2), Vector(1.0, 0.0), True)
    ).x == approx(0.0), "a follower in the way is carried ahead of its leader"


def test_steps_a_follower_in_the_way_to_its_own_side():
    assert tow().carry(
        Neighbour(Vector(-1.0, -uniform(0.05, 1.0)), Vector(1.0, 0.0), True)
    ).y > 0.0, "a follower in the way does not step to its own side"


def test_steps_a_follower_dead_ahead_to_one_side():
    assert tow().carry(
        Neighbour(Vector(-1.0, 0.0), Vector(1.0, 0.0), True)
    ).length() > 0.0, "a follower dead ahead of its leader does not step aside"


def test_steps_aside_at_least_as_fast_as_the_leader_comes():
    speed = uniform(0.5, 1.5)
    assert tow().carry(
        Neighbour(Vector(-1.0, -0.3), Vector(speed, 0.0), True)
    ).length() >= speed, "a follower steps aside slower than its leader comes"


def test_cannot_step_aside_faster_than_a_drone_flies():
    assert tow().carry(
        Neighbour(Vector(-1.0, -0.01), Vector(1.9, 0.0), True)
    ).length() <= 2.0 + 1e-9, "a follower steps aside faster than a drone flies"


def test_lets_go_of_a_follower_in_the_way():
    assert tow().hold(Neighbour(Vector(-0.8, -0.2), Vector(1.0, 0.0), True)) == Vector(
        0.0, 0.0
    ), "the spring still holds a follower in the way of its leader"


def test_pulls_a_follower_behind_a_flying_leader_toward_its_wedge():
    leader = Neighbour(Vector(uniform(1.5, 3.0), uniform(-1.0, 1.0)), Vector(1.0, 0.0), True)
    place = Wings(rope(), Limits(2.0, 4.0, 1.8, 8.0), 0.0).place(leader)
    assert tow().hold(leader) == place.times(
        0.6 * min(place.length(), 1.5) / place.length()
    ), "a follower behind a flying leader is not pulled toward its wedge"


def test_finds_a_follower_on_the_bent_way_of_a_turning_leader_in_the_way():
    radius = uniform(1.0, 3.0)
    assert tow(1.5 / radius).blocks(
        Neighbour(Vector(-radius, -radius), Vector(1.5, 0.0), True)
    ), "a follower on the bent way of its leader is not in the way"


def test_lets_a_follower_ahead_of_a_leader_turning_away_stay_out_of_the_way():
    assert not tow(-1.8).blocks(
        Neighbour(Vector(-3.0, 0.0), Vector(2.0, 0.0), True)
    ), "a follower ahead of a leader turning away from it is in the way"


def test_pushes_a_follower_out_of_the_circle_of_a_leader_turning_left():
    assert tow(1.0).carry(
        Neighbour(Vector(1.5, -0.5), Vector(1.5, 0.0), True)
    ).y < 0.0, "a follower inside the circle of a leader turning left is not pushed out"


def test_lets_go_of_a_follower_inside_the_circle_of_a_turning_leader():
    assert tow(1.0).hold(
        Neighbour(Vector(1.5, -0.5), Vector(1.5, 0.0), True)
    ) == Vector(0.0, 0.0), "the wedge still pulls a follower inside the circle of a turning leader"


def test_holds_a_follower_of_a_hovering_leader_by_its_spring():
    offset = Vector(uniform(-3.0, 3.0), uniform(-3.0, 3.0))
    assert tow().hold(Neighbour(offset, Vector(0.0, 0.0), True)) == Bond(
        Spring(1.2, 1.0, 0.4, 1.5)
    ).velocity(offset), "the spring does not hold a follower of a hovering leader"
