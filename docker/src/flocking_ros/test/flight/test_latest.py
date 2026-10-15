from random import uniform
from threading import Timer
from uuid import uuid4

from flocking_ros.flight.latest import Latest
from flocking_ros.flight.refusal import Refusal
from geometry_msgs.msg import Point, Pose, PoseStamped
from hamcrest import assert_that, calling, has_key, raises
from mavros_msgs.msg import State


def test_confirms_recorded_message() -> None:
    mode = uuid4().hex
    latest = Latest(0.1)
    seen: dict[str, bool] = {}
    latest.record(State(mode=mode))
    latest.expect(lambda state: seen.setdefault(state.mode, True), 'unreached')
    assert_that(seen, has_key(mode), 'Latest did not confirm the recorded message')


def test_confirms_message_arriving_later() -> None:
    height = uniform(1.0, 9.0)
    latest = Latest(5.0)
    seen: dict[float, bool] = {}
    Timer(0.05, latest.record, [PoseStamped(pose=Pose(position=Point(z=height)))]).start()
    latest.expect(lambda pose: seen.setdefault(pose.pose.position.z, True), 'unreached')
    assert_that(seen, has_key(height), 'Latest did not wait for the message arriving later')


def test_trusts_only_latest_message() -> None:
    latest = Latest(0.1)
    latest.record(State(armed=True))
    latest.record(State(armed=False))
    assert_that(
        calling(latest.expect).with_args(lambda state: state.armed, 'disarmed'),
        raises(Refusal),
        'Latest did not forget the outdated message',
    )


def test_refuses_with_given_reason_when_message_never_matches() -> None:
    reason = uuid4().hex
    latest = Latest(0.1)
    latest.record(State(mode=uuid4().hex))
    assert_that(
        calling(latest.expect).with_args(lambda state: state.mode == 'GUIDED', reason),
        raises(Refusal, pattern=reason),
        'Latest did not refuse with the given reason',
    )


def test_refuses_when_nothing_is_recorded() -> None:
    assert_that(
        calling(Latest(0.1).expect).with_args(lambda message: True, 'silent'),
        raises(Refusal),
        'Latest did not refuse without any message',
    )
