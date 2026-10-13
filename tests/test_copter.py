from random import uniform

from pymavlink import mavutil

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
