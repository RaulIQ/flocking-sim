from itertools import pairwise

from scenarios.catalogue import catalogue
from scenarios.trial import Trial


def test_brings_the_whole_cloud_through_the_gap(tmp_path):
    assert (
        Trial("gap", catalogue()["gap"], 6).run(tmp_path).tally.passage.count == 8
    ), "the gap scenario leaves a drone behind the wall"


def test_brings_ten_drones_through_the_gap(tmp_path):
    assert (
        Trial("gap_ten", catalogue()["gap_ten"], 6).run(tmp_path).tally.passage.count == 10
    ), "the gap scenario for ten drones leaves a drone behind the wall"


def test_stops_the_leader_a_hard_bubble_short_of_the_wall(tmp_path):
    assert (
        Trial("wall", catalogue()["wall"], 6).run(tmp_path).tally.breaches == 0
    ), "the wall scenario lets a wall into a hard bubble"


def test_cannot_send_the_leader_through_the_solid_wall(tmp_path):
    assert (
        Trial("wall", catalogue()["wall"], 6).run(tmp_path).tally.passage.count == 0
    ), "the wall scenario lets a drone through the solid wall"


def test_settles_the_cloud_around_a_hovering_leader(tmp_path):
    assert (
        Trial("hover", catalogue()["hover"], 6).run(tmp_path).lines()[10]
        == "fastest follower at the end, m/s: 0.000"
    ), "the hover scenario leaves the cloud trembling"


def test_tells_a_story_for_every_scenario():
    assert all(
        scenario.story for scenario in catalogue().values()
    ), "a scenario comes without a story"


def test_brings_the_whole_cloud_through_two_gaps(tmp_path):
    assert (
        Trial("two_gaps", catalogue()["two_gaps"], 6).run(tmp_path).tally.passage.count
        == 10
    ), "the scenario with two gaps leaves a drone behind the wall"


def test_splits_the_cloud_between_the_two_gaps():
    assert {
        after.drones[index].body.position.y > 0.0
        for (_, before), (_, after) in pairwise(
            Trial("two_gaps", catalogue()["two_gaps"], 6).frames()
        )
        for index in range(len(after.drones))
        if before.drones[index].body.position.x
        < 4.0
        <= after.drones[index].body.position.x
    } == {True, False}, "the cloud does not use both gaps"
