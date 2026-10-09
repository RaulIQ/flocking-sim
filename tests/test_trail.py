from simulator.trail import Trail
from simulator.vector import Vector


def test_remembers_a_fresh_point():
    assert Trail((), 3).extended(Vector(1.5, -2.25)).points == (
        Vector(1.5, -2.25),
    ), "a trail does not remember a fresh point"


def test_keeps_the_oldest_point_first():
    assert Trail((), 3).extended(Vector(1.0, 0.0)).extended(
        Vector(2.0, 0.0)
    ).points == (
        Vector(1.0, 0.0),
        Vector(2.0, 0.0),
    ), "a trail does not keep its points in order"


def test_forgets_the_oldest_point_beyond_the_limit():
    assert Trail((Vector(1.0, 0.0), Vector(2.0, 0.0)), 2).extended(
        Vector(3.0, 0.0)
    ).points == (
        Vector(2.0, 0.0),
        Vector(3.0, 0.0),
    ), "a full trail does not drop its oldest point"


def test_cannot_grow_past_the_limit():
    assert len(
        Trail((Vector(1.0, 0.0), Vector(2.0, 0.0)), 2).extended(Vector(3.0, 0.0)).points
    ) == 2, "a trail grows past its limit"


def test_cannot_remember_anything_without_a_limit():
    assert Trail((), 0).extended(Vector(1.5, -2.25)).points == (), (
        "a trail without a limit still remembers a point"
    )
