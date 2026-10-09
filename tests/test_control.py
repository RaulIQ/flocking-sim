from collections import defaultdict

from pygame import K_DOWN, K_LEFT, K_RIGHT, K_UP, K_a, K_d, K_s, K_w
from pytest import approx

from config import Limits
from simulator.control import Pilot
from simulator.vector import Vector


def test_asks_to_fly_forward():
    assert Pilot(Limits(2.0, 4.0, 1.8, 6.0)).velocity(
        defaultdict(bool, {K_w: True})
    ) == Vector(approx(2.0), approx(0.0)), "the w key does not fly forward"


def test_asks_to_fly_backward():
    assert Pilot(Limits(2.0, 4.0, 1.8, 6.0)).velocity(
        defaultdict(bool, {K_s: True})
    ) == Vector(approx(-2.0), approx(0.0)), "the s key does not fly backward"


def test_asks_to_slide_left():
    assert Pilot(Limits(2.0, 4.0, 1.8, 6.0)).velocity(
        defaultdict(bool, {K_a: True})
    ) == Vector(approx(0.0), approx(2.0)), "the a key does not slide left"


def test_asks_to_slide_right():
    assert Pilot(Limits(2.0, 4.0, 1.8, 6.0)).velocity(
        defaultdict(bool, {K_d: True})
    ) == Vector(approx(0.0), approx(-2.0)), "the d key does not slide right"


def test_flies_forward_on_the_up_arrow():
    assert Pilot(Limits(2.0, 4.0, 1.8, 6.0)).velocity(
        defaultdict(bool, {K_UP: True})
    ) == Vector(approx(2.0), approx(0.0)), "the up arrow does not fly forward"


def test_flies_backward_on_the_down_arrow():
    assert Pilot(Limits(2.0, 4.0, 1.8, 6.0)).velocity(
        defaultdict(bool, {K_DOWN: True})
    ) == Vector(approx(-2.0), approx(0.0)), "the down arrow does not fly backward"


def test_slides_left_on_the_left_arrow():
    assert Pilot(Limits(2.0, 4.0, 1.8, 6.0)).velocity(
        defaultdict(bool, {K_LEFT: True})
    ) == Vector(approx(0.0), approx(2.0)), "the left arrow does not slide left"


def test_slides_right_on_the_right_arrow():
    assert Pilot(Limits(2.0, 4.0, 1.8, 6.0)).velocity(
        defaultdict(bool, {K_RIGHT: True})
    ) == Vector(approx(0.0), approx(-2.0)), "the right arrow does not slide right"


def test_cannot_double_the_speed_with_a_letter_and_an_arrow():
    assert Pilot(Limits(2.0, 4.0, 1.8, 6.0)).velocity(
        defaultdict(bool, {K_w: True, K_UP: True})
    ) == Vector(approx(2.0), approx(0.0)), "a letter and an arrow together fly too fast"


def test_cannot_ask_for_more_than_the_top_speed_diagonally():
    assert Pilot(Limits(2.0, 4.0, 1.8, 6.0)).velocity(
        defaultdict(bool, {K_w: True, K_a: True})
    ).length() == approx(2.0), "a diagonal request beats the top speed"


def test_cannot_fly_with_two_opposite_keys_down():
    assert Pilot(Limits(2.0, 4.0, 1.8, 6.0)).velocity(
        defaultdict(bool, {K_w: True, K_s: True})
    ) == Vector(approx(0.0), approx(0.0)), "two opposite keys still fly the drone"


def test_cannot_ask_for_anything_with_no_keys_down():
    assert Pilot(Limits(2.0, 4.0, 1.8, 6.0)).velocity(defaultdict(bool)) == Vector(
        approx(0.0), approx(0.0)
    ), "an idle keyboard still asks to fly"
