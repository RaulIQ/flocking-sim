from math import cos, pi, sin
from random import uniform

from geometry_msgs.msg import Pose, PoseStamped, Quaternion, Twist, TwistStamped, Vector3
from pytest import approx
from sensor_msgs.msg import NavSatFix

from agent.command import Command
from agent.senses import Motion, Senses
from agent.signals import Bearing, Range, Role, Signals
from agent.vector import Vector
from autopilot.spot import Spot
from ground import Census, Post


def test_places_a_copter_at_its_metres_from_the_origin():
    origin = Spot(uniform(-60.0, 60.0), uniform(-170.0, 170.0))
    place = Vector(uniform(-20.0, 20.0), uniform(-20.0, 20.0))
    assert Census(origin, 1).bodies(
        {
            1: {
                "fix": NavSatFix(
                    latitude=origin.shifted(place).latitude,
                    longitude=origin.shifted(place).longitude,
                ),
                "pose": PoseStamped(),
                "motion": TwistStamped(),
            }
        }
    )[0].position == Vector(
        approx(place.x, abs=1e-6), approx(place.y, abs=1e-6)
    ), "a copter is not placed at its metres from the origin"


def test_heads_a_copter_where_its_attitude_points_from_the_east():
    heading = uniform(0.0, 2.0 * pi)
    assert Census(Spot(uniform(-60.0, 60.0), uniform(-170.0, 170.0)), 1).bodies(
        {
            1: {
                "fix": NavSatFix(),
                "pose": PoseStamped(
                    pose=Pose(orientation=Quaternion(z=sin(heading / 2.0), w=cos(heading / 2.0)))
                ),
                "motion": TwistStamped(),
            }
        }
    )[0].heading == approx(heading), "a copter does not head where its attitude points"


def test_moves_a_copter_east_along_x_and_north_along_y():
    east = uniform(-2.0, 2.0)
    north = uniform(-2.0, 2.0)
    assert Census(Spot(uniform(-60.0, 60.0), uniform(-170.0, 170.0)), 1).bodies(
        {
            1: {
                "fix": NavSatFix(),
                "pose": PoseStamped(),
                "motion": TwistStamped(twist=Twist(linear=Vector3(x=east, y=north))),
            }
        }
    )[0].velocity == Vector(
        approx(east), approx(north)
    ), "a copter does not move east along x and north along y"


def test_turns_a_copter_counterclockwise():
    spin = uniform(-1.5, 1.5)
    assert Census(Spot(uniform(-60.0, 60.0), uniform(-170.0, 170.0)), 1).bodies(
        {
            1: {
                "fix": NavSatFix(),
                "pose": PoseStamped(),
                "motion": TwistStamped(twist=Twist(angular=Vector3(z=spin))),
            }
        }
    )[0].spin == approx(spin), "a copter does not turn counterclockwise"


def test_counts_every_copter_in_its_order():
    origin = Spot(uniform(-60.0, 60.0), uniform(-170.0, 170.0))
    assert [
        round(body.position.x, 3)
        for body in Census(origin, 3).bodies(
            {
                number: {
                    "fix": NavSatFix(
                        latitude=origin.shifted(Vector(float(number), 0.0)).latitude,
                        longitude=origin.shifted(Vector(float(number), 0.0)).longitude,
                    ),
                    "pose": PoseStamped(),
                    "motion": TwistStamped(),
                }
                for number in (3, 1, 2)
            }
        )
    ] == [1.0, 2.0, 3.0], "the copters are not counted in their order"


def test_cannot_count_a_copter_not_heard_of_in_full():
    assert not Census(Spot(uniform(-60.0, 60.0), uniform(-170.0, 170.0)), 2).complete(
        {
            1: {"fix": NavSatFix(), "pose": PoseStamped(), "motion": TwistStamped()},
            2: {"fix": NavSatFix(), "pose": PoseStamped()},
        }
    ), "a copter is counted before all of it is heard"


def test_counts_once_every_copter_is_heard_of_in_full():
    assert Census(Spot(uniform(-60.0, 60.0), uniform(-170.0, 170.0)), 2).complete(
        {
            number: {"fix": NavSatFix(), "pose": PoseStamped(), "motion": TwistStamped()}
            for number in (1, 2)
        }
    ), "the copters are not counted once all of them are heard"


def test_tells_a_drone_whether_it_leads():
    leader = uniform(0.0, 1.0) < 0.5
    assert (
        Post(
            Senses(Motion(Vector(0.0, 0.0), 0.0), Signals((), (), ()), (), Command(Vector(0.0, 0.0), 0.0)),
            leader,
        )
        .message()
        .leader
        == leader
    ), "a drone is not told whether it leads"


def test_tells_a_drone_how_far_its_neighbours_are():
    assert [
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
    ] == [(2, 1.25), (5, 3.5)], "a drone is not told how far its neighbours are"


def test_tells_a_drone_where_it_sees_its_neighbours():
    assert [
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
    ] == [(2, 0.75), (5, -2.5)], "a drone is not told where it sees its neighbours"


def test_tells_a_drone_who_leads_among_its_neighbours():
    assert [
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
    ] == [(2, True), (5, False)], "a drone is not told who leads among its neighbours"


def test_tells_a_drone_where_the_walls_are():
    assert [
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
    ] == [(0.5, -1.25), (-3.0, 2.0)], "a drone is not told where the walls are"


def test_tells_a_drone_what_the_pilot_asks():
    message = Post(
        Senses(
            Motion(Vector(0.0, 0.0), 0.0),
            Signals((), (), ()),
            (),
            Command(Vector(1.5, -0.25), 0.75),
        ),
        True,
    ).message()
    assert (message.request.linear.x, message.request.linear.y, message.request.angular.z) == (
        1.5,
        -0.25,
        0.75,
    ), "a drone is not told what the pilot asks"
