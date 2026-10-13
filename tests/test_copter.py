from random import randint, uniform

from pymavlink import mavutil
from pytest import approx

from autopilot.copter import Copter
from tests.decoy import Decoy


def test_is_steady_once_it_knows_where_it_is():
    decoy = Decoy(mavutil.mavlink_connection("tcpin:127.0.0.1:0", source_system=7))
    link = decoy.link(7)
    decoy.estimate(831)
    assert Copter(link).steady(), "a copter that knows where it is does not count as steady"


def test_cannot_be_steady_while_it_only_knows_how_it_is_turned():
    decoy = Decoy(mavutil.mavlink_connection("tcpin:127.0.0.1:0", source_system=7))
    link = decoy.link(7)
    decoy.estimate(167)
    assert not Copter(link).steady(), "a copter that does not know where it is counts as steady"


def test_cannot_be_steady_before_it_spoke():
    assert not Copter(
        Decoy(mavutil.mavlink_connection("tcpin:127.0.0.1:0", source_system=7)).link(7)
    ).steady(), "a silent copter counts as steady"


def test_is_guided_in_the_mode_that_obeys_targets():
    decoy = Decoy(mavutil.mavlink_connection("tcpin:127.0.0.1:0", source_system=7))
    link = decoy.link(7)
    decoy.state(4, False)
    assert Copter(link).guided(), "a copter in the guided mode does not count as guided"


def test_cannot_be_guided_in_another_mode():
    decoy = Decoy(mavutil.mavlink_connection("tcpin:127.0.0.1:0", source_system=7))
    link = decoy.link(7)
    decoy.state(randint(5, 9), False)
    assert not Copter(link).guided(), "a copter in another mode counts as guided"


def test_is_armed_once_its_motors_may_spin():
    decoy = Decoy(mavutil.mavlink_connection("tcpin:127.0.0.1:0", source_system=7))
    link = decoy.link(7)
    decoy.state(4, True)
    assert Copter(link).armed(), "a copter with its motors armed does not count as armed"


def test_cannot_be_armed_with_its_motors_safe():
    decoy = Decoy(mavutil.mavlink_connection("tcpin:127.0.0.1:0", source_system=7))
    link = decoy.link(7)
    decoy.state(4, False)
    assert not Copter(link).armed(), "a copter with its motors safe counts as armed"


def test_cannot_be_guided_or_armed_before_it_spoke():
    copter = Copter(
        Decoy(mavutil.mavlink_connection("tcpin:127.0.0.1:0", source_system=7)).link(7)
    )
    assert not (copter.guided() or copter.armed()), "a silent copter counts as guided or armed"


def test_flies_at_its_height_in_metres():
    decoy = Decoy(mavutil.mavlink_connection("tcpin:127.0.0.1:0", source_system=7))
    link = decoy.link(7)
    decoy.climb(2874)
    assert Copter(link).height() == approx(2.874), "the height does not come in metres"


def test_asks_for_the_guided_mode():
    decoy = Decoy(mavutil.mavlink_connection("tcpin:127.0.0.1:0", source_system=7))
    Copter(decoy.link(7)).guide()
    asked = decoy.asked()
    assert (asked.command, asked.param1, asked.param2) == (
        mavutil.mavlink.MAV_CMD_DO_SET_MODE,
        mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
        4,
    ), "the guided mode is not asked for"


def test_asks_to_arm_the_motors():
    decoy = Decoy(mavutil.mavlink_connection("tcpin:127.0.0.1:0", source_system=7))
    Copter(decoy.link(7)).arm()
    asked = decoy.asked()
    assert (asked.command, asked.param1) == (
        mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
        1,
    ), "the motors are not asked to arm"


def test_asks_to_take_off_to_the_altitude():
    decoy = Decoy(mavutil.mavlink_connection("tcpin:127.0.0.1:0", source_system=7))
    altitude = uniform(2.0, 9.0)
    Copter(decoy.link(7)).rise(altitude)
    asked = decoy.asked()
    assert (asked.command, asked.param7) == (
        mavutil.mavlink.MAV_CMD_NAV_TAKEOFF,
        approx(altitude),
    ), "a takeoff to the altitude is not asked for"


def test_asks_the_copter_it_stands_for():
    system = randint(1, 9)
    decoy = Decoy(mavutil.mavlink_connection("tcpin:127.0.0.1:0", source_system=system))
    Copter(decoy.link(system)).arm()
    assert decoy.asked().target_system == system, "another copter is asked to arm"
