from threading import Timer
from uuid import uuid4

from flocking_ros.flight.refusal import Refusal
from flocking_ros.flight.status import Status
from hamcrest import assert_that, calling, has_key, raises
from mavros_msgs.msg import State


def test_confirms_recorded_state() -> None:
    mode = uuid4().hex
    status = Status(0.1)
    seen: dict[str, bool] = {}
    status.record(State(mode=mode))
    status.expect(lambda state: seen.setdefault(state.mode, True), 'unreached')
    assert_that(seen, has_key(mode), 'Status did not confirm the recorded state')


def test_confirms_state_arriving_later() -> None:
    mode = uuid4().hex
    status = Status(5.0)
    seen: dict[str, bool] = {}
    Timer(0.05, status.record, [State(mode=mode)]).start()
    status.expect(lambda state: seen.setdefault(state.mode, True), 'unreached')
    assert_that(seen, has_key(mode), 'Status did not wait for the state arriving later')


def test_trusts_only_latest_state() -> None:
    status = Status(0.1)
    status.record(State(armed=True))
    status.record(State(armed=False))
    assert_that(
        calling(status.expect).with_args(lambda state: state.armed, 'disarmed'),
        raises(Refusal),
        'Status did not forget the outdated state'
    )


def test_refuses_with_given_reason_when_state_never_matches() -> None:
    reason = uuid4().hex
    status = Status(0.1)
    status.record(State(mode=uuid4().hex))
    assert_that(
        calling(status.expect).with_args(lambda state: state.mode == 'GUIDED', reason),
        raises(Refusal, pattern=reason),
        'Status did not refuse with the given reason'
    )


def test_refuses_when_nothing_is_recorded() -> None:
    assert_that(
        calling(Status(0.1).expect).with_args(lambda state: True, 'silent'),
        raises(Refusal),
        'Status did not refuse without any state'
    )
