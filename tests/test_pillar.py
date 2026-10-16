from random import uniform

from pytest import approx

from agent.vector import Vector
from simulator.pillar import Pillar


def test_finds_the_point_of_its_side_facing_a_place():
    radius = uniform(0.3, 1.0)
    assert Pillar(Vector(4.0, 1.0), radius).nearest(Vector(1.0, 1.0)) == Vector(
        approx(4.0 - radius), approx(1.0)
    ), "a pillar does not find the point of its side facing a place"


def test_keeps_the_nearest_point_on_its_side():
    radius = uniform(0.3, 1.0)
    centre = Vector(uniform(-3.0, 3.0), uniform(-3.0, 3.0))
    assert Pillar(centre, radius).nearest(
        Vector(uniform(-6.0, 6.0), uniform(-6.0, 6.0))
    ).minus(centre).length() == approx(radius), "the nearest point of a pillar leaves its side"


def test_pushes_a_place_inside_it_out_to_its_side():
    assert Pillar(Vector(4.0, 1.0), 0.6).nearest(Vector(4.2, 1.0)) == Vector(
        approx(4.6), approx(1.0)
    ), "a pillar does not push a place inside it out to its side"


def test_finds_a_point_of_its_side_for_its_own_centre():
    assert Pillar(Vector(4.0, 1.0), 0.6).nearest(Vector(4.0, 1.0)).minus(
        Vector(4.0, 1.0)
    ).length() == approx(0.6), "a pillar finds no point of its side for its own centre"
