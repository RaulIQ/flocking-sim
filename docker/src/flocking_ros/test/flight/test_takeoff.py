from contextlib import suppress
import random

from fake_vehicle import FakeVehicle
from flocking_ros.flight.refusal import Refusal
from flocking_ros.flight.takeoff import Takeoff
from hamcrest import assert_that, calling, contains_exactly, empty, raises


def test_flies_guided_then_arms_then_ascends() -> None:
    steps: list[str] = []
    altitude = random.uniform(5.0, 10.0)
    Takeoff(FakeVehicle(frozenset(), steps), altitude).fly()
    assert_that(
        steps,
        contains_exactly('switch GUIDED', 'arm', f'ascend {altitude}'),
        'Takeoff did not fly its three steps in order'
    )


def test_does_not_arm_when_mode_is_refused() -> None:
    steps: list[str] = []
    with suppress(Refusal):
        Takeoff(FakeVehicle(frozenset({'switch'}), steps), random.uniform(5.0, 10.0)).fly()
    assert_that(steps, empty(), 'Takeoff did not stop after the refused mode')


def test_does_not_ascend_when_arming_is_refused() -> None:
    steps: list[str] = []
    with suppress(Refusal):
        Takeoff(FakeVehicle(frozenset({'arm'}), steps), random.uniform(5.0, 10.0)).fly()
    assert_that(
        steps,
        contains_exactly('switch GUIDED'),
        'Takeoff did not stop after the refused arming'
    )


def test_names_the_refused_step() -> None:
    assert_that(
        calling(
            Takeoff(FakeVehicle(frozenset({'arm'}), []), random.uniform(5.0, 10.0)).fly
        ).with_args(),
        raises(Refusal, pattern='arm'),
        'Takeoff did not name the refused step'
    )
