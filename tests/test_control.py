from pygame import K_a, K_d, K_e, K_q, K_s, K_w
from pytest import approx

from config import Limits
from simulator.control import Pilot
from simulator.vector import Vector


def test_asks_to_fly_forward():
    assert Pilot(Limits(2.0, 4.0, 1.5, 6.0)).command(
        {K_w: True, K_s: False, K_a: False, K_d: False, K_q: False, K_e: False}
    ).velocity == Vector(approx(2.0), approx(0.0)), "the w key does not fly forward"


def test_asks_to_fly_backward():
    assert Pilot(Limits(2.0, 4.0, 1.5, 6.0)).command(
        {K_w: False, K_s: True, K_a: False, K_d: False, K_q: False, K_e: False}
    ).velocity == Vector(approx(-2.0), approx(0.0)), "the s key does not fly backward"


def test_asks_to_slide_left():
    assert Pilot(Limits(2.0, 4.0, 1.5, 6.0)).command(
        {K_w: False, K_s: False, K_a: True, K_d: False, K_q: False, K_e: False}
    ).velocity == Vector(approx(0.0), approx(2.0)), "the a key does not slide left"


def test_asks_to_slide_right():
    assert Pilot(Limits(2.0, 4.0, 1.5, 6.0)).command(
        {K_w: False, K_s: False, K_a: False, K_d: True, K_q: False, K_e: False}
    ).velocity == Vector(approx(0.0), approx(-2.0)), "the d key does not slide right"


def test_cannot_ask_for_more_than_the_top_speed_diagonally():
    assert Pilot(Limits(2.0, 4.0, 1.5, 6.0)).command(
        {K_w: True, K_s: False, K_a: True, K_d: False, K_q: False, K_e: False}
    ).velocity.length() == approx(2.0), "a diagonal request beats the top speed"


def test_asks_to_turn_left():
    assert Pilot(Limits(2.0, 4.0, 1.5, 6.0)).command(
        {K_w: False, K_s: False, K_a: False, K_d: False, K_q: True, K_e: False}
    ).spin == approx(1.5), "the q key does not turn left"


def test_asks_to_turn_right():
    assert Pilot(Limits(2.0, 4.0, 1.5, 6.0)).command(
        {K_w: False, K_s: False, K_a: False, K_d: False, K_q: False, K_e: True}
    ).spin == approx(-1.5), "the e key does not turn right"


def test_cannot_ask_for_anything_with_no_keys_down():
    assert Pilot(Limits(2.0, 4.0, 1.5, 6.0)).command(
        {K_w: False, K_s: False, K_a: False, K_d: False, K_q: False, K_e: False}
    ).velocity == Vector(approx(0.0), approx(0.0)), "an idle keyboard still asks to fly"


def test_cannot_ask_to_turn_with_both_turn_keys_down():
    assert Pilot(Limits(2.0, 4.0, 1.5, 6.0)).command(
        {K_w: False, K_s: False, K_a: False, K_d: False, K_q: True, K_e: True}
    ).spin == approx(0.0), "two opposite turn keys still turn the drone"
