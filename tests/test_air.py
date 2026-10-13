from random import uniform
from time import monotonic

from pymavlink import mavutil
from pytest import approx

from agent.command import Command
from agent.vector import Vector
from autopilot.air import Air
from autopilot.hold import Hold
from autopilot.pulse import Pulse
from autopilot.spot import Spot
from autopilot.squad import Squad
from simulator.body import Body
from tests.decoy import Decoy


def test_tells_where_the_copter_is_and_not_where_the_drone_was():
    origin = Spot(uniform(-60.0, 60.0), uniform(-170.0, 170.0))
    decoy = Decoy(mavutil.mavlink_connection("tcpin:127.0.0.1:0", source_system=1))
    link = decoy.link(1)
    decoy.fix(
        round(origin.shifted(Vector(7.5, -3.25)).latitude * 1e7),
        round(origin.shifted(Vector(7.5, -3.25)).longitude * 1e7),
        0,
        0,
    )
    decoy.attitude(uniform(-3.0, 3.0), uniform(-2.0, 2.0))
    assert Air(Squad((link,), origin), Hold(0.0, 1.0, 1.0), Pulse(50.0)).moved(
        (Body(Vector(99.0, 99.0), 0.0, Vector(0.0, 0.0), 0.0),),
        (Command(Vector(1.0, 0.0), 0.0),),
    )[0].position == Vector(
        approx(7.5, abs=0.02), approx(-3.25, abs=0.02)
    ), "the air does not tell where the copter is"


def test_sends_every_command_up_to_its_copter():
    decoy = Decoy(mavutil.mavlink_connection("tcpin:127.0.0.1:0", source_system=1))
    link = decoy.link(1)
    decoy.fix(1, 2, 0, 0)
    decoy.attitude(uniform(-3.0, 3.0), uniform(-2.0, 2.0))
    Air(
        Squad((link,), Spot(uniform(-60.0, 60.0), uniform(-170.0, 170.0))),
        Hold(0.0, 1.0, 1.0),
        Pulse(50.0),
    ).moved((), (Command(Vector(1.75, 0.0), 0.0),))
    assert decoy.steered().vx == approx(1.75), "a command does not reach its copter"


def test_lets_one_beat_pass_before_it_reads_the_copters():
    decoy = Decoy(mavutil.mavlink_connection("tcpin:127.0.0.1:0", source_system=1))
    link = decoy.link(1)
    decoy.fix(1, 2, 0, 0)
    decoy.attitude(uniform(-3.0, 3.0), uniform(-2.0, 2.0))
    Air(
        Squad((link,), Spot(uniform(-60.0, 60.0), uniform(-170.0, 170.0))),
        Hold(0.0, 1.0, 1.0),
        Pulse(10.0),
    ).moved((), (Command(Vector(0.0, 0.0), 0.0),))
    assert monotonic() % 0.1 < 0.03, "the air answers off the beat"
