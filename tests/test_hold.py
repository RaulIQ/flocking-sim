from random import uniform

from pytest import approx

from autopilot.hold import Hold


def test_climbs_by_the_gap_times_the_gain():
    assert Hold(3.0, 0.8, 5.0).climb(2.5) == approx(
        0.4
    ), "the climb is not the gap to the altitude times the gain"


def test_sinks_when_above_the_altitude():
    assert Hold(3.0, 0.8, 5.0).climb(3.5) == approx(
        -0.4
    ), "a copter above the altitude is not sent down"


def test_cannot_climb_at_the_altitude():
    altitude = uniform(2.0, 9.0)
    assert Hold(altitude, uniform(0.5, 2.0), uniform(0.5, 2.0)).climb(
        altitude
    ) == approx(0.0), "a copter at the altitude is still sent up or down"


def test_cannot_climb_faster_than_the_cap():
    cap = uniform(0.5, 2.0)
    assert Hold(50.0, 1.5, cap).climb(uniform(0.0, 9.0)) == approx(
        cap
    ), "the climb goes beyond the cap"


def test_cannot_sink_faster_than_the_cap():
    cap = uniform(0.5, 2.0)
    assert Hold(3.0, 1.5, cap).climb(uniform(40.0, 90.0)) == approx(
        -cap
    ), "the sink goes beyond the cap"
