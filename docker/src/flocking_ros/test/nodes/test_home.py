from math import cos, radians
import subprocess

from config import copters, sortie
from hamcrest import assert_that, close_to, equal_to, is_not


def test_puts_the_first_drone_on_the_origin():
    assert_that(
        subprocess.run(
            ['ros2', 'run', 'flocking_ros', 'home', '1'],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip(),
        equal_to(
            f'{sortie(copters()).hangar.fleet.origin.latitude:.7f},'
            f'{sortie(copters()).hangar.fleet.origin.longitude:.7f},0,90'
        ),
        'the first drone does not start on the origin',
    )


def test_puts_the_second_drone_one_spacing_away():
    latitude, longitude, altitude, yaw = (
        float(part)
        for part in subprocess.run(
            ['ros2', 'run', 'flocking_ros', 'home', '2'],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.split(',')
    )
    origin = sortie(copters()).hangar.fleet.origin
    assert_that(
        (
            (radians(latitude - origin.latitude) * 6378100.0) ** 2
            + (
                radians(longitude - origin.longitude)
                * 6378100.0
                * cos(radians(origin.latitude))
            )
            ** 2
        )
        ** 0.5,
        close_to(copters().swarm.muster.spacing, 0.02),
        'the second drone does not start one spacing away',
    )


def test_cannot_place_a_drone_the_swarm_does_not_have():
    assert_that(
        subprocess.run(
            ['ros2', 'run', 'flocking_ros', 'home', str(copters().swarm.muster.count + 1)],
            capture_output=True,
            text=True,
        ).returncode,
        is_not(0),
        'a drone beyond the swarm still gets a place',
    )
