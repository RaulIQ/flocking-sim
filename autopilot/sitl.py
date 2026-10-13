from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from shutil import copy
from subprocess import STDOUT, Popen
from typing import final

from pymavlink import mavutil

from autopilot.fleet import Fleet
from autopilot.link import Link
from autopilot.spot import Spot


@final
@dataclass(frozen=True)
class Sitl:
    """One copter that ArduPilot simulates on this machine, standing at its home.

    The copter starts with the nose to the east, where the kinematic drones
    look at the start, with its memory wiped and with no MAVProxy in front of
    it. Its fleet tunes it with a frame and with parameters laid over the
    defaults of the copter. ArduPilot reads a frame only from the folder a
    copter runs in, so the frame is brought there first. The copter keeps its
    files in that folder of its own and runs only while asked.
    """

    fleet: Fleet
    number: int
    home: Spot

    def port(self) -> int:
        return self.fleet.port + 10 * self.number

    def words(self) -> tuple:
        return (
            str(self.fleet.source / "build" / "sitl" / "bin" / "arducopter"),
            "--wipe",
            "--model",
            "+:frame.json",
            "--speedup",
            "1",
            "--base-port",
            str(self.fleet.port),
            "-I",
            str(self.number),
            "--sysid",
            str(self.number + 1),
            "--home",
            f"{self.home.latitude:.7f},{self.home.longitude:.7f},0,90",
            "--defaults",
            f"{self.fleet.source / 'Tools' / 'autotest' / 'default_params' / 'copter.parm'}"
            f",{self.fleet.tuning / 'copter.parm'}",
        )

    def link(self) -> Link:
        return Link(
            mavutil.mavlink_connection(f"tcp:127.0.0.1:{self.port()}"),
            self.number + 1,
        )

    @contextmanager
    def running(self, folder: Path):
        (folder / str(self.number)).mkdir(parents=True, exist_ok=True)
        copy(self.fleet.tuning / "frame.json", folder / str(self.number))
        with open(folder / str(self.number) / "sitl.log", "w") as log:
            process = Popen(
                self.words(), cwd=folder / str(self.number), stdout=log, stderr=STDOUT
            )
            try:
                yield process
            finally:
                process.terminate()
                process.wait(timeout=5)
