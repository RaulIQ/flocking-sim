from dataclasses import dataclass
from pathlib import Path
from typing import final


@final
@dataclass(frozen=True)
class Stub:
    """A folder that looks like a built ArduPilot, whose copter is a shell script."""

    root: Path
    script: str

    def built(self) -> Path:
        binary = self.root / "build" / "sitl" / "bin" / "arducopter"
        binary.parent.mkdir(parents=True)
        binary.write_text(f"#!/bin/sh\n{self.script}\n")
        binary.chmod(0o755)
        return self.root
