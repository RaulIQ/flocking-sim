from math import pi

from pygame import Surface
from pytest import approx

from config import (
    Barrier,
    Bubbles,
    Cloud,
    Limits,
    Picture,
    Settings,
    Shape,
    Spring,
    Swarm,
    Window,
)
from simulator.body import Body
from simulator.drone import Drone
from simulator.flock import Flock
from simulator.trail import Trail
from agent.vector import Vector
from simulator.view import View
from simulator.wall import Wall


def test_draws_the_origin_in_the_middle_of_the_window():
    assert View(
        Surface((10, 10)),
        Settings(
            Limits(2.0, 4.0, 1.8, 8.0),
            Picture(Window(1000, 700, 60.0, 60), Shape(0.1, 0.35, 600)),
            Swarm(8, 1.2, Bubbles(0.25, 0.6), Cloud(Spring(1.2, 2.0, 0.5, 1.0), Spring(1.2, 2.0, 1.5, 1.5), Spring(0.6, 8.0, 0.0, 0.0), 6)),
            Barrier(4.0, 14.0, 1.2, (0.0,)),
        ),
    ).spot(Vector(0.0, 0.0)) == (
        approx(500.0),
        approx(350.0),
    ), "the origin does not land in the middle of the window"


def test_draws_a_northern_place_above_the_middle():
    assert View(
        Surface((10, 10)),
        Settings(
            Limits(2.0, 4.0, 1.8, 8.0),
            Picture(Window(1000, 700, 60.0, 60), Shape(0.1, 0.35, 600)),
            Swarm(8, 1.2, Bubbles(0.25, 0.6), Cloud(Spring(1.2, 2.0, 0.5, 1.0), Spring(1.2, 2.0, 1.5, 1.5), Spring(0.6, 8.0, 0.0, 0.0), 6)),
            Barrier(4.0, 14.0, 1.2, (0.0,)),
        ),
    ).spot(Vector(0.0, 1.0)) == (
        approx(500.0),
        approx(290.0),
    ), "a place to the north does not rise on the screen"


def test_reads_the_middle_of_the_window_as_the_origin():
    assert View(
        Surface((10, 10)),
        Settings(
            Limits(2.0, 4.0, 1.8, 8.0),
            Picture(Window(1000, 700, 60.0, 60), Shape(0.1, 0.35, 600)),
            Swarm(8, 1.2, Bubbles(0.25, 0.6), Cloud(Spring(1.2, 2.0, 0.5, 1.0), Spring(1.2, 2.0, 1.5, 1.5), Spring(0.6, 8.0, 0.0, 0.0), 6)),
            Barrier(4.0, 14.0, 1.2, (0.0,)),
        ),
    ).place((500, 350)) == Vector(
        approx(0.0), approx(0.0)
    ), "the middle of the window does not read as the origin"


def test_reads_a_pixel_right_of_the_middle_as_an_eastern_place():
    assert View(
        Surface((10, 10)),
        Settings(
            Limits(2.0, 4.0, 1.8, 8.0),
            Picture(Window(1000, 700, 60.0, 60), Shape(0.1, 0.35, 600)),
            Swarm(8, 1.2, Bubbles(0.25, 0.6), Cloud(Spring(1.2, 2.0, 0.5, 1.0), Spring(1.2, 2.0, 1.5, 1.5), Spring(0.6, 8.0, 0.0, 0.0), 6)),
            Barrier(4.0, 14.0, 1.2, (0.0,)),
        ),
    ).place((560, 350)) == Vector(
        approx(1.0), approx(0.0)
    ), "a pixel to the right does not read as a place to the east"


def test_reads_a_pixel_above_the_middle_as_a_northern_place():
    assert View(
        Surface((10, 10)),
        Settings(
            Limits(2.0, 4.0, 1.8, 8.0),
            Picture(Window(1000, 700, 60.0, 60), Shape(0.1, 0.35, 600)),
            Swarm(8, 1.2, Bubbles(0.25, 0.6), Cloud(Spring(1.2, 2.0, 0.5, 1.0), Spring(1.2, 2.0, 1.5, 1.5), Spring(0.6, 8.0, 0.0, 0.0), 6)),
            Barrier(4.0, 14.0, 1.2, (0.0,)),
        ),
    ).place((500, 290)) == Vector(
        approx(0.0), approx(1.0)
    ), "a pixel above the middle does not read as a place to the north"


def test_paints_the_leader_in_its_own_colour():
    surface = Surface((200, 200))
    View(
        surface,
        Settings(
            Limits(2.0, 4.0, 1.8, 8.0),
            Picture(Window(200, 200, 100.0, 60), Shape(0.1, 0.35, 5)),
            Swarm(2, 1.2, Bubbles(0.25, 0.6), Cloud(Spring(1.2, 2.0, 0.5, 1.0), Spring(1.2, 2.0, 1.5, 1.5), Spring(0.6, 8.0, 0.0, 0.0), 6)),
            Barrier(4.0, 14.0, 1.2, (0.0,)),
        ),
    ).show(
        Flock(
            (
                Drone(Body(Vector(0.0, 0.0), pi / 2, Vector(0.0, 0.0), 0.0), Trail((), 5), True),
                Drone(Body(Vector(-0.7, 0.0), pi / 2, Vector(0.0, 0.0), 0.0), Trail((), 5), False),
            )
        ),
        (),
    )
    assert tuple(surface.get_at((100, 100)))[:3] != tuple(surface.get_at((30, 100)))[
        :3
    ], "the leader does not differ in colour from a follower"


def test_paints_a_follower_brighter_than_the_sky():
    surface = Surface((200, 200))
    View(
        surface,
        Settings(
            Limits(2.0, 4.0, 1.8, 8.0),
            Picture(Window(200, 200, 100.0, 60), Shape(0.1, 0.35, 5)),
            Swarm(2, 1.2, Bubbles(0.25, 0.6), Cloud(Spring(1.2, 2.0, 0.5, 1.0), Spring(1.2, 2.0, 1.5, 1.5), Spring(0.6, 8.0, 0.0, 0.0), 6)),
            Barrier(4.0, 14.0, 1.2, (0.0,)),
        ),
    ).show(
        Flock(
            (
                Drone(Body(Vector(0.0, 0.0), pi / 2, Vector(0.0, 0.0), 0.0), Trail((), 5), True),
                Drone(Body(Vector(-0.7, 0.0), pi / 2, Vector(0.0, 0.0), 0.0), Trail((), 5), False),
            )
        ),
        (),
    )
    assert tuple(surface.get_at((30, 100)))[:3] != tuple(surface.get_at((195, 5)))[
        :3
    ], "a follower does not show against the sky"


def test_rings_a_drone_with_its_hard_bubble():
    surface = Surface((200, 200))
    View(
        surface,
        Settings(
            Limits(2.0, 4.0, 1.8, 8.0),
            Picture(Window(200, 200, 100.0, 60), Shape(0.1, 0.35, 5)),
            Swarm(2, 1.2, Bubbles(0.25, 0.6), Cloud(Spring(1.2, 2.0, 0.5, 1.0), Spring(1.2, 2.0, 1.5, 1.5), Spring(0.6, 8.0, 0.0, 0.0), 6)),
            Barrier(4.0, 14.0, 1.2, (0.0,)),
        ),
    ).show(
        Flock(
            (
                Drone(Body(Vector(0.0, 0.0), pi / 2, Vector(0.0, 0.0), 0.0), Trail((), 5), True),
                Drone(Body(Vector(-0.7, 0.0), pi / 2, Vector(0.0, 0.0), 0.0), Trail((), 5), False),
            )
        ),
        (),
    )
    assert {tuple(surface.get_at((x, 100)))[:3] for x in (123, 124, 125, 126)} != {
        tuple(surface.get_at((195, 5)))[:3]
    }, "the hard bubble does not show around a drone"


def test_rings_a_drone_with_its_soft_bubble():
    surface = Surface((200, 200))
    View(
        surface,
        Settings(
            Limits(2.0, 4.0, 1.8, 8.0),
            Picture(Window(200, 200, 100.0, 60), Shape(0.1, 0.35, 5)),
            Swarm(2, 1.2, Bubbles(0.25, 0.6), Cloud(Spring(1.2, 2.0, 0.5, 1.0), Spring(1.2, 2.0, 1.5, 1.5), Spring(0.6, 8.0, 0.0, 0.0), 6)),
            Barrier(4.0, 14.0, 1.2, (0.0,)),
        ),
    ).show(
        Flock(
            (
                Drone(Body(Vector(0.0, 0.0), pi / 2, Vector(0.0, 0.0), 0.0), Trail((), 5), True),
                Drone(Body(Vector(-0.7, 0.0), pi / 2, Vector(0.0, 0.0), 0.0), Trail((), 5), False),
            )
        ),
        (),
    )
    assert {tuple(surface.get_at((x, 100)))[:3] for x in (158, 159, 160, 161)} != {
        tuple(surface.get_at((195, 5)))[:3]
    }, "the soft bubble does not show around a drone"


def test_paints_the_two_bubbles_in_different_colours():
    surface = Surface((200, 200))
    View(
        surface,
        Settings(
            Limits(2.0, 4.0, 1.8, 8.0),
            Picture(Window(200, 200, 100.0, 60), Shape(0.1, 0.35, 5)),
            Swarm(2, 1.2, Bubbles(0.25, 0.6), Cloud(Spring(1.2, 2.0, 0.5, 1.0), Spring(1.2, 2.0, 1.5, 1.5), Spring(0.6, 8.0, 0.0, 0.0), 6)),
            Barrier(4.0, 14.0, 1.2, (0.0,)),
        ),
    ).show(
        Flock(
            (
                Drone(Body(Vector(0.0, 0.0), pi / 2, Vector(0.0, 0.0), 0.0), Trail((), 5), True),
                Drone(Body(Vector(-0.7, 0.0), pi / 2, Vector(0.0, 0.0), 0.0), Trail((), 5), False),
            )
        ),
        (),
    )
    assert {tuple(surface.get_at((x, 100)))[:3] for x in (123, 124, 125, 126)} != {
        tuple(surface.get_at((x, 100)))[:3] for x in (158, 159, 160, 161)
    }, "the hard bubble does not differ in colour from the soft one"


def test_draws_a_wall_against_the_sky():
    surface = Surface((200, 200))
    View(
        surface,
        Settings(
            Limits(2.0, 4.0, 1.8, 8.0),
            Picture(Window(200, 200, 100.0, 60), Shape(0.1, 0.35, 5)),
            Swarm(2, 1.2, Bubbles(0.25, 0.6), Cloud(Spring(1.2, 4.0, 0.5, 1.0), Spring(1.2, 4.0, 1.5, 1.5), Spring(0.6, 8.0, 0.0, 0.0), 6)),
            Barrier(4.0, 14.0, 1.2, (0.0,)),
        ),
    ).show(
        Flock(
            (Drone(Body(Vector(0.0, 0.0), pi / 2, Vector(0.0, 0.0), 0.0), Trail((), 5), True),)
        ),
        (Wall(Vector(0.5, -1.0), Vector(0.5, 1.0)),),
    )
    assert tuple(surface.get_at((150, 20)))[:3] != tuple(surface.get_at((195, 5)))[
        :3
    ], "a wall does not show against the sky"
