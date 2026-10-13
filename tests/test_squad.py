from random import uniform

from pymavlink import mavutil
from pytest import approx, raises

from agent.vector import Vector
from autopilot.spot import Spot
from autopilot.squad import Squad
from tests.decoy import Decoy


def test_sees_every_copter_at_its_metres_from_the_origin():
    origin = Spot(uniform(-60.0, 60.0), uniform(-170.0, 170.0))
    places = (
        Vector(uniform(-50.0, 50.0), uniform(-50.0, 50.0)),
        Vector(uniform(-50.0, 50.0), uniform(-50.0, 50.0)),
    )
    links = ()
    for system, place in enumerate(places, 1):
        decoy = Decoy(mavutil.mavlink_connection("tcpin:127.0.0.1:0", source_system=system))
        links += (decoy.link(system),)
        decoy.fix(
            round(origin.shifted(place).latitude * 1e7),
            round(origin.shifted(place).longitude * 1e7),
            0,
            0,
        )
        decoy.attitude(uniform(-3.0, 3.0), uniform(-2.0, 2.0))
    assert tuple(body.position for body in Squad(links, origin).bodies()) == tuple(
        Vector(approx(place.x, abs=0.02), approx(place.y, abs=0.02)) for place in places
    ), "a copter is not seen at its metres from the origin"


def test_asks_every_copter_for_its_telemetry():
    decoys = tuple(
        Decoy(mavutil.mavlink_connection("tcpin:127.0.0.1:0", source_system=system))
        for system in (1, 2, 3)
    )
    links = tuple(decoy.link(system) for system, decoy in enumerate(decoys, 1))
    for decoy in decoys:
        decoy.beat()
        decoy.fix(1, 2, 3, 4)
        decoy.attitude(uniform(-3.0, 3.0), uniform(-2.0, 2.0))
    Squad(links, Spot(uniform(-60.0, 60.0), uniform(-170.0, 170.0))).tune(
        uniform(10.0, 50.0), 5.0
    )
    assert None not in [
        decoy.asked() for decoy in decoys
    ], "a copter is not asked for its telemetry"


def test_cannot_tune_a_copter_that_stays_silent():
    link = Decoy(
        mavutil.mavlink_connection("tcpin:127.0.0.1:0", source_system=6)
    ).link(6)
    with raises(TimeoutError, match="Copter 6 sent no HEARTBEAT"):
        Squad((link,), Spot(uniform(-60.0, 60.0), uniform(-170.0, 170.0))).tune(
            uniform(10.0, 50.0), 0.2
        )


def test_cannot_tune_a_copter_that_beats_but_tells_nothing():
    decoy = Decoy(mavutil.mavlink_connection("tcpin:127.0.0.1:0", source_system=6))
    link = decoy.link(6)
    decoy.beat()
    with raises(TimeoutError, match="Copter 6 sent no GLOBAL_POSITION_INT"):
        Squad((link,), Spot(uniform(-60.0, 60.0), uniform(-170.0, 170.0))).tune(
            uniform(10.0, 50.0), 0.2
        )
