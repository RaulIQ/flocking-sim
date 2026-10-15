from random import uniform

from agent.tracks import Tracks
from autopilot.hold import Hold
from flocking_msgs.msg import Bearing, Range, Role, Senses
from geometry_msgs.msg import Point, Twist, Vector3
from hamcrest import assert_that, close_to, contains_exactly, equal_to, is_
from kit import Kit
from mavros_msgs.msg import PositionTarget


def test_feels_its_own_flight_forward():
    forward = uniform(-2.0, 2.0)
    assert_that(
        Kit(Hold(3.0, 1.0, 1.0))
        .board()
        .senses(Twist(linear=Vector3(x=forward, y=uniform(-2.0, 2.0))), Senses())
        .motion.velocity.x,
        close_to(forward, 1e-9),
        'a board does not feel its own flight forward',
    )


def test_feels_its_own_flight_to_the_left():
    left = uniform(-2.0, 2.0)
    assert_that(
        Kit(Hold(3.0, 1.0, 1.0))
        .board()
        .senses(Twist(linear=Vector3(x=uniform(-2.0, 2.0), y=left)), Senses())
        .motion.velocity.y,
        close_to(left, 1e-9),
        'a board does not feel its own flight to the left',
    )


def test_feels_its_own_turn_counterclockwise():
    spin = uniform(-1.5, 1.5)
    assert_that(
        Kit(Hold(3.0, 1.0, 1.0))
        .board()
        .senses(Twist(angular=Vector3(z=spin)), Senses())
        .motion.spin,
        close_to(spin, 1e-9),
        'a board does not feel its own turn',
    )


def test_hears_how_far_its_neighbours_are():
    assert_that(
        [
            (echo.tag, echo.distance)
            for echo in Kit(Hold(3.0, 1.0, 1.0))
            .board()
            .senses(
                Twist(),
                Senses(ranges=[Range(tag=3, distance=1.75), Range(tag=0, distance=2.5)]),
            )
            .signals.ranges
        ],
        contains_exactly((3, 1.75), (0, 2.5)),
        'a board does not hear how far its neighbours are',
    )


def test_sees_where_its_neighbours_are():
    assert_that(
        [
            (sight.tag, sight.angle)
            for sight in Kit(Hold(3.0, 1.0, 1.0))
            .board()
            .senses(
                Twist(),
                Senses(bearings=[Bearing(tag=3, angle=-0.5), Bearing(tag=0, angle=2.25)]),
            )
            .signals.bearings
        ],
        contains_exactly((3, -0.5), (0, 2.25)),
        'a board does not see where its neighbours are',
    )


def test_hears_who_leads_among_its_neighbours():
    assert_that(
        [
            (word.tag, word.leader)
            for word in Kit(Hold(3.0, 1.0, 1.0))
            .board()
            .senses(
                Twist(),
                Senses(roles=[Role(tag=3, leader=False), Role(tag=0, leader=True)]),
            )
            .signals.roles
        ],
        contains_exactly((3, False), (0, True)),
        'a board does not hear who leads',
    )


def test_feels_where_the_walls_are():
    assert_that(
        [
            (offset.x, offset.y)
            for offset in Kit(Hold(3.0, 1.0, 1.0))
            .board()
            .senses(Twist(), Senses(obstacles=[Point(x=1.5, y=-0.25), Point(x=-4.0, y=3.0)]))
            .obstacles
        ],
        contains_exactly((1.5, -0.25), (-4.0, 3.0)),
        'a board does not feel where the walls are',
    )


def test_hears_what_the_pilot_asks():
    request = (
        Kit(Hold(3.0, 1.0, 1.0))
        .board()
        .senses(
            Twist(), Senses(request=Twist(linear=Vector3(x=1.25, y=-0.5), angular=Vector3(z=0.75)))
        )
        .request
    )
    assert_that(
        (request.velocity.x, request.velocity.y, request.spin),
        equal_to((1.25, -0.5, 0.75)),
        'a board does not hear what the pilot asks',
    )


def test_flies_what_the_pilot_asks_once_told_it_leads():
    board = Kit(Hold(3.0, 1.0, 1.0)).board()
    target = board.target(
        Tracks(()),
        board.senses(
            Twist(),
            Senses(request=Twist(linear=Vector3(x=0.75, y=-0.4), angular=Vector3(z=0.3))),
        ),
        3.0,
        True,
    )
    assert_that(
        [round(value, 6) for value in (target.velocity.x, target.velocity.y, target.yaw_rate)],
        contains_exactly(0.75, -0.4, 0.3),
        'a leader does not fly what the pilot asks',
    )


def test_cannot_fly_what_the_pilot_asks_while_it_follows():
    board = Kit(Hold(3.0, 1.0, 1.0)).board()
    target = board.target(
        Tracks(()),
        board.senses(
            Twist(),
            Senses(request=Twist(linear=Vector3(x=0.75, y=-0.4), angular=Vector3(z=0.3))),
        ),
        3.0,
        False,
    )
    assert_that(
        [round(value, 6) for value in (target.velocity.x, target.velocity.y, target.yaw_rate)],
        contains_exactly(0.0, 0.0, 0.0),
        'a follower flies what the pilot asks',
    )


def test_climbs_back_to_the_altitude():
    board = Kit(Hold(3.0, 0.8, 1.0)).board()
    assert_that(
        board.target(Tracks(()), board.senses(Twist(), Senses()), 2.5, False).velocity.z,
        close_to(0.4, 1e-9),
        'a board does not climb back to its altitude',
    )


def test_asks_in_the_frame_of_the_copter():
    board = Kit(Hold(3.0, 1.0, 1.0)).board()
    assert_that(
        board.target(Tracks(()), board.senses(Twist(), Senses()), 3.0, uniform(0.0, 1.0) < 0.5)
        .coordinate_frame,
        is_(PositionTarget.FRAME_BODY_NED),
        'a board does not ask in the frame of the copter',
    )


def test_asks_for_the_speed_and_the_turn_alone():
    board = Kit(Hold(3.0, 1.0, 1.0)).board()
    assert_that(
        board.target(Tracks(()), board.senses(Twist(), Senses()), 3.0, uniform(0.0, 1.0) < 0.5)
        .type_mask,
        equal_to(
            PositionTarget.IGNORE_PX
            | PositionTarget.IGNORE_PY
            | PositionTarget.IGNORE_PZ
            | PositionTarget.IGNORE_AFX
            | PositionTarget.IGNORE_AFY
            | PositionTarget.IGNORE_AFZ
            | PositionTarget.IGNORE_YAW
        ),
        'a board asks for more than the speed and the turn',
    )
