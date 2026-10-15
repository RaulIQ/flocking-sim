from random import uniform

from agent.command import Command
from agent.senses import Motion, Senses
from agent.signals import Bearing, Range, Role, Signals
from agent.vector import Vector
from flocking_ros.ground.post import Post
from hamcrest import assert_that, contains_exactly, is_


def test_tells_a_drone_whether_it_leads():
    leader = uniform(0.0, 1.0) < 0.5
    assert_that(
        Post(
            Senses(
                Motion(Vector(0.0, 0.0), 0.0),
                Signals((), (), ()),
                (),
                Command(Vector(0.0, 0.0), 0.0),
            ),
            leader,
        )
        .message()
        .leader,
        is_(leader),
        'a drone is not told whether it leads',
    )


def test_tells_a_drone_how_far_its_neighbours_are():
    assert_that(
        [
            (echo.tag, echo.distance)
            for echo in Post(
                Senses(
                    Motion(Vector(0.0, 0.0), 0.0),
                    Signals((Range(2, 1.25), Range(5, 3.5)), (), ()),
                    (),
                    Command(Vector(0.0, 0.0), 0.0),
                ),
                False,
            )
            .message()
            .ranges
        ],
        contains_exactly((2, 1.25), (5, 3.5)),
        'a drone is not told how far its neighbours are',
    )


def test_tells_a_drone_where_it_sees_its_neighbours():
    assert_that(
        [
            (sight.tag, sight.angle)
            for sight in Post(
                Senses(
                    Motion(Vector(0.0, 0.0), 0.0),
                    Signals((), (Bearing(2, 0.75), Bearing(5, -2.5)), ()),
                    (),
                    Command(Vector(0.0, 0.0), 0.0),
                ),
                False,
            )
            .message()
            .bearings
        ],
        contains_exactly((2, 0.75), (5, -2.5)),
        'a drone is not told where it sees its neighbours',
    )


def test_tells_a_drone_who_leads_among_its_neighbours():
    assert_that(
        [
            (word.tag, word.leader)
            for word in Post(
                Senses(
                    Motion(Vector(0.0, 0.0), 0.0),
                    Signals((), (), (Role(2, True), Role(5, False))),
                    (),
                    Command(Vector(0.0, 0.0), 0.0),
                ),
                False,
            )
            .message()
            .roles
        ],
        contains_exactly((2, True), (5, False)),
        'a drone is not told who leads among its neighbours',
    )


def test_tells_a_drone_where_the_walls_are():
    assert_that(
        [
            (point.x, point.y)
            for point in Post(
                Senses(
                    Motion(Vector(0.0, 0.0), 0.0),
                    Signals((), (), ()),
                    (Vector(0.5, -1.25), Vector(-3.0, 2.0)),
                    Command(Vector(0.0, 0.0), 0.0),
                ),
                False,
            )
            .message()
            .obstacles
        ],
        contains_exactly((0.5, -1.25), (-3.0, 2.0)),
        'a drone is not told where the walls are',
    )


def test_tells_a_drone_what_the_pilot_asks():
    request = (
        Post(
            Senses(
                Motion(Vector(0.0, 0.0), 0.0),
                Signals((), (), ()),
                (),
                Command(Vector(1.5, -0.25), 0.75),
            ),
            True,
        )
        .message()
        .request
    )
    assert_that(
        (request.linear.x, request.linear.y, request.angular.z),
        contains_exactly(1.5, -0.25, 0.75),
        'a drone is not told what the pilot asks',
    )
