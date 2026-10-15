import random
from uuid import uuid4

from fake_vehicle import FakeVehicle
from flocking_ros.flight.online import Online
from flocking_ros.flight.refusal import Refusal
from flocking_ros.flight.status import Status
from hamcrest import assert_that, calling, contains_exactly, raises
from mavros_msgs.msg import State


def test_passes_steps_to_connected_vehicle() -> None:
    steps: list[str] = []
    mode = uuid4().hex
    altitude = random.uniform(5.0, 10.0)
    status = Status(0.1)
    status.record(State(connected=True))
    vehicle = Online(FakeVehicle(frozenset(), steps), status)
    vehicle.switch(mode)
    vehicle.arm()
    vehicle.ascend(altitude)
    assert_that(
        steps,
        contains_exactly(f'switch {mode}', 'arm', f'ascend {altitude}'),
        'Online did not pass the steps to the connected vehicle'
    )


def test_cannot_switch_while_disconnected() -> None:
    status = Status(0.1)
    status.record(State(connected=False))
    assert_that(
        calling(Online(FakeVehicle(frozenset(), []), status).switch).with_args(uuid4().hex),
        raises(Refusal, pattern='not connected'),
        'Online did not refuse to switch while disconnected'
    )


def test_cannot_arm_while_disconnected() -> None:
    status = Status(0.1)
    status.record(State(connected=False))
    assert_that(
        calling(Online(FakeVehicle(frozenset(), []), status).arm).with_args(),
        raises(Refusal, pattern='not connected'),
        'Online did not refuse to arm while disconnected'
    )


def test_cannot_ascend_while_disconnected() -> None:
    status = Status(0.1)
    status.record(State(connected=False))
    assert_that(
        calling(Online(FakeVehicle(frozenset(), []), status).ascend).with_args(
            random.uniform(5.0, 10.0)
        ),
        raises(Refusal, pattern='not connected'),
        'Online did not refuse to ascend while disconnected'
    )
