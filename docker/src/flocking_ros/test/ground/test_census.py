from math import cos, pi, sin
from random import uniform

from agent.vector import Vector
from autopilot.spot import Spot
from flocking_ros.ground.census import Census
from geometry_msgs.msg import Point, Pose, PoseStamped, Quaternion, Twist, TwistStamped, Vector3
from hamcrest import assert_that, close_to, contains_exactly, is_
from sensor_msgs.msg import NavSatFix


def test_places_a_copter_east_of_the_origin_by_its_metres():
    origin = Spot(uniform(-60.0, 60.0), uniform(-170.0, 170.0))
    place = Vector(uniform(-20.0, 20.0), uniform(-20.0, 20.0))
    assert_that(
        Census(origin, 1).bodies(
            {
                1: {
                    'fix': NavSatFix(
                        latitude=origin.shifted(place).latitude,
                        longitude=origin.shifted(place).longitude,
                    ),
                    'pose': PoseStamped(),
                    'motion': TwistStamped(),
                }
            }
        )[0].position.x,
        close_to(place.x, 1e-6),
        'a copter is not placed east of the origin by its metres',
    )


def test_places_a_copter_north_of_the_origin_by_its_metres():
    origin = Spot(uniform(-60.0, 60.0), uniform(-170.0, 170.0))
    place = Vector(uniform(-20.0, 20.0), uniform(-20.0, 20.0))
    assert_that(
        Census(origin, 1).bodies(
            {
                1: {
                    'fix': NavSatFix(
                        latitude=origin.shifted(place).latitude,
                        longitude=origin.shifted(place).longitude,
                    ),
                    'pose': PoseStamped(),
                    'motion': TwistStamped(),
                }
            }
        )[0].position.y,
        close_to(place.y, 1e-6),
        'a copter is not placed north of the origin by its metres',
    )


def test_heads_a_copter_where_its_attitude_points_from_the_east():
    heading = uniform(0.0, 2.0 * pi)
    assert_that(
        Census(Spot(uniform(-60.0, 60.0), uniform(-170.0, 170.0)), 1).bodies(
            {
                1: {
                    'fix': NavSatFix(),
                    'pose': PoseStamped(
                        pose=Pose(
                            orientation=Quaternion(z=sin(heading / 2.0), w=cos(heading / 2.0))
                        )
                    ),
                    'motion': TwistStamped(),
                }
            }
        )[0].heading,
        close_to(heading, 1e-9),
        'a copter does not head where its attitude points',
    )


def test_moves_a_copter_east_along_x_and_north_along_y():
    east = uniform(-2.0, 2.0)
    north = uniform(-2.0, 2.0)
    body = Census(Spot(uniform(-60.0, 60.0), uniform(-170.0, 170.0)), 1).bodies(
        {
            1: {
                'fix': NavSatFix(),
                'pose': PoseStamped(),
                'motion': TwistStamped(twist=Twist(linear=Vector3(x=east, y=north))),
            }
        }
    )[0]
    assert_that(
        (body.velocity.x, body.velocity.y),
        contains_exactly(close_to(east, 1e-9), close_to(north, 1e-9)),
        'a copter does not move east along x and north along y',
    )


def test_turns_a_copter_counterclockwise():
    spin = uniform(-1.5, 1.5)
    assert_that(
        Census(Spot(uniform(-60.0, 60.0), uniform(-170.0, 170.0)), 1).bodies(
            {
                1: {
                    'fix': NavSatFix(),
                    'pose': PoseStamped(),
                    'motion': TwistStamped(twist=Twist(angular=Vector3(z=spin))),
                }
            }
        )[0].spin,
        close_to(spin, 1e-9),
        'a copter does not turn counterclockwise',
    )


def test_counts_every_copter_in_its_order():
    origin = Spot(uniform(-60.0, 60.0), uniform(-170.0, 170.0))
    assert_that(
        [
            round(body.position.x, 3)
            for body in Census(origin, 3).bodies(
                {
                    number: {
                        'fix': NavSatFix(
                            latitude=origin.shifted(Vector(float(number), 0.0)).latitude,
                            longitude=origin.shifted(Vector(float(number), 0.0)).longitude,
                        ),
                        'pose': PoseStamped(),
                        'motion': TwistStamped(),
                    }
                    for number in (3, 1, 2)
                }
            )
        ],
        contains_exactly(1.0, 2.0, 3.0),
        'the copters are not counted in their order',
    )


def test_cannot_count_a_copter_not_heard_of_in_full():
    assert_that(
        Census(Spot(uniform(-60.0, 60.0), uniform(-170.0, 170.0)), 2).complete(
            {
                1: {'fix': NavSatFix(), 'pose': PoseStamped(), 'motion': TwistStamped()},
                2: {'fix': NavSatFix(), 'pose': PoseStamped()},
            }
        ),
        is_(False),
        'a copter is counted before all of it is heard',
    )


def test_counts_once_every_copter_is_heard_of_in_full():
    assert_that(
        Census(Spot(uniform(-60.0, 60.0), uniform(-170.0, 170.0)), 2).complete(
            {
                number: {'fix': NavSatFix(), 'pose': PoseStamped(), 'motion': TwistStamped()}
                for number in (1, 2)
            }
        ),
        is_(True),
        'the copters are not counted once all of them are heard',
    )


def test_cannot_call_the_cloud_airborne_while_a_copter_climbs():
    assert_that(
        Census(Spot(uniform(-60.0, 60.0), uniform(-170.0, 170.0)), 2).airborne(
            {
                1: {'pose': PoseStamped(pose=Pose(position=Point(z=2.95)))},
                2: {'pose': PoseStamped(pose=Pose(position=Point(z=1.5)))},
            },
            3.0,
        ),
        is_(False),
        'the cloud is called airborne while a copter still climbs',
    )


def test_calls_the_cloud_airborne_once_every_copter_is_up():
    assert_that(
        Census(Spot(uniform(-60.0, 60.0), uniform(-170.0, 170.0)), 2).airborne(
            {
                1: {'pose': PoseStamped(pose=Pose(position=Point(z=2.95)))},
                2: {'pose': PoseStamped(pose=Pose(position=Point(z=2.75)))},
            },
            3.0,
        ),
        is_(True),
        'the cloud is not called airborne with every copter up',
    )
