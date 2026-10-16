from random import uniform

from pytest import approx

from agent.neighbour import Neighbour
from agent.sweep import Sweep
from agent.vector import Vector


def test_pushes_a_drone_out_of_the_circle_of_a_leader_turning_left():
    assert Sweep(Neighbour(Vector(0.0, -1.0), Vector(2.0, 0.0), True), 2.0 / uniform(1.5, 4.0)).exit(
        0.5
    ).y < 0.0, "a drone inside the circle of a leader turning left is not pushed out of it"


def test_pushes_a_drone_out_of_the_circle_of_a_leader_turning_right():
    assert Sweep(Neighbour(Vector(0.0, 1.0), Vector(2.0, 0.0), True), -2.0 / uniform(1.5, 4.0)).exit(
        0.5
    ).y > 0.0, "a drone inside the circle of a leader turning right is not pushed out of it"


def test_pushes_a_drone_as_far_as_the_widened_circle_reaches():
    clearance = uniform(0.2, 1.0)
    assert Sweep(Neighbour(Vector(0.0, -1.0), Vector(2.0, 0.0), True), 1.0).exit(
        clearance
    ).length() == approx(1.0 + clearance), "a drone is not pushed out to the edge of the widened circle"


def test_cannot_push_a_drone_outside_the_widened_circle():
    assert Sweep(Neighbour(Vector(0.0, uniform(0.6, 2.0)), Vector(2.0, 0.0), True), 1.0).exit(
        0.5
    ) == Vector(0.0, 0.0), "a drone outside the circle of its leader is pushed"


def test_cannot_push_a_drone_while_the_leader_flies_straight():
    assert Sweep(Neighbour(Vector(0.0, -uniform(0.5, 2.0)), Vector(2.0, 0.0), True), 0.0).exit(
        0.5
    ) == Vector(0.0, 0.0), "a drone is pushed while its leader flies straight"
