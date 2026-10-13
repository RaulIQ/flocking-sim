from random import randint, uniform

from pymavlink import mavutil
from pytest import approx, raises

from autopilot.spot import Spot
from tests.decoy import Decoy


def test_tells_the_spot_in_degrees():
    decoy = Decoy(mavutil.mavlink_connection("tcpin:127.0.0.1:0", source_system=7))
    link = decoy.link(7)
    decoy.fix(-353632607, 1491652351, randint(-500, 500), randint(-500, 500))
    decoy.attitude(uniform(-3.0, 3.0), uniform(-2.0, 2.0))
    assert link.telemetry().fix.spot == Spot(
        approx(-35.3632607), approx(149.1652351)
    ), "the spot does not come in degrees"


def test_tells_the_speeds_in_metres_a_second():
    decoy = Decoy(mavutil.mavlink_connection("tcpin:127.0.0.1:0", source_system=7))
    link = decoy.link(7)
    decoy.fix(randint(-600000000, 600000000), randint(-1700000000, 1700000000), 137, -264)
    decoy.attitude(uniform(-3.0, 3.0), uniform(-2.0, 2.0))
    assert (link.telemetry().fix.north, link.telemetry().fix.east) == (
        approx(1.37),
        approx(-2.64),
    ), "the speeds do not come in metres a second"


def test_tells_the_yaw_and_its_rate():
    decoy = Decoy(mavutil.mavlink_connection("tcpin:127.0.0.1:0", source_system=7))
    link = decoy.link(7)
    yaw = uniform(-3.0, 3.0)
    rate = uniform(-2.0, 2.0)
    decoy.fix(randint(-600000000, 600000000), randint(-1700000000, 1700000000), 0, 0)
    decoy.attitude(yaw, rate)
    assert (link.telemetry().attitude.yaw, link.telemetry().attitude.rate) == (
        approx(yaw),
        approx(rate),
    ), "the yaw and its rate do not come as the copter told them"


def test_tells_only_the_latest_of_what_the_copter_said():
    decoy = Decoy(mavutil.mavlink_connection("tcpin:127.0.0.1:0", source_system=7))
    link = decoy.link(7)
    decoy.attitude(uniform(-3.0, 3.0), uniform(-2.0, 2.0))
    decoy.fix(randint(-600000000, 600000000), randint(-1700000000, 1700000000), 111, 0)
    decoy.fix(randint(-600000000, 600000000), randint(-1700000000, 1700000000), 222, 0)
    assert link.telemetry().fix.north == approx(
        2.22
    ), "an older word of the copter outlives a newer one"


def test_cannot_tell_anything_before_the_copter_spoke():
    link = Decoy(
        mavutil.mavlink_connection("tcpin:127.0.0.1:0", source_system=7)
    ).link(7)
    with raises(LookupError, match="Copter 7 has not told"):
        link.telemetry()


def test_cannot_tell_anything_from_a_position_alone():
    decoy = Decoy(mavutil.mavlink_connection("tcpin:127.0.0.1:0", source_system=4))
    link = decoy.link(4)
    decoy.fix(randint(-600000000, 600000000), randint(-1700000000, 1700000000), 0, 0)
    with raises(LookupError, match="Copter 4 has not told"):
        link.telemetry()


def test_asks_for_the_position_and_the_attitude():
    decoy = Decoy(mavutil.mavlink_connection("tcpin:127.0.0.1:0", source_system=7))
    link = decoy.link(7)
    decoy.beat()
    link.subscribe(uniform(10.0, 50.0))
    assert {decoy.asked().param1, decoy.asked().param1} == {
        mavutil.mavlink.MAVLINK_MSG_ID_GLOBAL_POSITION_INT,
        mavutil.mavlink.MAVLINK_MSG_ID_ATTITUDE,
    }, "the position and the attitude are not both asked for"


def test_asks_for_the_pause_that_gives_the_rate():
    decoy = Decoy(mavutil.mavlink_connection("tcpin:127.0.0.1:0", source_system=7))
    link = decoy.link(7)
    decoy.beat()
    link.subscribe(25.0)
    assert decoy.asked().param2 == approx(
        40000.0
    ), "the pause between messages does not give the rate"


def test_asks_the_copter_it_talks_to():
    system = randint(1, 9)
    decoy = Decoy(mavutil.mavlink_connection("tcpin:127.0.0.1:0", source_system=system))
    link = decoy.link(system)
    decoy.beat()
    link.subscribe(uniform(10.0, 50.0))
    assert decoy.asked().target_system == system, "the request goes to another copter"


def test_asks_to_change_how_often_messages_come():
    decoy = Decoy(mavutil.mavlink_connection("tcpin:127.0.0.1:0", source_system=7))
    link = decoy.link(7)
    decoy.beat()
    link.subscribe(uniform(10.0, 50.0))
    assert (
        decoy.asked().command == mavutil.mavlink.MAV_CMD_SET_MESSAGE_INTERVAL
    ), "the request does not change how often messages come"


def test_cannot_ask_a_copter_that_has_not_beaten_yet():
    link = Decoy(
        mavutil.mavlink_connection("tcpin:127.0.0.1:0", source_system=5)
    ).link(5)
    with raises(LookupError, match="Copter 5 has not sent a heartbeat"):
        link.subscribe(uniform(10.0, 50.0))
