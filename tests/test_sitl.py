from pathlib import Path
from random import randint, uniform

from autopilot.sitl import Sitl
from autopilot.spot import Spot
from tests.stub import Stub


def test_listens_ten_ports_further_with_every_number():
    number = randint(1, 9)
    base = randint(20000, 40000)
    assert (
        Sitl(Path("/nowhere"), number, Spot(uniform(-60.0, 60.0), uniform(-170.0, 170.0)), base).port()
        == base + 10 * number
    ), "a copter does not listen ten ports further with every number"


def test_asks_for_the_base_port_before_the_number():
    words = Sitl(
        Path("/nowhere"), randint(1, 9), Spot(uniform(-60.0, 60.0), uniform(-170.0, 170.0)), 23450
    ).words()
    assert words.index("--base-port") < words.index(
        "-I"
    ), "the base port does not come before the number"


def test_names_the_copter_one_above_its_number():
    number = randint(1, 9)
    words = Sitl(
        Path("/nowhere"), number, Spot(uniform(-60.0, 60.0), uniform(-170.0, 170.0)), 23450
    ).words()
    assert words[words.index("--sysid") + 1] == str(
        number + 1
    ), "the system id is not one above the number"


def test_starts_at_its_home_with_the_nose_to_the_east():
    words = Sitl(Path("/nowhere"), randint(1, 9), Spot(-35.3632607, 149.1652351), 23450).words()
    assert (
        words[words.index("--home") + 1] == "-35.3632607,149.1652351,0,90"
    ), "a copter does not start at its home with the nose to the east"


def test_runs_the_copter_built_in_the_source():
    assert Sitl(
        Path("/somewhere/ardupilot"),
        randint(1, 9),
        Spot(uniform(-60.0, 60.0), uniform(-170.0, 170.0)),
        23450,
    ).words()[0] == "/somewhere/ardupilot/build/sitl/bin/arducopter", "a copter does not run from its source"


def test_runs_in_a_folder_of_its_own(tmp_path):
    with Sitl(
        Stub(tmp_path / "ardupilot", "echo here > mark").built(),
        4,
        Spot(uniform(-60.0, 60.0), uniform(-170.0, 170.0)),
        23450,
    ).running(tmp_path / "run") as process:
        process.wait(timeout=5)
        assert (tmp_path / "run" / "4" / "mark").exists(), "a copter does not run in a folder of its own"


def test_writes_what_the_copter_says_into_a_log(tmp_path):
    with Sitl(
        Stub(tmp_path / "ardupilot", "echo ready").built(),
        2,
        Spot(uniform(-60.0, 60.0), uniform(-170.0, 170.0)),
        23450,
    ).running(tmp_path / "run") as process:
        process.wait(timeout=5)
        assert (
            tmp_path / "run" / "2" / "sitl.log"
        ).read_text() == "ready\n", "the words of a copter do not reach its log"


def test_cannot_leave_the_copter_running(tmp_path):
    with Sitl(
        Stub(tmp_path / "ardupilot", "exec sleep 30").built(),
        1,
        Spot(uniform(-60.0, 60.0), uniform(-170.0, 170.0)),
        23450,
    ).running(tmp_path / "run") as process:
        pass
    assert process.poll() is not None, "a copter keeps running after it was left"
