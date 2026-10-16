from uuid import uuid4

from fake_vehicle import FakeVehicle
from flocking_ros.flight.refusal import Refusal
from flocking_ros.flight.transition import Transition
from hamcrest import assert_that, calling, contains_exactly, raises


def test_switches_vehicle_to_its_mode() -> None:
    steps: list[str] = []
    mode = uuid4().hex
    Transition(FakeVehicle(frozenset(), steps), mode).fly()
    assert_that(
        steps,
        contains_exactly(f'switch {mode}'),
        'Transition did not switch the vehicle to its mode'
    )


def test_passes_refusal_on() -> None:
    assert_that(
        calling(Transition(FakeVehicle(frozenset({'switch'}), []), uuid4().hex).fly).with_args(),
        raises(Refusal),
        'Transition did not pass the refusal on'
    )
