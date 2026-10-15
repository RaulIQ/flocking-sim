import random
from uuid import uuid4

from fake_vehicle import FakeVehicle
from flocking_ros.flight.latest import Latest
from flocking_ros.flight.placed import Placed
from flocking_ros.flight.refusal import Refusal
from geometry_msgs.msg import Point, Pose, PoseStamped
from hamcrest import assert_that, calling, contains_exactly, empty, raises
from mavros_msgs.msg import SysStatus
from pymavlink.dialects.v20 import ardupilotmega as mavlink


def test_passes_steps_once_it_knows_where_it_is() -> None:
    steps: list[str] = []
    mode = uuid4().hex
    altitude = random.uniform(5.0, 10.0)
    estimate = Latest(0.1)
    estimate.record(PoseStamped(pose=Pose(position=Point(z=altitude))))
    health = Latest(0.1)
    health.record(SysStatus(sensors_health=mavlink.MAV_SYS_STATUS_PREARM_CHECK))
    vehicle = Placed(FakeVehicle(frozenset(), steps), estimate, health)
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
        calling(
            Placed(FakeVehicle(frozenset(), []), Latest(0.1), Latest(0.1)).switch
        ).with_args(uuid4().hex),
        raises(Refusal, pattern='where it is'),
        'Placed switched without knowing where it is',
    )


def test_does_not_ask_for_a_mode_without_a_position() -> None:
    steps: list[str] = []
    try:
        Placed(FakeVehicle(frozenset(), steps), Latest(0.1), Latest(0.1)).switch(uuid4().hex)
    except Refusal:
        pass
    assert_that(steps, empty(), 'Placed asked for a mode without knowing where it is')


def test_cannot_count_a_climb_done_below_the_altitude() -> None:
    altitude = random.uniform(5.0, 10.0)
    estimate = Latest(0.1)
    estimate.record(PoseStamped(pose=Pose(position=Point(z=0.8 * altitude))))
    assert_that(
        calling(
            Placed(FakeVehicle(frozenset(), []), estimate, Latest(0.1)).ascend
        ).with_args(altitude),
        raises(Refusal, pattern='did not reach'),
        'Placed counted a climb done below the altitude',
    )


def test_cannot_arm_before_the_autopilot_passes_its_checks() -> None:
    health = Latest(0.1)
    health.record(
        SysStatus(sensors_health=random.randint(0, mavlink.MAV_SYS_STATUS_PREARM_CHECK - 1))
    )
    assert_that(
        calling(
            Placed(FakeVehicle(frozenset(), []), Latest(0.1), health).arm
        ).with_args(),
        raises(Refusal, pattern='checks'),
        'Placed armed before the autopilot passed its checks',
    )


def test_does_not_ask_to_arm_before_the_autopilot_passes_its_checks() -> None:
    steps: list[str] = []
    health = Latest(0.1)
    health.record(
        SysStatus(sensors_health=random.randint(0, mavlink.MAV_SYS_STATUS_PREARM_CHECK - 1))
    )
    try:
        Placed(FakeVehicle(frozenset(), steps), Latest(0.1), health).arm()
    except Refusal:
        pass
    assert_that(steps, empty(), 'Placed asked to arm before the autopilot passed its checks')
