from random import uniform

from flocking_msgs.msg import Bearing, Range, Role, Senses
from geometry_msgs.msg import Point, Twist, Vector3
from mavros_msgs.msg import PositionTarget
from pytest import approx

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
            False,
        ),
        Hold(3.0, 1.0, 1.0),
    ).senses(Twist(linear=Vector3(x=forward, y=left, z=uniform(-1.0, 1.0))), Senses()).motion.velocity == Vector(
        approx(forward), approx(left)
    ), "a board does not feel its own flight forward and to the left"


def test_feels_its_own_turn_counterclockwise():
    spin = uniform(-1.5, 1.5)
    assert Board(
        Mind(
            Instinct(Cloud(Spring(1.2, 0.5, 0.15, 1.0), Spring(1.2, 1.0, 0.4, 1.5), Spring(0.6, 1.0, 0.0, 0.0), 6), Limits(2.0, 4.0, 1.8, 8.0)),
            Shield(Limits(2.0, 4.0, 1.8, 8.0), 0.25, 0.05, 0.5),
            Tracker(0.05),
            False,
        ),
        Hold(3.0, 1.0, 1.0),
    ).senses(Twist(angular=Vector3(z=spin)), Senses()).motion.spin == approx(
        spin
    ), "a board does not feel its own turn"


def test_hears_how_far_its_neighbours_are():
    assert [
        (echo.tag, echo.distance)
        for echo in Board(
            Mind(
                Instinct(Cloud(Spring(1.2, 0.5, 0.15, 1.0), Spring(1.2, 1.0, 0.4, 1.5), Spring(0.6, 1.0, 0.0, 0.0), 6), Limits(2.0, 4.0, 1.8, 8.0)),
                Shield(Limits(2.0, 4.0, 1.8, 8.0), 0.25, 0.05, 0.5),
                Tracker(0.05),
                False,
            ),
            Hold(3.0, 1.0, 1.0),
        )
        .senses(Twist(), Senses(ranges=[Range(tag=3, distance=1.75), Range(tag=0, distance=2.5)]))
        .signals.ranges
    ] == [(3, 1.75), (0, 2.5)], "a board does not hear how far its neighbours are"


def test_sees_where_its_neighbours_are():
    assert [
        (sight.tag, sight.angle)
        for sight in Board(
            Mind(
                Instinct(Cloud(Spring(1.2, 0.5, 0.15, 1.0), Spring(1.2, 1.0, 0.4, 1.5), Spring(0.6, 1.0, 0.0, 0.0), 6), Limits(2.0, 4.0, 1.8, 8.0)),
                Shield(Limits(2.0, 4.0, 1.8, 8.0), 0.25, 0.05, 0.5),
                Tracker(0.05),
                False,
            ),
            Hold(3.0, 1.0, 1.0),
        )
        .senses(Twist(), Senses(bearings=[Bearing(tag=3, angle=-0.5), Bearing(tag=0, angle=2.25)]))
        .signals.bearings
    ] == [(3, -0.5), (0, 2.25)], "a board does not see where its neighbours are"


def test_hears_who_leads_among_its_neighbours():
    assert [
        (word.tag, word.leader)
        for word in Board(
            Mind(
                Instinct(Cloud(Spring(1.2, 0.5, 0.15, 1.0), Spring(1.2, 1.0, 0.4, 1.5), Spring(0.6, 1.0, 0.0, 0.0), 6), Limits(2.0, 4.0, 1.8, 8.0)),
                Shield(Limits(2.0, 4.0, 1.8, 8.0), 0.25, 0.05, 0.5),
                Tracker(0.05),
                False,
            ),
            Hold(3.0, 1.0, 1.0),
        )
        .senses(Twist(), Senses(roles=[Role(tag=3, leader=False), Role(tag=0, leader=True)]))
        .signals.roles
    ] == [(3, False), (0, True)], "a board does not hear who leads"


def test_feels_where_the_walls_are():
    assert Board(
        Mind(
            Instinct(Cloud(Spring(1.2, 0.5, 0.15, 1.0), Spring(1.2, 1.0, 0.4, 1.5), Spring(0.6, 1.0, 0.0, 0.0), 6), Limits(2.0, 4.0, 1.8, 8.0)),
            Shield(Limits(2.0, 4.0, 1.8, 8.0), 0.25, 0.05, 0.5),
            Tracker(0.05),
            False,
        ),
        Hold(3.0, 1.0, 1.0),
    ).senses(Twist(), Senses(obstacles=[Point(x=1.5, y=-0.25), Point(x=-4.0, y=3.0)])).obstacles == (
        Vector(1.5, -0.25),
        Vector(-4.0, 3.0),
    ), "a board does not feel where the walls are"


def test_hears_what_the_pilot_asks():
    request = Board(
        Mind(
            Instinct(Cloud(Spring(1.2, 0.5, 0.15, 1.0), Spring(1.2, 1.0, 0.4, 1.5), Spring(0.6, 1.0, 0.0, 0.0), 6), Limits(2.0, 4.0, 1.8, 8.0)),
            Shield(Limits(2.0, 4.0, 1.8, 8.0), 0.25, 0.05, 0.5),
            Tracker(0.05),
            False,
        ),
        Hold(3.0, 1.0, 1.0),
    ).senses(
        Twist(), Senses(request=Twist(linear=Vector3(x=1.25, y=-0.5), angular=Vector3(z=0.75)))
    ).request
    assert (request.velocity.x, request.velocity.y, request.spin) == (
        1.25,
        -0.5,
        0.75,
    ), "a board does not hear what the pilot asks"


def test_flies_what_the_pilot_asks_once_told_it_leads():
    board = Board(
        Mind(
            Instinct(Cloud(Spring(1.2, 0.5, 0.15, 1.0), Spring(1.2, 1.0, 0.4, 1.5), Spring(0.6, 1.0, 0.0, 0.0), 6), Limits(2.0, 4.0, 1.8, 8.0)),
            Shield(Limits(2.0, 4.0, 1.8, 8.0), 0.25, 0.05, 0.5),
            Tracker(0.05),
            False,
        ),
        Hold(3.0, 1.0, 1.0),
    )
    letter = Senses(
        leader=True, request=Twist(linear=Vector3(x=0.75, y=-0.4), angular=Vector3(z=0.3))
    )
    target = board.target(Tracks(()), board.senses(Twist(), letter), 3.0, letter.leader)
    assert (target.velocity.x, target.velocity.y, target.yaw_rate) == (
        approx(0.75),
        approx(-0.4),
        approx(0.3),
    ), "a leader does not fly what the pilot asks"


def test_cannot_fly_what_the_pilot_asks_while_it_follows():
    board = Board(
        Mind(
            Instinct(Cloud(Spring(1.2, 0.5, 0.15, 1.0), Spring(1.2, 1.0, 0.4, 1.5), Spring(0.6, 1.0, 0.0, 0.0), 6), Limits(2.0, 4.0, 1.8, 8.0)),
            Shield(Limits(2.0, 4.0, 1.8, 8.0), 0.25, 0.05, 0.5),
            Tracker(0.05),
            True,
        ),
        Hold(3.0, 1.0, 1.0),
    )
    letter = Senses(
        leader=False, request=Twist(linear=Vector3(x=0.75, y=-0.4), angular=Vector3(z=0.3))
    )
    target = board.target(Tracks(()), board.senses(Twist(), letter), 3.0, letter.leader)
    assert (target.velocity.x, target.velocity.y, target.yaw_rate) == (
        approx(0.0),
        approx(0.0),
        approx(0.0),
    ), "a follower flies what the pilot asks"


def test_climbs_back_to_the_altitude():
    board = Board(
        Mind(
            Instinct(Cloud(Spring(1.2, 0.5, 0.15, 1.0), Spring(1.2, 1.0, 0.4, 1.5), Spring(0.6, 1.0, 0.0, 0.0), 6), Limits(2.0, 4.0, 1.8, 8.0)),
            Shield(Limits(2.0, 4.0, 1.8, 8.0), 0.25, 0.05, 0.5),
            Tracker(0.05),
            False,
        ),
        Hold(3.0, 0.8, 1.0),
    )
    assert board.target(Tracks(()), board.senses(Twist(), Senses()), 2.5, False).velocity.z == approx(
        0.4
    ), "a board does not climb back to its altitude"


def test_asks_in_the_frame_of_the_copter():
    board = Board(
        Mind(
            Instinct(Cloud(Spring(1.2, 0.5, 0.15, 1.0), Spring(1.2, 1.0, 0.4, 1.5), Spring(0.6, 1.0, 0.0, 0.0), 6), Limits(2.0, 4.0, 1.8, 8.0)),
            Shield(Limits(2.0, 4.0, 1.8, 8.0), 0.25, 0.05, 0.5),
            Tracker(0.05),
            False,
        ),
        Hold(3.0, 1.0, 1.0),
    )
    assert (
        board.target(Tracks(()), board.senses(Twist(), Senses()), 3.0, uniform(0.0, 1.0) < 0.5).coordinate_frame
        == PositionTarget.FRAME_BODY_NED
    ), "a board does not ask in the frame of the copter"


def test_asks_for_the_speed_and_the_turn_alone():
    board = Board(
        Mind(
            Instinct(Cloud(Spring(1.2, 0.5, 0.15, 1.0), Spring(1.2, 1.0, 0.4, 1.5), Spring(0.6, 1.0, 0.0, 0.0), 6), Limits(2.0, 4.0, 1.8, 8.0)),
            Shield(Limits(2.0, 4.0, 1.8, 8.0), 0.25, 0.05, 0.5),
            Tracker(0.05),
            False,
        ),
        Hold(3.0, 1.0, 1.0),
    )
    assert board.target(Tracks(()), board.senses(Twist(), Senses()), 3.0, uniform(0.0, 1.0) < 0.5).type_mask == (
        PositionTarget.IGNORE_PX
        | PositionTarget.IGNORE_PY
        | PositionTarget.IGNORE_PZ
        | PositionTarget.IGNORE_AFX
        | PositionTarget.IGNORE_AFY
        | PositionTarget.IGNORE_AFZ
        | PositionTarget.IGNORE_YAW
    ), "a board asks for more than the speed and the turn"
