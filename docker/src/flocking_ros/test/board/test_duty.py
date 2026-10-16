import random

from autopilot.hold import Hold
from domain import Domain
from fake_radio import FakeRadio
from flocking_msgs.msg import Senses
from flocking_ros.board.duty import Duty
from geometry_msgs.msg import Twist
from hamcrest import assert_that, empty, has_length
from kit import Kit
from mavros_msgs.msg import ExtendedState
from rclpy.context import Context


def test_asks_for_nothing_while_the_copter_is_not_in_the_air():
    sent: list = []
    with Domain(random.randint(1, 100), Context()) as node:
        Duty(
            node,
            Kit(Hold(3.0, 1.0, 1.0)).board(),
            20.0,
            {
                'twist': Twist(),
                'height': random.uniform(0.0, 3.0),
                'letter': Senses(),
                'flight': ExtendedState(
                    landed_state=random.choice(
                        (
                            ExtendedState.LANDED_STATE_ON_GROUND,
                            ExtendedState.LANDED_STATE_TAKEOFF,
                            ExtendedState.LANDED_STATE_LANDING,
                        )
                    )
                ),
                'out': FakeRadio(sent),
            },
        ).tick()
    assert_that(sent, empty(), 'a board asks for a speed while its copter is not in the air')


def test_asks_for_a_speed_once_the_copter_is_in_the_air():
    sent: list = []
    with Domain(random.randint(1, 100), Context()) as node:
        Duty(
            node,
            Kit(Hold(3.0, 1.0, 1.0)).board(),
            20.0,
            {
                'twist': Twist(),
                'height': random.uniform(2.0, 4.0),
                'letter': Senses(),
                'flight': ExtendedState(landed_state=ExtendedState.LANDED_STATE_IN_AIR),
                'out': FakeRadio(sent),
            },
        ).tick()
    assert_that(sent, has_length(1), 'a board asks for no speed while its copter is in the air')
