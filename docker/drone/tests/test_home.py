import subprocess
from math import cos, radians

from pytest import approx

from config import copters, sortie


def test_puts_the_first_drone_on_the_origin():
    assert subprocess.run(
        ["python3", "docker/drone/nodes/home.py", "1"], capture_output=True, text=True, check=True
    ).stdout.strip() == (
        f"{sortie(copters()).hangar.fleet.origin.latitude:.7f},"
        f"{sortie(copters()).hangar.fleet.origin.longitude:.7f},0,90"
    ), "the first drone does not start on the origin"


def test_puts_the_second_drone_one_spacing_away():
    latitude, longitude, altitude, yaw = (
        float(part)
        for part in subprocess.run(
            ["python3", "docker/drone/nodes/home.py", "2"], capture_output=True, text=True, check=True
        ).stdout.split(",")
    )
    origin = sortie(copters()).hangar.fleet.origin
    assert (
        (
            (radians(latitude - origin.latitude) * 6378100.0) ** 2
            + (radians(longitude - origin.longitude) * 6378100.0 * cos(radians(origin.latitude))) ** 2
        )
        ** 0.5
    ) == approx(copters().swarm.muster.spacing, abs=0.02), "the second drone does not start one spacing away"


def test_cannot_place_a_drone_the_swarm_does_not_have():
    assert (
        subprocess.run(
            ["python3", "docker/drone/nodes/home.py", str(copters().swarm.muster.count + 1)],
            capture_output=True,
            text=True,
        ).returncode
        != 0
    ), "a drone beyond the swarm still gets a place"
