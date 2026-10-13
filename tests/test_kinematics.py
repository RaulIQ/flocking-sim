from pytest import approx, raises

from agent.command import Command
from agent.tuning import Limits
from agent.vector import Vector
from simulator.body import Body
from simulator.kinematics import Kinematics


def test_moves_every_body_by_its_own_command():
    assert [
        body.position
        for body in Kinematics(Limits(2.0, 100.0, 1.8, 8.0), 0.5).moved(
            (
                Body(Vector(0.4, -0.7), 0.0, Vector(0.0, 0.0), 0.0),
                Body(Vector(3.1, 2.2), 0.0, Vector(0.0, 0.0), 0.0),
            ),
            (Command(Vector(2.0, 0.0), 0.0), Command(Vector(0.0, -1.0), 0.0)),
        )
    ] == [
        Vector(approx(1.4), approx(-0.7)),
        Vector(approx(3.1), approx(1.7)),
    ], "a body does not move by its own command"


def test_cannot_move_a_body_that_has_no_command():
    with raises(ValueError):
        Kinematics(Limits(2.0, 100.0, 1.8, 8.0), 0.5).moved(
            (
                Body(Vector(0.4, -0.7), 0.0, Vector(0.0, 0.0), 0.0),
                Body(Vector(3.1, 2.2), 0.0, Vector(0.0, 0.0), 0.0),
            ),
            (Command(Vector(2.0, 0.0), 0.0),),
        )
