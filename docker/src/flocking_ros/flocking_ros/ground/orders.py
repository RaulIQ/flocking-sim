from dataclasses import dataclass
from typing import final

from pygame import KEYDOWN
from std_msgs.msg import String


@final
@dataclass(frozen=True)
class Orders:
    """
    The keys that tell every copter at once to change its flight, such as to land.

    Keys arrive by scancode, one slot per physical place on the keyboard, so
    that a Cyrillic layout gives the same orders. A pressed key sends its word
    to every copter; a key with no word, or a released one, sends nothing.
    """

    radios: tuple
    words: dict

    def given(self, events: list) -> None:
        for event in events:
            if event.type == KEYDOWN and event.scancode in self.words:
                for radio in self.radios:
                    radio.publish(String(data=self.words[event.scancode]))
