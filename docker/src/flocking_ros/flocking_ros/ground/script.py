from dataclasses import dataclass
from typing import final

from agent.command import Command
from flocking_ros.ground.helm import Helm
from scenarios.report import Report
from scenarios.route import Route
from scenarios.scenario import Scenario
from scenarios.tally import Tally
from simulator.body import Body
from simulator.flock import Flock


@final
@dataclass(frozen=True)
class Script(Helm):
    """
    A scripted pilot that flies the leader along the route of a scenario.

    The run is reported once the scenario ends. The frames are counted from
    the moment the whole cloud is airborne, so the report comes exactly once,
    at the frame the scenario ends.
    """

    name: str
    scenario: Scenario
    route: Route

    def rest(self, body: Body) -> 'Script':
        return Script(self.name, self.scenario, self.route.rest(body))

    def command(self, body: Body) -> Command:
        return self.route.command(body)

    def told(self, frame: int, tally: Tally, flock: Flock) -> tuple:
        if frame != round(self.scenario.seconds * self.scenario.settings.picture.window.rate):
            return ()
        return Report(self.name, self.scenario, tally, flock).lines()[:-1]
