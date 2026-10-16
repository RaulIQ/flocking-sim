from dataclasses import dataclass
from pathlib import Path
from typing import final
from xml.etree import ElementTree

from agent.vector import Vector
from autopilot.scene import Scene
from simulator.muster import Muster


@final
@dataclass(frozen=True)
class Arena(Scene):
    """The world of Gazebo with every copter of a swarm standing at its place in the muster.

    Gazebo takes its world from one file, while the copters differ by their
    places and by the port on which the plugin of each talks to its own
    autopilot, so every copter is a copy of one model laid into the world.
    Every autopilot counts its position from the shared origin, which is the
    origin of the world, so a copter stands at its place in the shared frame,
    east and north, at the height its model stands at.
    """

    world: Path
    model: Path
    muster: Muster
    port: int

    def text(self) -> str:
        tree = ElementTree.parse(self.world)
        tree.find("world").extend(
            self.copter(number, place) for number, place in enumerate(self.muster.places())
        )
        return ElementTree.tostring(tree.getroot(), encoding="unicode")

    def copter(self, number: int, place: Vector) -> ElementTree.Element:
        model = ElementTree.parse(self.model).find("model")
        model.set("name", f"uav{number + 1}")
        model.find("pose").text = " ".join(
            (str(place.x), str(place.y), *model.find("pose").text.split()[2:])
        )
        model.find("plugin[@name='ArduPilotPlugin']/fdm_port_in").text = str(self.port + 10 * number)
        return model
