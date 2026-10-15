from agent.vector import Vector
from config import copters
from flocking_ros.ground.script import Script
from hamcrest import assert_that, close_to, contains_exactly, empty, equal_to
from scenarios.route import Route
from scenarios.scenario import Scenario
from scenarios.tally import Passage, Tally
from simulator.body import Body
from simulator.drone import Drone
from simulator.flock import Flock
from simulator.trail import Trail


def test_flies_the_leader_toward_the_next_place_of_the_route():
    command = Script(
        'hop',
        Scenario('A hop', copters(), Route((Vector(-6.0, 0.0),), 1.5, 0.3), 10.0),
        Route((Vector(-6.0, 0.0),), 1.5, 0.3),
    ).command(Body(Vector(0.0, 0.0), 0.0, Vector(0.0, 0.0), 0.0))
    assert_that(
        (command.velocity.x, command.velocity.y),
        contains_exactly(close_to(-1.5, 1e-9), close_to(0.0, 1e-9)),
        'the script does not fly the leader toward the next place',
    )


def test_moves_on_once_the_leader_reaches_a_place():
    assert_that(
        Script(
            'hop',
            Scenario(
                'A hop', copters(), Route((Vector(-6.0, 0.0), Vector(0.0, 0.0)), 1.5, 0.3), 10.0
            ),
            Route((Vector(-6.0, 0.0), Vector(0.0, 0.0)), 1.5, 0.3),
        )
        .rest(Body(Vector(-5.9, 0.1), 0.0, Vector(0.0, 0.0), 0.0))
        .route.places,
        contains_exactly(Vector(0.0, 0.0)),
        'the script does not move on once the leader reaches a place',
    )


def test_cannot_report_before_the_scenario_ends():
    assert_that(
        Script(
            'hop',
            Scenario('A hop', copters(), Route((), 1.5, 0.3), 10.0),
            Route((), 1.5, 0.3),
        ).told(
            199,
            Tally(1.0, 1.0, 0, Passage(0, 0.0)),
            Flock(
                (Drone(Body(Vector(0.0, 0.0), 0.0, Vector(0.0, 0.0), 0.0), Trail((), 1), True),)
            ),
        ),
        empty(),
        'the script reports before its scenario ends',
    )


def test_reports_once_the_scenario_ends():
    assert_that(
        Script(
            'hop',
            Scenario('A hop', copters(), Route((), 1.5, 0.3), 10.0),
            Route((), 1.5, 0.3),
        ).told(
            200,
            Tally(1.0, 1.0, 0, Passage(0, 0.0)),
            Flock(
                (Drone(Body(Vector(0.0, 0.0), 0.0, Vector(0.0, 0.0), 0.0), Trail((), 1), True),)
            ),
        )[0],
        equal_to('scenario: hop'),
        'the script does not report once its scenario ends',
    )
