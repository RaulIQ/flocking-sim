import random

from flocking_ros.flight.persistent import Persistent
from flocking_ros.flight.refusal import Refusal
from hamcrest import assert_that, calling, has_length, raises
from stubborn_maneuver import StubbornManeuver


def test_flies_a_refused_maneuver_again_until_it_is_flown() -> None:
    refusals = random.randint(1, 4)
    tries: list[int] = []
    Persistent(StubbornManeuver([refusals], tries), 5.0, 0.01).fly()
    assert_that(
        tries, has_length(refusals + 1), 'Persistent did not fly the refused maneuver again'
    )


def test_flies_an_obeyed_maneuver_once() -> None:
    tries: list[int] = []
    Persistent(StubbornManeuver([0], tries), 5.0, 0.01).fly()
    assert_that(tries, has_length(1), 'Persistent flew an obeyed maneuver more than once')


def test_cannot_fly_again_beyond_its_seconds() -> None:
    assert_that(
        calling(Persistent(StubbornManeuver([10**6], []), 0.1, 0.01).fly).with_args(),
        raises(Refusal, pattern='refused'),
        'Persistent kept flying beyond its seconds',
    )
