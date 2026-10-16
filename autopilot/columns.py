from dataclasses import dataclass
from typing import final
from xml.etree import ElementTree

from autopilot.scene import Scene
from simulator.posts import Posts


@final
@dataclass(frozen=True)
class Columns(Scene):
    """A world of Gazebo with a still, solid column standing on the ground at every pillar of the posts.

    The columns stand where the drones feel the pillars, in the shared frame,
    east and north, and reach above the flight, so a copter that misses the
    gap hits one.
    """

    scene: Scene
    posts: Posts
    height: float

    def text(self) -> str:
        root = ElementTree.fromstring(self.scene.text())
        root.find("world").extend(
            ElementTree.fromstring(
                f'<model name="pillar{number}"><static>true</static>'
                f"<pose>{pillar.centre.x} {pillar.centre.y} {self.height / 2} 0 0 0</pose>"
                '<link name="link">'
                f'<collision name="collision"><geometry><cylinder><radius>{pillar.radius}</radius>'
                f"<length>{self.height}</length></cylinder></geometry></collision>"
                f'<visual name="visual"><geometry><cylinder><radius>{pillar.radius}</radius>'
                f"<length>{self.height}</length></cylinder></geometry>"
                "<material><ambient>0.69 0.71 0.77 1</ambient><diffuse>0.69 0.71 0.77 1</diffuse></material>"
                "</visual></link></model>"
            )
            for number, pillar in enumerate(self.posts.walls(), start=1)
        )
        return ElementTree.tostring(root, encoding="unicode")
