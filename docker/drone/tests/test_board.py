from random import uniform

from geometry_msgs.msg import Twist, Vector3
from mavros_msgs.msg import PositionTarget
from pytest import approx

from agent.command import Command
from agent.instinct import Instinct
from agent.mind import Mind
from agent.shield import Shield
from agent.tracker import Tracker
from agent.tracks import Tracks
from agent.tuning import Cloud, Limits, Spring
from agent.vector import Vector
from autopilot.hold import Hold
from board import Board


def test_feels_its_own_flight_forward_and_to_the_left():
    forward = uniform(-2.0, 2.0)
    left = uniform(-2.0, 2.0)
    assert Board(
        Mind(
            Instinct(Cloud(Spring(1.2, 0.5, 0.15, 1.0), Spring(1.2, 1.0, 0.4, 1.5), Spring(0.6, 1.0, 0.0, 0.0), 6), Limits(2.0, 4.0, 1.8, 8.0)),
            Shield(Limits(2.0, 4.0, 1.8, 8.0), 0.25, 0.05, 0.5),
            Tracker(0.05),
            True,
        ),
        Hold(3.0, 1.0, 1.0),
        Command(Vector(0.0, 0.0), 0.0),
    ).senses(Twist(linear=Vector3(x=forward, y=left, z=uniform(-1.0, 1.0)))).motion.velocity == Vector(
        approx(forward), approx(left)
    ), "a board does not feel its own flight forward and to the left"


def test_feels_its_own_turn_counterclockwise():
    spin = uniform(-1.5, 1.5)
    assert Board(
        Mind(
            Instinct(Cloud(Spring(1.2, 0.5, 0.15, 1.0), Spring(1.2, 1.0, 0.4, 1.5), Spring(0.6, 1.0, 0.0, 0.0), 6), Limits(2.0, 4.0, 1.8, 8.0)),
            Shield(Limits(2.0, 4.0, 1.8, 8.0), 0.25, 0.05, 0.5),
            Tracker(0.05),
            True,
        ),
        Hold(3.0, 1.0, 1.0),
        Command(Vector(0.0, 0.0), 0.0),
    ).senses(Twist(angular=Vector3(z=spin))).motion.spin == approx(
        spin
    ), "a board does not feel its own turn"


def test_hands_the_mind_the_request():
    request = Command(Vector(uniform(-2.0, 2.0), uniform(-2.0, 2.0)), uniform(-1.5, 1.5))
    assert Board(
        Mind(
            Instinct(Cloud(Spring(1.2, 0.5, 0.15, 1.0), Spring(1.2, 1.0, 0.4, 1.5), Spring(0.6, 1.0, 0.0, 0.0), 6), Limits(2.0, 4.0, 1.8, 8.0)),
            Shield(Limits(2.0, 4.0, 1.8, 8.0), 0.25, 0.05, 0.5),
            Tracker(0.05),
            True,
        ),
        Hold(3.0, 1.0, 1.0),
        request,
    ).senses(Twist()).request == request, "a board does not hand the mind the request"


def test_asks_for_the_speed_its_mind_decides_forward_and_to_the_left():
    board = Board(
        Mind(
            Instinct(Cloud(Spring(1.2, 0.5, 0.15, 1.0), Spring(1.2, 1.0, 0.4, 1.5), Spring(0.6, 1.0, 0.0, 0.0), 6), Limits(2.0, 4.0, 1.8, 8.0)),
            Shield(Limits(2.0, 4.0, 1.8, 8.0), 0.25, 0.05, 0.5),
            Tracker(0.05),
            True,
        ),
        Hold(3.0, 1.0, 1.0),
        Command(Vector(0.75, -0.4), 0.3),
    )
    target = board.target(Tracks(()), board.senses(Twist()), 3.0)
    assert (target.velocity.x, target.velocity.y, target.yaw_rate) == (
        approx(0.75),
        approx(-0.4),
        approx(0.3),
    ), "a board does not ask for the speed its mind decides"


def test_climbs_back_to_the_altitude():
    board = Board(
        Mind(
            Instinct(Cloud(Spring(1.2, 0.5, 0.15, 1.0), Spring(1.2, 1.0, 0.4, 1.5), Spring(0.6, 1.0, 0.0, 0.0), 6), Limits(2.0, 4.0, 1.8, 8.0)),
            Shield(Limits(2.0, 4.0, 1.8, 8.0), 0.25, 0.05, 0.5),
            Tracker(0.05),
            True,
        ),
        Hold(3.0, 0.8, 1.0),
        Command(Vector(0.0, 0.0), 0.0),
    )
    assert board.target(Tracks(()), board.senses(Twist()), 2.5).velocity.z == approx(
        0.4
    ), "a board does not climb back to its altitude"


def test_asks_in_the_frame_of_the_copter():
    board = Board(
        Mind(
            Instinct(Cloud(Spring(1.2, 0.5, 0.15, 1.0), Spring(1.2, 1.0, 0.4, 1.5), Spring(0.6, 1.0, 0.0, 0.0), 6), Limits(2.0, 4.0, 1.8, 8.0)),
            Shield(Limits(2.0, 4.0, 1.8, 8.0), 0.25, 0.05, 0.5),
            Tracker(0.05),
            True,
        ),
        Hold(3.0, 1.0, 1.0),
        Command(Vector(uniform(-2.0, 2.0), uniform(-2.0, 2.0)), uniform(-1.5, 1.5)),
    )
    assert (
        board.target(Tracks(()), board.senses(Twist()), 3.0).coordinate_frame
        == PositionTarget.FRAME_BODY_NED
    ), "a board does not ask in the frame of the copter"


def test_asks_for_the_speed_and_the_turn_alone():
    board = Board(
        Mind(
            Instinct(Cloud(Spring(1.2, 0.5, 0.15, 1.0), Spring(1.2, 1.0, 0.4, 1.5), Spring(0.6, 1.0, 0.0, 0.0), 6), Limits(2.0, 4.0, 1.8, 8.0)),
            Shield(Limits(2.0, 4.0, 1.8, 8.0), 0.25, 0.05, 0.5),
            Tracker(0.05),
            True,
        ),
        Hold(3.0, 1.0, 1.0),
        Command(Vector(uniform(-2.0, 2.0), uniform(-2.0, 2.0)), uniform(-1.5, 1.5)),
    )
    assert board.target(Tracks(()), board.senses(Twist()), 3.0).type_mask == (
        PositionTarget.IGNORE_PX
        | PositionTarget.IGNORE_PY
        | PositionTarget.IGNORE_PZ
        | PositionTarget.IGNORE_AFX
        | PositionTarget.IGNORE_AFY
        | PositionTarget.IGNORE_AFZ
        | PositionTarget.IGNORE_YAW
    ), "a board asks for more than the speed and the turn"
