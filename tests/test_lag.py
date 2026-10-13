from collections import deque

from pytest import approx, raises

from agent.command import Command
from agent.tuning import Limits
from agent.vector import Vector
from simulator.body import Body
from simulator.kinematics import Kinematics
from simulator.lag import Lag


def test_holds_a_command_back_for_its_wait():
    lag = Lag(Kinematics(Limits(9.0, 900.0, 9.0, 900.0), 1.0), deque(), 2, 1.0)
    assert [
        lag.moved(
            (Body(Vector(0.0, 0.0), 0.0, Vector(0.0, 0.0), 0.0),),
            (Command(Vector(1.5, 0.0), 0.0),),
        )[0].velocity.x
        for tick in range(4)
    ] == [0.0, 0.0, approx(1.5), approx(1.5)], "a command does not wait its turn"


def test_eases_a_command_in_by_its_share_every_tick():
    lag = Lag(Kinematics(Limits(9.0, 900.0, 9.0, 900.0), 1.0), deque(), 0, 0.5)
    assert [
        lag.moved(
            (Body(Vector(0.0, 0.0), 0.0, Vector(0.0, 0.0), 0.0),),
            (Command(Vector(2.0, 0.0), 0.0),),
        )[0].velocity.x
        for tick in range(3)
    ] == [approx(1.0), approx(1.5), approx(1.75)], "a command is not eased in"


def test_eases_the_spin_in_as_well():
    lag = Lag(Kinematics(Limits(9.0, 900.0, 9.0, 900.0), 1.0), deque(), 0, 0.25)
    assert lag.moved(
        (Body(Vector(0.0, 0.0), 0.0, Vector(0.0, 0.0), 0.0),),
        (Command(Vector(0.0, 0.0), 2.0),),
    )[0].spin == approx(0.5), "the spin is not eased in"


def test_keeps_a_line_of_its_own_for_every_drone():
    lag = Lag(Kinematics(Limits(9.0, 900.0, 9.0, 900.0), 1.0), deque(), 1, 1.0)
    lag.moved(
        (
            Body(Vector(0.0, 0.0), 0.0, Vector(0.0, 0.0), 0.0),
            Body(Vector(5.0, 5.0), 0.0, Vector(0.0, 0.0), 0.0),
        ),
        (Command(Vector(1.0, 0.0), 0.0), Command(Vector(-2.0, 0.0), 0.0)),
    )
    assert [
        body.velocity.x
        for body in lag.moved(
            (
                Body(Vector(0.0, 0.0), 0.0, Vector(0.0, 0.0), 0.0),
                Body(Vector(5.0, 5.0), 0.0, Vector(0.0, 0.0), 0.0),
            ),
            (Command(Vector(0.0, 0.0), 0.0), Command(Vector(0.0, 0.0), 0.0)),
        )
    ] == [approx(1.0), approx(-2.0)], "the drones share one line of commands"


def test_passes_a_command_straight_on_with_no_wait_and_a_full_share():
    assert Lag(
        Kinematics(Limits(9.0, 900.0, 9.0, 900.0), 1.0), deque(), 0, 1.0
    ).moved(
        (Body(Vector(0.0, 0.0), 0.0, Vector(0.0, 0.0), 0.0),),
        (Command(Vector(1.25, -0.5), 0.0),),
    )[0].velocity == Vector(
        approx(1.25), approx(-0.5)
    ), "a lag with nothing to add still changes the command"


def test_cannot_ease_commands_for_a_changed_number_of_drones():
    lag = Lag(Kinematics(Limits(9.0, 900.0, 9.0, 900.0), 1.0), deque(), 0, 0.5)
    lag.moved(
        (Body(Vector(0.0, 0.0), 0.0, Vector(0.0, 0.0), 0.0),),
        (Command(Vector(1.0, 0.0), 0.0),),
    )
    with raises(ValueError):
        lag.moved(
            (
                Body(Vector(0.0, 0.0), 0.0, Vector(0.0, 0.0), 0.0),
                Body(Vector(5.0, 5.0), 0.0, Vector(0.0, 0.0), 0.0),
            ),
            (Command(Vector(1.0, 0.0), 0.0), Command(Vector(1.0, 0.0), 0.0)),
        )
