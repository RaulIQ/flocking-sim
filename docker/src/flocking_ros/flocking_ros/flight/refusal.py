from typing import final


@final
class Refusal(Exception):
    """Failure of the autopilot to carry out a flight step."""
