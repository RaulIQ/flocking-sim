import random
from typing import Any
from uuid import uuid4

from fake_link import FakeLink
from flocking_ros.flight.latest import Latest
from flocking_ros.flight.mavros_vehicle import MavrosVehicle
from flocking_ros.flight.refusal import Refusal
from hamcrest import assert_that, calling, contains_exactly, raises
from mavros_msgs.msg import State
from mavros_msgs.srv import CommandBool, CommandTOL, SetMode


def test_requests_given_mode() -> None:
    requests: list[Any] = []
    mode = uuid4().hex
    status = Latest(0.1)
    status.record(State(mode=mode))
    MavrosVehicle(
        FakeLink(SetMode.Response(mode_sent=True), requests),
        FakeLink(CommandBool.Response(), []),
        FakeLink(CommandTOL.Response(), []),
        status
    ).switch(mode)
    assert_that(
        [request.custom_mode for request in requests],
        contains_exactly(mode),
        'Vehicle did not request the given mode'
    )


def test_cannot_switch_when_mode_is_rejected() -> None:
    mode = uuid4().hex
    status = Latest(0.1)
    status.record(State(mode=mode))
    assert_that(
        calling(
            MavrosVehicle(
                FakeLink(SetMode.Response(mode_sent=False), []),
                FakeLink(CommandBool.Response(), []),
                FakeLink(CommandTOL.Response(), []),
                status
            ).switch
        ).with_args(mode),
        raises(Refusal, pattern=mode),
        'Vehicle did not refuse the rejected mode'
    )


def test_cannot_switch_when_mode_is_never_entered() -> None:
    mode = uuid4().hex
    status = Latest(0.1)
    status.record(State(mode=uuid4().hex))
    assert_that(
        calling(
            MavrosVehicle(
                FakeLink(SetMode.Response(mode_sent=True), []),
                FakeLink(CommandBool.Response(), []),
                FakeLink(CommandTOL.Response(), []),
                status
            ).switch
        ).with_args(mode),
        raises(Refusal, pattern=mode),
        'Vehicle did not refuse the mode that was never entered'
    )


def test_requests_arming() -> None:
    requests: list[Any] = []
    status = Latest(0.1)
    status.record(State(armed=True))
    MavrosVehicle(
        FakeLink(SetMode.Response(), []),
        FakeLink(CommandBool.Response(success=True), requests),
        FakeLink(CommandTOL.Response(), []),
        status
    ).arm()
    assert_that(
        [request.value for request in requests],
        contains_exactly(True),
        'Vehicle did not request arming'
    )


def test_cannot_arm_when_arming_is_rejected() -> None:
    status = Latest(0.1)
    status.record(State(armed=True))
    assert_that(
        calling(
            MavrosVehicle(
                FakeLink(SetMode.Response(), []),
                FakeLink(CommandBool.Response(success=False), []),
                FakeLink(CommandTOL.Response(), []),
                status
            ).arm
        ).with_args(),
        raises(Refusal, pattern='arm'),
        'Vehicle did not refuse the rejected arming'
    )


def test_cannot_arm_when_motors_stay_disarmed() -> None:
    status = Latest(0.1)
    status.record(State(armed=False))
    assert_that(
        calling(
            MavrosVehicle(
                FakeLink(SetMode.Response(), []),
                FakeLink(CommandBool.Response(success=True), []),
                FakeLink(CommandTOL.Response(), []),
                status
            ).arm
        ).with_args(),
        raises(Refusal, pattern='armed'),
        'Vehicle did not refuse while motors stayed disarmed'
    )


def test_requests_takeoff_to_given_altitude() -> None:
    requests: list[Any] = []
    altitude = random.randint(40, 80) / 8
    MavrosVehicle(
        FakeLink(SetMode.Response(), []),
        FakeLink(CommandBool.Response(), []),
        FakeLink(CommandTOL.Response(success=True), requests),
        Latest(0.1)
    ).ascend(altitude)
    assert_that(
        [request.altitude for request in requests],
        contains_exactly(altitude),
        'Vehicle did not request takeoff to the given altitude'
    )


def test_cannot_ascend_when_takeoff_is_rejected() -> None:
    assert_that(
        calling(
            MavrosVehicle(
                FakeLink(SetMode.Response(), []),
                FakeLink(CommandBool.Response(), []),
                FakeLink(CommandTOL.Response(success=False), []),
                Latest(0.1)
            ).ascend
        ).with_args(random.uniform(5.0, 10.0)),
        raises(Refusal, pattern='take off'),
        'Vehicle did not refuse the rejected takeoff'
    )
