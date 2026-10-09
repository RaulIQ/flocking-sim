from pygame import Surface
from pytest import approx

from config import Limits, Settings, Shape, Window
from simulator.vector import Vector
from simulator.view import View


def test_draws_the_origin_in_the_middle_of_the_window():
    assert View(
        Surface((10, 10)),
        Settings(Limits(2.0, 4.0, 1.8, 8.0), Window(1000, 700, 60.0), Shape(0.1, 0.35, 600), 60),
    ).spot(Vector(0.0, 0.0)) == (
        approx(500.0),
        approx(350.0),
    ), "the origin does not land in the middle of the window"


def test_draws_a_northern_place_above_the_middle():
    assert View(
        Surface((10, 10)),
        Settings(Limits(2.0, 4.0, 1.8, 8.0), Window(1000, 700, 60.0), Shape(0.1, 0.35, 600), 60),
    ).spot(Vector(0.0, 1.0)) == (
        approx(500.0),
        approx(290.0),
    ), "a place to the north does not rise on the screen"


def test_reads_the_middle_of_the_window_as_the_origin():
    assert View(
        Surface((10, 10)),
        Settings(Limits(2.0, 4.0, 1.8, 8.0), Window(1000, 700, 60.0), Shape(0.1, 0.35, 600), 60),
    ).place((500, 350)) == Vector(
        approx(0.0), approx(0.0)
    ), "the middle of the window does not read as the origin"


def test_reads_a_pixel_right_of_the_middle_as_an_eastern_place():
    assert View(
        Surface((10, 10)),
        Settings(Limits(2.0, 4.0, 1.8, 8.0), Window(1000, 700, 60.0), Shape(0.1, 0.35, 600), 60),
    ).place((560, 350)) == Vector(
        approx(1.0), approx(0.0)
    ), "a pixel to the right does not read as a place to the east"


def test_reads_a_pixel_above_the_middle_as_a_northern_place():
    assert View(
        Surface((10, 10)),
        Settings(Limits(2.0, 4.0, 1.8, 8.0), Window(1000, 700, 60.0), Shape(0.1, 0.35, 600), 60),
    ).place((500, 290)) == Vector(
        approx(0.0), approx(1.0)
    ), "a pixel above the middle does not read as a place to the north"


def test_reads_back_the_place_it_drew():
    assert View(
        Surface((10, 10)),
        Settings(Limits(2.0, 4.0, 1.8, 8.0), Window(1000, 700, 60.0), Shape(0.1, 0.35, 600), 60),
    ).place(
        View(
            Surface((10, 10)),
            Settings(
                Limits(2.0, 4.0, 1.8, 8.0), Window(1000, 700, 60.0), Shape(0.1, 0.35, 600), 60
            ),
        ).spot(Vector(1.5, -2.25))
    ) == Vector(approx(1.5), approx(-2.25)), "a drawn place does not read back the same"
