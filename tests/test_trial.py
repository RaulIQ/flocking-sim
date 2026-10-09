from agent.vector import Vector
from config import defaults
from scenarios.route import Route
from scenarios.scenario import Scenario
from scenarios.trial import Trial


def test_steps_through_every_tick_of_the_scenario():
    assert len(
        list(
            Trial(
                "short", Scenario("A short hop", defaults(), Route((), 1.0, 0.3), 1.5), 6
            ).frames()
        )
    ) == 90, "a trial does not step through every tick of its scenario"


def test_flies_the_leader_along_the_route():
    assert list(
        Trial(
            "hop",
            Scenario("A hop west", defaults(), Route((Vector(-3.0, 0.0),), 1.0, 0.3), 6.0),
            6,
        ).frames()
    )[-1][1].leader().body.position.x < -2.5, "a trial does not fly the leader along the route"


def test_writes_a_summary_of_the_run(tmp_path):
    Trial("hop", Scenario("A short hop", defaults(), Route((), 1.0, 0.3), 0.5), 6).run(
        tmp_path
    )
    assert "closest pair of drones, m:" in (tmp_path / "hop.txt").read_text(), (
        "a trial does not write a summary of its run"
    )


def test_writes_a_line_for_every_drone_in_every_kept_frame(tmp_path):
    Trial("hop", Scenario("A short hop", defaults(), Route((), 1.0, 0.3), 0.5), 6).run(
        tmp_path
    )
    assert len((tmp_path / "hop.csv").read_text().splitlines()) == 41, (
        "a trace does not hold a line for every drone in every kept frame"
    )


def test_writes_the_same_trace_every_time(tmp_path):
    Trial(
        "hop",
        Scenario("A hop west", defaults(), Route((Vector(-3.0, 0.0),), 2.0, 0.3), 3.0),
        6,
    ).run(tmp_path / "first")
    Trial(
        "hop",
        Scenario("A hop west", defaults(), Route((Vector(-3.0, 0.0),), 2.0, 0.3), 3.0),
        6,
    ).run(tmp_path / "second")
    assert (tmp_path / "first" / "hop.csv").read_text() == (
        tmp_path / "second" / "hop.csv"
    ).read_text(), "two runs of one scenario do not write the same trace"


def test_reports_what_it_has_tallied(tmp_path):
    assert (
        Trial("hop", Scenario("A short hop", defaults(), Route((), 1.0, 0.3), 0.5), 6)
        .run(tmp_path)
        .lines()[0]
        == "scenario: hop"
    ), "a report does not start with the name of its scenario"
