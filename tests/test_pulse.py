from time import monotonic

from autopilot.pulse import Pulse


def test_wakes_on_the_beat():
    Pulse(10.0).wait()
    assert monotonic() % 0.1 < 0.03, "a pulse does not wake on its beat"


def test_cannot_wait_longer_than_one_beat():
    start = monotonic()
    Pulse(20.0).wait()
    assert monotonic() - start < 0.08, "a pulse waits longer than one beat"
