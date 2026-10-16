from uuid import uuid4

from flocking_ros.flight.dispatch import Dispatch
from hamcrest import assert_that, contains_exactly, empty
from rclpy.logging import get_logger, LoggingSeverity
from std_msgs.msg import String
from stubborn_maneuver import StubbornManeuver


def test_flies_maneuver_named_by_command() -> None:
    tries: list[int] = []
    word = uuid4().hex
    log = get_logger(uuid4().hex)
    log.set_level(LoggingSeverity.FATAL)
    Dispatch(
        {word: StubbornManeuver([0], tries), uuid4().hex: StubbornManeuver([1], [])}, log
    ).receive(String(data=word))
    assert_that(tries, contains_exactly(1), 'Dispatch did not fly the maneuver named by command')


def test_does_not_fly_on_unknown_command() -> None:
    tries: list[int] = []
    log = get_logger(uuid4().hex)
    log.set_level(LoggingSeverity.FATAL)
    Dispatch({uuid4().hex: StubbornManeuver([0], tries)}, log).receive(String(data=uuid4().hex))
    assert_that(tries, empty(), 'Dispatch did not ignore the unknown command')


def test_keeps_flying_after_refused_maneuver() -> None:
    tries: list[int] = []
    refused = uuid4().hex
    word = uuid4().hex
    log = get_logger(uuid4().hex)
    log.set_level(LoggingSeverity.FATAL)
    dispatch = Dispatch(
        {refused: StubbornManeuver([1], []), word: StubbornManeuver([0], tries)}, log
    )
    dispatch.receive(String(data=refused))
    dispatch.receive(String(data=word))
    assert_that(tries, contains_exactly(1), 'Dispatch did not keep flying after the refusal')
