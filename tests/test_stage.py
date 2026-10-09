from itertools import combinations

from pytest import approx

from agent.command import Command
from agent.tuning import Cloud, Limits, Spring
from agent.vector import Vector
from config import Barrier, Bubbles, Picture, Settings, Shape, Swarm, Window
from simulator.stage import Stage


def test_musters_as_many_drones_as_the_settings_ask():
    assert len(
        Stage(
            Settings(
                Limits(2.0, 4.0, 1.8, 8.0),
                Picture(Window(1000, 700, 60.0, 60), Shape(0.1, 0.35, 7)),
                Swarm(5, 1.3, Bubbles(0.25, 0.6), Cloud(Spring(1.2, 4.0, 0.5, 1.0), Spring(1.2, 4.0, 1.5, 1.5), Spring(0.6, 8.0, 0.0, 0.0), 6)),
                Barrier(4.0, 14.0, 1.2, (0.0,)),
            )
        )
        .flock()
        .drones
    ) == 5, "a stage does not muster every drone"


def test_musters_the_drones_a_spacing_apart():
    assert min(
        one.body.position.minus(other.body.position).length()
        for one, other in combinations(
            Stage(
                Settings(
                    Limits(2.0, 4.0, 1.8, 8.0),
                    Picture(Window(1000, 700, 60.0, 60), Shape(0.1, 0.35, 7)),
                    Swarm(5, 1.3, Bubbles(0.25, 0.6), Cloud(Spring(1.2, 4.0, 0.5, 1.0), Spring(1.2, 4.0, 1.5, 1.5), Spring(0.6, 8.0, 0.0, 0.0), 6)),
                    Barrier(4.0, 14.0, 1.2, (0.0,)),
                )
            )
            .flock()
            .drones,
            2,
        )
    ) == approx(1.3), "a stage does not muster the drones a spacing apart"


def test_gives_the_lead_to_the_first_drone():
    assert [
        drone.leader
        for drone in Stage(
            Settings(
                Limits(2.0, 4.0, 1.8, 8.0),
                Picture(Window(1000, 700, 60.0, 60), Shape(0.1, 0.35, 7)),
                Swarm(3, 1.3, Bubbles(0.25, 0.6), Cloud(Spring(1.2, 4.0, 0.5, 1.0), Spring(1.2, 4.0, 1.5, 1.5), Spring(0.6, 8.0, 0.0, 0.0), 6)),
                Barrier(4.0, 14.0, 1.2, (0.0,)),
            )
        )
        .flock()
        .drones
    ] == [True, False, False], "a stage does not give the lead to the first drone"


def test_builds_the_walls_of_its_barrier():
    assert Stage(
        Settings(
            Limits(2.0, 4.0, 1.8, 8.0),
            Picture(Window(1000, 700, 60.0, 60), Shape(0.1, 0.35, 7)),
            Swarm(3, 1.3, Bubbles(0.25, 0.6), Cloud(Spring(1.2, 4.0, 0.5, 1.0), Spring(1.2, 4.0, 1.5, 1.5), Spring(0.6, 8.0, 0.0, 0.0), 6)),
            Barrier(3.5, 14.0, 1.2, (0.0,)),
        )
    ).walls()[1].start == Vector(
        approx(3.5), approx(0.6)
    ), "a stage does not build the walls of its barrier"


def test_ticks_as_often_as_the_window_refreshes():
    assert Stage(
        Settings(
            Limits(2.0, 4.0, 1.8, 8.0),
            Picture(Window(1000, 700, 60.0, 25), Shape(0.1, 0.35, 7)),
            Swarm(3, 1.3, Bubbles(0.25, 0.6), Cloud(Spring(1.2, 4.0, 0.5, 1.0), Spring(1.2, 4.0, 1.5, 1.5), Spring(0.6, 8.0, 0.0, 0.0), 6)),
            Barrier(4.0, 14.0, 1.2, (0.0,)),
        )
    ).lapse() == approx(0.04), "a stage does not tick as often as the window refreshes"


def test_flies_the_leader_on_a_request():
    stage = Stage(
        Settings(
            Limits(2.0, 100.0, 1.8, 8.0),
            Picture(Window(1000, 700, 60.0, 4), Shape(0.1, 0.35, 7)),
            Swarm(3, 1.3, Bubbles(0.25, 0.6), Cloud(Spring(1.2, 4.0, 0.5, 1.0), Spring(1.2, 4.0, 1.5, 1.5), Spring(0.6, 8.0, 0.0, 0.0), 6)),
            Barrier(40.0, 14.0, 1.2, (0.0,)),
        )
    )
    assert stage.after(
        stage.flock(), Command(Vector(0.0, -1.6), 0.0)
    ).leader().body.position == Vector(
        approx(0.0), approx(-0.4)
    ), "a stage does not fly the leader on a request"


def test_cannot_fly_the_leader_into_a_wall():
    stage = Stage(
        Settings(
            Limits(2.0, 100.0, 1.8, 8.0),
            Picture(Window(1000, 700, 60.0, 4), Shape(0.1, 0.35, 7)),
            Swarm(1, 1.3, Bubbles(0.25, 0.6), Cloud(Spring(1.2, 4.0, 0.5, 1.0), Spring(1.2, 4.0, 1.5, 1.5), Spring(0.6, 8.0, 0.0, 0.0), 6)),
            Barrier(0.2, 14.0, 0.0, (0.0,)),
        )
    )
    assert stage.after(
        stage.flock(), Command(Vector(2.0, 0.0), 0.0)
    ).leader().body.position == Vector(
        approx(0.0), approx(0.0)
    ), "a stage flies the leader into a wall"
