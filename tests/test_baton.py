from pygame import K_SPACE, K_TAB, KEYDOWN, MOUSEBUTTONDOWN, MOUSEMOTION, Surface
from pygame.event import Event

from agent.vector import Vector
from config import Bubbles, Cloud, Limits, Settings, Shape, Spring, Swarm, Window
from simulator.baton import Baton
from simulator.body import Body
from simulator.drone import Drone
from simulator.flock import Flock
from simulator.trail import Trail
from simulator.view import View


def test_passes_the_lead_on_the_tab_key():
    assert [
        drone.leader
        for drone in Baton(
            View(
                Surface((10, 10)),
                Settings(
                    Limits(2.0, 4.0, 1.8, 8.0),
                    Window(200, 200, 100.0, 60),
                    Shape(0.1, 0.35, 5),
                    Swarm(2, 1.2, Bubbles(0.25, 0.6), Cloud(Spring(1.2, 4.0, 0.5, 1.0), Spring(1.2, 4.0, 1.5, 1.5), 6)),
                ),
            ),
            0.6,
        )
        .passed(
            Flock(
                (
                    Drone(Body(Vector(0.0, 0.0), 0.0, Vector(0.0, 0.0), 0.0), Trail((), 5), True),
                    Drone(Body(Vector(-0.7, 0.0), 0.0, Vector(0.0, 0.0), 0.0), Trail((), 5), False),
                )
            ),
            [Event(KEYDOWN, key=K_TAB)],
        )
        .drones
    ] == [False, True], "the tab key does not pass the lead"


def test_passes_the_lead_once_for_every_tab():
    assert [
        drone.leader
        for drone in Baton(
            View(
                Surface((10, 10)),
                Settings(
                    Limits(2.0, 4.0, 1.8, 8.0),
                    Window(200, 200, 100.0, 60),
                    Shape(0.1, 0.35, 5),
                    Swarm(2, 1.2, Bubbles(0.25, 0.6), Cloud(Spring(1.2, 4.0, 0.5, 1.0), Spring(1.2, 4.0, 1.5, 1.5), 6)),
                ),
            ),
            0.6,
        )
        .passed(
            Flock(
                (
                    Drone(Body(Vector(0.0, 0.0), 0.0, Vector(0.0, 0.0), 0.0), Trail((), 5), True),
                    Drone(Body(Vector(-0.7, 0.0), 0.0, Vector(0.0, 0.0), 0.0), Trail((), 5), False),
                    Drone(Body(Vector(0.7, 0.4), 0.0, Vector(0.0, 0.0), 0.0), Trail((), 5), False),
                )
            ),
            [Event(KEYDOWN, key=K_TAB), Event(KEYDOWN, key=K_TAB)],
        )
        .drones
    ] == [False, False, True], "two tabs do not pass the lead twice"


def test_hands_the_lead_to_a_clicked_drone():
    assert [
        drone.leader
        for drone in Baton(
            View(
                Surface((10, 10)),
                Settings(
                    Limits(2.0, 4.0, 1.8, 8.0),
                    Window(200, 200, 100.0, 60),
                    Shape(0.1, 0.35, 5),
                    Swarm(2, 1.2, Bubbles(0.25, 0.6), Cloud(Spring(1.2, 4.0, 0.5, 1.0), Spring(1.2, 4.0, 1.5, 1.5), 6)),
                ),
            ),
            0.6,
        )
        .passed(
            Flock(
                (
                    Drone(Body(Vector(0.0, 0.0), 0.0, Vector(0.0, 0.0), 0.0), Trail((), 5), True),
                    Drone(Body(Vector(-0.7, 0.0), 0.0, Vector(0.0, 0.0), 0.0), Trail((), 5), False),
                )
            ),
            [Event(MOUSEBUTTONDOWN, button=1, pos=(25, 110))],
        )
        .drones
    ] == [False, True], "a click on a drone does not hand it the lead"


def test_cannot_hand_the_lead_with_the_right_button():
    assert [
        drone.leader
        for drone in Baton(
            View(
                Surface((10, 10)),
                Settings(
                    Limits(2.0, 4.0, 1.8, 8.0),
                    Window(200, 200, 100.0, 60),
                    Shape(0.1, 0.35, 5),
                    Swarm(2, 1.2, Bubbles(0.25, 0.6), Cloud(Spring(1.2, 4.0, 0.5, 1.0), Spring(1.2, 4.0, 1.5, 1.5), 6)),
                ),
            ),
            0.6,
        )
        .passed(
            Flock(
                (
                    Drone(Body(Vector(0.0, 0.0), 0.0, Vector(0.0, 0.0), 0.0), Trail((), 5), True),
                    Drone(Body(Vector(-0.7, 0.0), 0.0, Vector(0.0, 0.0), 0.0), Trail((), 5), False),
                )
            ),
            [Event(MOUSEBUTTONDOWN, button=3, pos=(25, 110))],
        )
        .drones
    ] == [True, False], "the right button hands the lead over"


def test_cannot_pass_the_lead_on_other_events():
    assert [
        drone.leader
        for drone in Baton(
            View(
                Surface((10, 10)),
                Settings(
                    Limits(2.0, 4.0, 1.8, 8.0),
                    Window(200, 200, 100.0, 60),
                    Shape(0.1, 0.35, 5),
                    Swarm(2, 1.2, Bubbles(0.25, 0.6), Cloud(Spring(1.2, 4.0, 0.5, 1.0), Spring(1.2, 4.0, 1.5, 1.5), 6)),
                ),
            ),
            0.6,
        )
        .passed(
            Flock(
                (
                    Drone(Body(Vector(0.0, 0.0), 0.0, Vector(0.0, 0.0), 0.0), Trail((), 5), True),
                    Drone(Body(Vector(-0.7, 0.0), 0.0, Vector(0.0, 0.0), 0.0), Trail((), 5), False),
                )
            ),
            [Event(KEYDOWN, key=K_SPACE), Event(MOUSEMOTION, pos=(30, 100))],
        )
        .drones
    ] == [True, False], "an unrelated event passes the lead"
