from random import uniform

from agent.tuning import Limits
from agent.vector import Vector
from flocking_ros.ground.hands import Hands
from hamcrest import assert_that, empty, same_instance
from scenarios.tally import Passage, Tally
from simulator.body import Body
from simulator.control import Pilot
from simulator.flock import Flock


def test_keeps_the_hands_of_the_pilot_whatever_the_leader_does():
    hands = Hands(Pilot(Limits(2.0, 4.0, 1.8, 8.0)))
    assert_that(
        hands.rest(
            Body(
                Vector(uniform(-9.0, 9.0), uniform(-9.0, 9.0)),
                uniform(0.0, 6.0),
                Vector(0.0, 0.0),
                0.0,
            )
        ),
        same_instance(hands),
        'the hands of the pilot change with the flight of the leader',
    )


def test_cannot_report_anything_from_the_hands_of_the_pilot():
    assert_that(
        Hands(Pilot(Limits(2.0, 4.0, 1.8, 8.0))).told(
            250, Tally(1.0, 1.0, 0, Passage(0, 0.0)), Flock(())
        ),
        empty(),
        'the hands of the pilot report something',
    )
