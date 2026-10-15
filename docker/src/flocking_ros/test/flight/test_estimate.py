from random import uniform
from threading import Timer
from uuid import uuid4

from flocking_ros.flight.estimate import Estimate
from flocking_ros.flight.refusal import Refusal
from geometry_msgs.msg import Point, Pose, PoseStamped
from hamcrest import assert_that, calling, has_key, raises


def test_confirms_recorded_position() -> None:
    height = uniform(1.0, 9.0)
    estimate = Estimate(0.1)
    seen: dict[float, bool] = {}
    estimate.record(PoseStamped(pose=Pose(position=Point(z=height))))
    estimate.expect(lambda pose: seen.setdefault(pose.pose.position.z, True), 'unreached')
    assert_that(seen, has_key(height), 'Estimate did not confirm the position')


def test_confirms_position_arriving_later() -> None:
    height = uniform(1.0, 9.0)
    estimate = Estimate(5.0)
    seen: dict[float, bool] = {}
    Timer(0.05, estimate.record, [PoseStamped(pose=Pose(position=Point(z=height)))]).start()
    estimate.expect(lambda pose: seen.setdefault(pose.pose.position.z, True), 'unreached')
    assert_that(seen, has_key(height), 'Estimate did not wait for the later position')


def test_trusts_only_latest_position() -> None:
    estimate = Estimate(0.1)
    estimate.record(PoseStamped(pose=Pose(position=Point(z=3.0))))
    estimate.record(PoseStamped(pose=Pose(position=Point(z=0.5))))
    assert_that(
        calling(estimate.expect).with_args(lambda pose: pose.pose.position.z > 2.0, 'low'),
        raises(Refusal),
        'Estimate did not forget the outdated position',
    )


def test_refuses_with_given_reason_when_position_never_matches() -> None:
    reason = uuid4().hex
    estimate = Estimate(0.1)
    estimate.record(PoseStamped(pose=Pose(position=Point(z=uniform(0.0, 1.0)))))
    assert_that(
        calling(estimate.expect).with_args(lambda pose: pose.pose.position.z > 2.0, reason),
        raises(Refusal, pattern=reason),
        'Estimate did not refuse with the given reason',
    )


def test_refuses_when_nothing_is_recorded() -> None:
    assert_that(
        calling(Estimate(0.1).expect).with_args(lambda pose: True, 'silent'),
        raises(Refusal),
        'Estimate did not refuse without any position',
    )
