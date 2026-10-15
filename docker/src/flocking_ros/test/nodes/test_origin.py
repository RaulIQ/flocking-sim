import subprocess

from config import copters, sortie
from hamcrest import assert_that, equal_to


def test_puts_every_drone_on_the_shared_origin():
    assert_that(
        subprocess.run(
            ['ros2', 'run', 'flocking_ros', 'origin'],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip(),
        equal_to(
            f'{sortie(copters()).hangar.fleet.origin.latitude:.7f},'
            f'{sortie(copters()).hangar.fleet.origin.longitude:.7f},0,90'
        ),
        'the drones do not start on the shared origin',
    )
