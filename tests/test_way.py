from math import pi
from random import uniform

from pytest import approx

from agent.neighbour import Neighbour
from agent.vector import Vector
from agent.way import Way


def test_finds_the_nearest_point_of_a_straight_way_beside_the_drone():
    side = uniform(0.2, 2.0)
    assert Way(Neighbour(Vector(-2.0, -side), Vector(1.3, 0.0), True), 0.0, 5.0).nearest() == Vector(
        approx(0.0), approx(-side)
    ), "the nearest point of a straight way is not beside the drone"


def test_measures_how_far_along_a_straight_way_the_drone_stands():
    ahead = uniform(0.5, 4.0)
    assert Way(Neighbour(Vector(-ahead, 0.4), Vector(1.0, 0.0), True), 0.0, 5.0).along() == approx(
        ahead
    ), "the drone does not stand as far along the straight way as it is ahead"


def test_cannot_put_a_drone_behind_its_leader_along_the_way():
    assert Way(
        Neighbour(Vector(uniform(0.5, 3.0), 0.3), Vector(1.0, 0.0), True), 0.0, 5.0
    ).along() == approx(0.0), "a drone behind its leader stands along its way"


def test_ends_a_straight_way_at_its_reach():
    reach = uniform(1.0, 3.0)
    assert Way(Neighbour(Vector(-5.0, 0.0), Vector(2.0, 0.0), True), 0.0, reach).nearest() == Vector(
        approx(reach - 5.0), approx(0.0)
    ), "a straight way runs past its reach"


def test_bends_the_way_of_a_leader_turning_left():
    radius = uniform(0.8, 4.0)
    assert Way(
        Neighbour(Vector(-radius, -radius), Vector(2.0, 0.0), True), 2.0 / radius, 10.0
    ).nearest() == Vector(approx(0.0), approx(0.0)), "the way of a leader turning left does not bend left"


def test_bends_the_way_of_a_leader_turning_right():
    radius = uniform(0.8, 4.0)
    assert Way(
        Neighbour(Vector(-radius, radius), Vector(2.0, 0.0), True), -2.0 / radius, 10.0
    ).nearest() == Vector(approx(0.0), approx(0.0)), "the way of a leader turning right does not bend right"


def test_measures_how_far_along_a_bent_way_the_drone_stands():
    radius = uniform(0.8, 4.0)
    assert Way(
        Neighbour(Vector(-radius, -radius), Vector(2.0, 0.0), True), 2.0 / radius, 10.0
    ).along() == approx(pi * radius / 2.0), "the drone does not stand a quarter turn along the bent way"


def test_ends_a_bent_way_at_its_reach():
    assert Way(
        Neighbour(Vector(-1.0, -1.0), Vector(2.0, 0.0), True), 2.0, pi / 4.0
    ).nearest() == Vector(approx(-1.0 + 2.0**-0.5), approx(-(2.0**-0.5))), "a bent way runs past its reach"
