from dataclasses import dataclass
from pathlib import Path
from typing import final


@final
@dataclass(frozen=True)
class Stub:
    """A folder that looks like a built ArduPilot, whose copter is a shell script, with a tuning beside it."""

    root: Path
    script: str

    def built(self) -> Path:
        binary = self.root / "build" / "sitl" / "bin" / "arducopter"
        binary.parent.mkdir(parents=True, exist_ok=True)
        binary.write_text(f"#!/bin/sh\n{self.script}\n")
        binary.chmod(0o755)
        return self.root

    def tuned(self) -> Path:
        (self.root / "tuning").mkdir(parents=True, exist_ok=True)
        (self.root / "tuning" / "frame.json").write_text('{"mass": 0.25}\n')
        (self.root / "tuning" / "copter.parm").write_text("WP_ACC 5\n")
        return self.root / "tuning"
