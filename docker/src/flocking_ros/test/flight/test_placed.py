import random
from uuid import uuid4

from fake_vehicle import FakeVehicle
from flocking_ros.flight.latest import Latest
from flocking_ros.flight.placed import Placed
from flocking_ros.flight.refusal import Refusal
from geometry_msgs.msg import Point, Pose, PoseStamped
from hamcrest import assert_that, calling, contains_exactly, empty, raises


def test_passes_steps_once_it_knows_where_it_is() -> None:
    steps: list[str] = []
    mode = uuid4().hex
    altitude = random.uniform(5.0, 10.0)
    estimate = Latest(0.1)
    estimate.record(PoseStamped(pose=Pose(position=Point(z=altitude))))
    vehicle = Placed(FakeVehicle(frozenset(), steps), estimate)
    vehicle.switch(mode)
    vehicle.arm()
    vehicle.ascend(altitude)
    assert_that(
        steps,
        contains_exactly(f'switch {mode}', 'arm', f'ascend {altitude}'),
        'Placed did not pass the steps once it knew where it was',
    )


def test_cannot_switch_without_a_position() -> None:
    assert_that(
        calling(Placed(FakeVehicle(frozenset(), []), Latest(0.1)).switch).with_args(
            uuid4().hex
        ),
        raises(Refusal, pattern='where it is'),
        'Placed switched without knowing where it is',
    )


def test_does_not_ask_for_a_mode_without_a_position() -> None:
    steps: list[str] = []
    try:
        Placed(FakeVehicle(frozenset(), steps), Latest(0.1)).switch(uuid4().hex)
    except Refusal:
        pass
    assert_that(steps, empty(), 'Placed asked for a mode without knowing where it is')


def test_cannot_count_a_climb_done_below_the_altitude() -> None:
    altitude = random.uniform(5.0, 10.0)
    estimate = Latest(0.1)
    estimate.record(PoseStamped(pose=Pose(position=Point(z=0.8 * altitude))))
    assert_that(
        calling(Placed(FakeVehicle(frozenset(), []), estimate).ascend).with_args(altitude),
        raises(Refusal, pattern='did not reach'),
        'Placed counted a climb done below the altitude',
    )
