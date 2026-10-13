from pathlib import Path
from random import randint, uniform

from pytest import approx

from autopilot.fleet import Fleet
from autopilot.hangar import Hangar
from autopilot.spot import Spot
from simulator.muster import Muster
from tests.stub import Stub


def test_holds_as_many_copters_as_the_muster_places():
    count = randint(2, 6)
    assert (
        len(
            Hangar(
                Fleet(23450, Spot(uniform(-60.0, 60.0), uniform(-170.0, 170.0)), Path("/nowhere"), Path("/nowhere/tuning.parm")),
                Muster(count, 1.3),
            ).copters()
        )
        == count
    ), "a hangar does not hold a copter for every place of the muster"


def test_stands_the_first_copter_on_the_origin():
    origin = Spot(uniform(-60.0, 60.0), uniform(-170.0, 170.0))
    assert origin.offset(
        Hangar(Fleet(23450, origin, Path("/nowhere"), Path("/nowhere/tuning.parm")), Muster(3, 1.3)).copters()[0].home
    ).length() == approx(0.0), "the first copter does not stand on the origin"


def test_stands_the_second_copter_one_spacing_away():
    origin = Spot(uniform(-60.0, 60.0), uniform(-170.0, 170.0))
    spacing = uniform(1.0, 3.0)
    assert origin.offset(
        Hangar(Fleet(23450, origin, Path("/nowhere"), Path("/nowhere/tuning.parm")), Muster(3, spacing)).copters()[1].home
    ).length() == approx(spacing), "the second copter does not stand one spacing away"


def test_cannot_give_two_copters_the_same_port():
    count = randint(2, 6)
    assert (
        len(
            {
                copter.port()
                for copter in Hangar(
                    Fleet(23450, Spot(uniform(-60.0, 60.0), uniform(-170.0, 170.0)), Path("/nowhere"), Path("/nowhere/tuning.parm")),
                    Muster(count, 1.3),
                ).copters()
            }
        )
        == count
    ), "two copters listen on the same port"


def test_runs_every_copter_while_open(tmp_path):
    with Hangar(
        Fleet(
            23450,
            Spot(uniform(-60.0, 60.0), uniform(-170.0, 170.0)),
            Stub(tmp_path / "ardupilot", "exec sleep 30").built(),
            Path("/nowhere/tuning.parm"),
        ),
        Muster(3, 1.3),
    ).opened(tmp_path / "run") as processes:
        assert [process.poll() for process in processes] == [
            None,
            None,
            None,
        ], "a copter does not run while the hangar is open"


def test_cannot_leave_any_copter_running_once_closed(tmp_path):
    with Hangar(
        Fleet(
            23450,
            Spot(uniform(-60.0, 60.0), uniform(-170.0, 170.0)),
            Stub(tmp_path / "ardupilot", "exec sleep 30").built(),
            Path("/nowhere/tuning.parm"),
        ),
        Muster(3, 1.3),
    ).opened(tmp_path / "run") as processes:
        pass
    assert None not in [
        process.poll() for process in processes
    ], "a copter keeps running after the hangar closed"
