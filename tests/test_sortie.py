from random import uniform

from pytest import raises

from autopilot.fleet import Fleet
from autopilot.hangar import Hangar
from autopilot.hold import Hold
from autopilot.pulse import Pulse
from autopilot.sortie import Sortie
from autopilot.spot import Spot
from simulator.muster import Muster
from tests.stub import Stub


def test_cannot_fly_copters_that_do_not_listen(tmp_path):
    with raises(ConnectionRefusedError):
        with Sortie(
            Hangar(
                Fleet(
                    23450,
                    Spot(uniform(-60.0, 60.0), uniform(-170.0, 170.0)),
                    Stub(tmp_path / "ardupilot", "exec sleep 30").built(),
                ),
                Muster(2, 1.3),
            ),
            Hold(3.0, 1.0, 1.0),
            Pulse(20.0),
        ).flown(tmp_path / "run"):
            pass
