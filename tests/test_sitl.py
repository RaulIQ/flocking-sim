from pathlib import Path
from random import randint, uniform

from pymavlink import mavutil
from pytest import approx

from autopilot.fleet import Fleet
from autopilot.sitl import Sitl
from autopilot.spot import Spot
from tests.decoy import Decoy
from tests.stub import Stub


def test_listens_ten_ports_further_with_every_number():
    number = randint(1, 9)
    base = randint(20000, 40000)
    assert (
        Sitl(Fleet(base, Spot(uniform(-60.0, 60.0), uniform(-170.0, 170.0)), Path("/nowhere"), Path("/nowhere/tuning")), number, Spot(uniform(-60.0, 60.0), uniform(-170.0, 170.0))).port()
        == base + 10 * number
    ), "a copter does not listen ten ports further with every number"


def test_asks_for_the_base_port_before_the_number():
    words = Sitl(Fleet(23450, Spot(uniform(-60.0, 60.0), uniform(-170.0, 170.0)), Path("/nowhere"), Path("/nowhere/tuning")), randint(1, 9), Spot(uniform(-60.0, 60.0), uniform(-170.0, 170.0))).words()
    assert words.index("--base-port") < words.index(
        "-I"
    ), "the base port does not come before the number"


def test_names_the_copter_one_above_its_number():
    number = randint(1, 9)
    words = Sitl(Fleet(23450, Spot(uniform(-60.0, 60.0), uniform(-170.0, 170.0)), Path("/nowhere"), Path("/nowhere/tuning")), number, Spot(uniform(-60.0, 60.0), uniform(-170.0, 170.0))).words()
    assert words[words.index("--sysid") + 1] == str(
        number + 1
    ), "the system id is not one above the number"


def test_starts_at_its_home_with_the_nose_to_the_east():
    words = Sitl(Fleet(23450, Spot(-35.3632607, 149.1652351), Path("/nowhere"), Path("/nowhere/tuning")), randint(1, 9), Spot(-35.3632607, 149.1652351)).words()
    assert (
        words[words.index("--home") + 1] == "-35.3632607,149.1652351,0,90"
    ), "a copter does not start at its home with the nose to the east"


def test_runs_the_copter_built_in_the_source():
    assert Sitl(Fleet(23450, Spot(uniform(-60.0, 60.0), uniform(-170.0, 170.0)), Path("/somewhere/ardupilot"), Path("/nowhere/tuning")), randint(1, 9), Spot(uniform(-60.0, 60.0), uniform(-170.0, 170.0))).words()[0] == "/somewhere/ardupilot/build/sitl/bin/arducopter", "a copter does not run from its source"


def test_runs_in_a_folder_of_its_own(tmp_path):
    with Sitl(Fleet(23450, Spot(uniform(-60.0, 60.0), uniform(-170.0, 170.0)), Stub(tmp_path / "ardupilot", "echo here > mark").built(), Stub(tmp_path / "ardupilot", "echo here > mark").tuned()), 4, Spot(uniform(-60.0, 60.0), uniform(-170.0, 170.0))).running(tmp_path / "run") as process:
        process.wait(timeout=5)
        assert (tmp_path / "run" / "4" / "mark").exists(), "a copter does not run in a folder of its own"


def test_writes_what_the_copter_says_into_a_log(tmp_path):
    with Sitl(Fleet(23450, Spot(uniform(-60.0, 60.0), uniform(-170.0, 170.0)), Stub(tmp_path / "ardupilot", "echo ready").built(), Stub(tmp_path / "ardupilot", "echo ready").tuned()), 2, Spot(uniform(-60.0, 60.0), uniform(-170.0, 170.0))).running(tmp_path / "run") as process:
        process.wait(timeout=5)
        assert (
            tmp_path / "run" / "2" / "sitl.log"
        ).read_text() == "ready\n", "the words of a copter do not reach its log"


def test_cannot_leave_the_copter_running(tmp_path):
    with Sitl(Fleet(23450, Spot(uniform(-60.0, 60.0), uniform(-170.0, 170.0)), Stub(tmp_path / "ardupilot", "exec sleep 30").built(), Stub(tmp_path / "ardupilot", "exec sleep 30").tuned()), 1, Spot(uniform(-60.0, 60.0), uniform(-170.0, 170.0))).running(tmp_path / "run") as process:
        pass
    assert process.poll() is not None, "a copter keeps running after it was left"


def test_links_to_the_port_it_listens_on():
    decoy = Decoy(mavutil.mavlink_connection("tcpin:127.0.0.1:0", source_system=3))
    link = Sitl(Fleet(decoy.port() - 20, Spot(uniform(-60.0, 60.0), uniform(-170.0, 170.0)), Path("/nowhere"), Path("/nowhere/tuning")), 2, Spot(uniform(-60.0, 60.0), uniform(-170.0, 170.0))).link()
    decoy.fix(-353632607, 1491652351, 0, 0)
    decoy.attitude(uniform(-3.0, 3.0), uniform(-2.0, 2.0))
    assert link.telemetry().fix.spot == Spot(
        approx(-35.3632607), approx(149.1652351)
    ), "a copter is not linked through the port it listens on"


def test_links_to_the_system_one_above_its_number():
    number = randint(1, 9)
    decoy = Decoy(mavutil.mavlink_connection("tcpin:127.0.0.1:0", source_system=number + 1))
    assert (
        Sitl(Fleet(decoy.port() - 10 * number, Spot(uniform(-60.0, 60.0), uniform(-170.0, 170.0)), Path("/nowhere"), Path("/nowhere/tuning")), number, Spot(uniform(-60.0, 60.0), uniform(-170.0, 170.0)))
        .link()
        .system
        == number + 1
    ), "a copter is not linked as the system one above its number"


def test_lays_the_parameters_of_its_tuning_over_the_defaults_of_the_copter():
    assert Sitl(
        Fleet(
            23450,
            Spot(uniform(-60.0, 60.0), uniform(-170.0, 170.0)),
            Path("/somewhere/ardupilot"),
            Path("/elsewhere/tuning"),
        ),
        randint(1, 9),
        Spot(uniform(-60.0, 60.0), uniform(-170.0, 170.0)),
    ).words()[-1] == (
        "/somewhere/ardupilot/Tools/autotest/default_params/copter.parm,/elsewhere/tuning/copter.parm"
    ), "the parameters of the tuning are not laid over the defaults of the copter"


def test_flies_the_frame_that_lies_in_its_own_folder():
    words = Sitl(
        Fleet(
            23450,
            Spot(uniform(-60.0, 60.0), uniform(-170.0, 170.0)),
            Path("/somewhere/ardupilot"),
            Path("/elsewhere/tuning"),
        ),
        randint(1, 9),
        Spot(uniform(-60.0, 60.0), uniform(-170.0, 170.0)),
    ).words()
    assert (
        words[words.index("--model") + 1] == "+:frame.json"
    ), "a copter does not fly the frame that lies in its own folder"


def test_brings_the_frame_of_its_tuning_into_its_own_folder(tmp_path):
    with Sitl(
        Fleet(
            23450,
            Spot(uniform(-60.0, 60.0), uniform(-170.0, 170.0)),
            Stub(tmp_path / "ardupilot", "echo ready").built(),
            Stub(tmp_path / "ardupilot", "echo ready").tuned(),
        ),
        3,
        Spot(uniform(-60.0, 60.0), uniform(-170.0, 170.0)),
    ).running(tmp_path / "run") as process:
        process.wait(timeout=5)
        assert (tmp_path / "run" / "3" / "frame.json").read_text() == (
            '{"mass": 0.25}\n'
        ), "the frame of the tuning does not reach the folder of the copter"
