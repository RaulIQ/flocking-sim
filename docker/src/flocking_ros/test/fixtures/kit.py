from dataclasses import dataclass
from typing import final

from agent.instinct import Instinct
from agent.mind import Mind
from agent.shield import Shield
from agent.tracker import Tracker
from agent.tuning import Cloud, Limits, Rope, Spring
from autopilot.hold import Hold
from flocking_ros.board.board import Board


@final
@dataclass(frozen=True)
class Kit:
    """
    A board with the tuning of the cloud spelled out.

    It serves tests that care only about what the board does with its senses
    and its altitude, not about how the mind is tuned.
    """

    hold: Hold

    def board(self) -> Board:
        return Board(
            Mind(
                Instinct(
                    Cloud(
                        Spring(1.2, 0.5, 0.15, 1.0),
                        Rope(Spring(1.2, 1.0, 0.4, 1.5), 1.5, 2.0),
                        Spring(0.6, 1.0, 0.0, 0.0),
                        6,
                    ),
                    Limits(2.0, 4.0, 1.8, 8.0),
                ),
                Shield(Limits(2.0, 4.0, 1.8, 8.0), 0.25, 0.05, 0.5),
                Tracker(0.05),
                False,
            ),
            self.hold,
        )
