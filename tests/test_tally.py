from math import inf

from pytest import approx

from agent.vector import Vector
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
from scenarios.tally import Passage, Tally
from simulator.body import Body
from simulator.drone import Drone
from simulator.flock import Flock
from simulator.trail import Trail


def test_notes_the_closest_pair_of_drones():
    assert Tally(inf, inf, 0, Passage(0, 0.0)).after(
        1.5,
        Flock(
            (
                Drone(Body(Vector(0.0, 0.0), 0.0, Vector(0.0, 0.0), 0.0), Trail((), 1), True),
                Drone(Body(Vector(0.9, 1.2), 0.0, Vector(0.0, 0.0), 0.0), Trail((), 1), False),
                Drone(Body(Vector(-3.0, 0.0), 0.0, Vector(0.0, 0.0), 0.0), Trail((), 1), False),
            )
        ),
        Settings(
            Limits(2.0, 4.0, 1.8, 8.0),
            Picture(Window(1000, 700, 60.0, 60), Shape(0.1, 0.35, 1)),
            Swarm(3, 1.2, Bubbles(0.25, 0.6), Cloud(Spring(1.2, 4.0, 0.5, 1.0), Spring(1.2, 4.0, 1.5, 1.5), Spring(0.6, 8.0, 0.0, 0.0), 6)),
            Barrier(4.0, 14.0, 1.2, (0.0,)),
        ),
    ).pair == approx(1.5), "a tally does not note the closest pair of drones"


def test_cannot_forget_a_closer_pair_from_an_earlier_frame():
    assert Tally(0.7, inf, 0, Passage(0, 0.0)).after(
        1.5,
        Flock(
            (
                Drone(Body(Vector(0.0, 0.0), 0.0, Vector(0.0, 0.0), 0.0), Trail((), 1), True),
                Drone(Body(Vector(0.9, 1.2), 0.0, Vector(0.0, 0.0), 0.0), Trail((), 1), False),
            )
        ),
        Settings(
            Limits(2.0, 4.0, 1.8, 8.0),
            Picture(Window(1000, 700, 60.0, 60), Shape(0.1, 0.35, 1)),
            Swarm(2, 1.2, Bubbles(0.25, 0.6), Cloud(Spring(1.2, 4.0, 0.5, 1.0), Spring(1.2, 4.0, 1.5, 1.5), Spring(0.6, 8.0, 0.0, 0.0), 6)),
            Barrier(4.0, 14.0, 1.2, (0.0,)),
        ),
    ).pair == approx(0.7), "a tally forgets a closer pair from an earlier frame"


def test_notes_the_closest_drone_to_a_wall():
    assert Tally(inf, inf, 0, Passage(0, 0.0)).after(
        1.5,
        Flock(
            (
                Drone(Body(Vector(0.0, 0.0), 0.0, Vector(0.0, 0.0), 0.0), Trail((), 1), True),
                Drone(Body(Vector(3.3, 2.0), 0.0, Vector(0.0, 0.0), 0.0), Trail((), 1), False),
            )
        ),
        Settings(
            Limits(2.0, 4.0, 1.8, 8.0),
            Picture(Window(1000, 700, 60.0, 60), Shape(0.1, 0.35, 1)),
            Swarm(2, 1.2, Bubbles(0.25, 0.6), Cloud(Spring(1.2, 4.0, 0.5, 1.0), Spring(1.2, 4.0, 1.5, 1.5), Spring(0.6, 8.0, 0.0, 0.0), 6)),
            Barrier(4.0, 14.0, 1.2, (0.0,)),
        ),
    ).wall == approx(0.7), "a tally does not note the closest drone to a wall"


def test_counts_a_frame_where_two_hard_bubbles_overlap():
    assert Tally(inf, inf, 3, Passage(0, 0.0)).after(
        1.5,
        Flock(
            (
                Drone(Body(Vector(0.0, 0.0), 0.0, Vector(0.0, 0.0), 0.0), Trail((), 1), True),
                Drone(Body(Vector(0.45, 0.0), 0.0, Vector(0.0, 0.0), 0.0), Trail((), 1), False),
            )
        ),
        Settings(
            Limits(2.0, 4.0, 1.8, 8.0),
            Picture(Window(1000, 700, 60.0, 60), Shape(0.1, 0.35, 1)),
            Swarm(2, 1.2, Bubbles(0.25, 0.6), Cloud(Spring(1.2, 4.0, 0.5, 1.0), Spring(1.2, 4.0, 1.5, 1.5), Spring(0.6, 8.0, 0.0, 0.0), 6)),
            Barrier(4.0, 14.0, 1.2, (0.0,)),
        ),
    ).breaches == 4, "a tally does not count a frame where two hard bubbles overlap"


def test_counts_a_frame_where_a_wall_reaches_into_a_hard_bubble():
    assert Tally(inf, inf, 3, Passage(0, 0.0)).after(
        1.5,
        Flock(
            (
                Drone(Body(Vector(0.0, 0.0), 0.0, Vector(0.0, 0.0), 0.0), Trail((), 1), True),
                Drone(Body(Vector(3.8, 2.0), 0.0, Vector(0.0, 0.0), 0.0), Trail((), 1), False),
            )
        ),
        Settings(
            Limits(2.0, 4.0, 1.8, 8.0),
            Picture(Window(1000, 700, 60.0, 60), Shape(0.1, 0.35, 1)),
            Swarm(2, 1.2, Bubbles(0.25, 0.6), Cloud(Spring(1.2, 4.0, 0.5, 1.0), Spring(1.2, 4.0, 1.5, 1.5), Spring(0.6, 8.0, 0.0, 0.0), 6)),
            Barrier(4.0, 14.0, 1.2, (0.0,)),
        ),
    ).breaches == 4, "a tally does not count a wall inside a hard bubble"


def test_cannot_count_a_frame_where_every_bubble_is_whole():
    assert Tally(inf, inf, 3, Passage(0, 0.0)).after(
        1.5,
        Flock(
            (
                Drone(Body(Vector(0.0, 0.0), 0.0, Vector(0.0, 0.0), 0.0), Trail((), 1), True),
                Drone(Body(Vector(0.55, 0.0), 0.0, Vector(0.0, 0.0), 0.0), Trail((), 1), False),
            )
        ),
        Settings(
            Limits(2.0, 4.0, 1.8, 8.0),
            Picture(Window(1000, 700, 60.0, 60), Shape(0.1, 0.35, 1)),
            Swarm(2, 1.2, Bubbles(0.25, 0.6), Cloud(Spring(1.2, 4.0, 0.5, 1.0), Spring(1.2, 4.0, 1.5, 1.5), Spring(0.6, 8.0, 0.0, 0.0), 6)),
            Barrier(4.0, 14.0, 1.2, (0.0,)),
        ),
    ).breaches == 3, "a tally counts a frame where every bubble is whole"


def test_notes_when_a_drone_gets_beyond_the_wall():
    assert Tally(inf, inf, 0, Passage(0, 0.0)).after(
        7.5,
        Flock(
            (
                Drone(Body(Vector(4.6, 0.0), 0.0, Vector(0.0, 0.0), 0.0), Trail((), 1), True),
                Drone(Body(Vector(3.0, 0.0), 0.0, Vector(0.0, 0.0), 0.0), Trail((), 1), False),
            )
        ),
        Settings(
            Limits(2.0, 4.0, 1.8, 8.0),
            Picture(Window(1000, 700, 60.0, 60), Shape(0.1, 0.35, 1)),
            Swarm(2, 1.2, Bubbles(0.25, 0.6), Cloud(Spring(1.2, 4.0, 0.5, 1.0), Spring(1.2, 4.0, 1.5, 1.5), Spring(0.6, 8.0, 0.0, 0.0), 6)),
            Barrier(4.0, 14.0, 1.2, (0.0,)),
        ),
    ).passage == Passage(1, approx(7.5)), "a tally does not note a drone beyond the wall"


def test_keeps_the_time_of_the_last_passage_while_nobody_passes():
    assert Tally(inf, inf, 0, Passage(1, 7.5)).after(
        9.0,
        Flock(
            (
                Drone(Body(Vector(4.6, 0.0), 0.0, Vector(0.0, 0.0), 0.0), Trail((), 1), True),
                Drone(Body(Vector(3.0, 0.0), 0.0, Vector(0.0, 0.0), 0.0), Trail((), 1), False),
            )
        ),
        Settings(
            Limits(2.0, 4.0, 1.8, 8.0),
            Picture(Window(1000, 700, 60.0, 60), Shape(0.1, 0.35, 1)),
            Swarm(2, 1.2, Bubbles(0.25, 0.6), Cloud(Spring(1.2, 4.0, 0.5, 1.0), Spring(1.2, 4.0, 1.5, 1.5), Spring(0.6, 8.0, 0.0, 0.0), 6)),
            Barrier(4.0, 14.0, 1.2, (0.0,)),
        ),
    ).passage == Passage(1, approx(7.5)), "a tally moves the time of a passage nobody made"


def test_tallies_a_lonely_drone_without_a_pair():
    assert Tally(inf, inf, 0, Passage(0, 0.0)).after(
        1.5,
        Flock(
            (Drone(Body(Vector(0.0, 0.0), 0.0, Vector(0.0, 0.0), 0.0), Trail((), 1), True),)
        ),
        Settings(
            Limits(2.0, 4.0, 1.8, 8.0),
            Picture(Window(1000, 700, 60.0, 60), Shape(0.1, 0.35, 1)),
            Swarm(1, 1.2, Bubbles(0.25, 0.6), Cloud(Spring(1.2, 4.0, 0.5, 1.0), Spring(1.2, 4.0, 1.5, 1.5), Spring(0.6, 8.0, 0.0, 0.0), 6)),
            Barrier(4.0, 14.0, 1.2, (0.0,)),
        ),
    ).pair == inf, "a lonely drone gets a pair distance out of nowhere"
