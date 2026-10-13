from random import uniform

from pytest import approx

from agent.command import Command
from agent.vector import Vector
from autopilot.attitude import Attitude
from autopilot.target import Target


def test_keeps_the_speed_along_the_nose():
    forward = uniform(-3.0, 3.0)
    assert Target(
        Command(Vector(forward, uniform(-3.0, 3.0)), uniform(-2.0, 2.0))
    ).forward() == approx(forward), "the speed along the nose does not stay"


def test_turns_the_speed_to_the_left_into_one_to_the_right():
    left = uniform(-3.0, 3.0)
    assert Target(
        Command(Vector(uniform(-3.0, 3.0), left), uniform(-2.0, 2.0))
    ).right() == approx(-left), "the speed to the left does not change sign"


def test_turns_the_spin_into_an_opposite_yaw_rate():
    spin = uniform(-2.0, 2.0)
    assert Target(
        Command(Vector(uniform(-3.0, 3.0), uniform(-3.0, 3.0)), spin)
    ).rate() == approx(-spin), "the spin does not change sign"


def test_asks_for_the_yaw_rate_that_reads_back_as_the_spin():
    spin = uniform(-2.0, 2.0)
    assert Attitude(
        uniform(-3.0, 3.0),
        Target(Command(Vector(uniform(-3.0, 3.0), uniform(-3.0, 3.0)), spin)).rate(),
    ).spin() == approx(spin), "an obeyed yaw rate does not read back as the spin"
