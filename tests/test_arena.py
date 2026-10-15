from random import randint, uniform
from xml.etree import ElementTree

from pytest import approx

from autopilot.arena import Arena
from simulator.muster import Muster


def world(folder):
    (folder / "world.sdf").write_text(
        '<sdf version="1.9"><world name="cloud"><include><uri>model://runway</uri></include></world></sdf>'
    )
    return folder / "world.sdf"


def model(folder, height):
    (folder / "model.sdf").write_text(
        '<sdf version="1.9"><model name="copter">'
        f"<pose>0 0 {height} 0 0 0</pose>"
        '<plugin name="ArduPilotPlugin" filename="ArduPilotPlugin"><fdm_port_in>9002</fdm_port_in></plugin>'
        "</model></sdf>"
    )
    return folder / "model.sdf"


def test_holds_a_copter_for_every_place_of_the_muster(tmp_path):
    count = randint(2, 6)
    assert (
        len(
            ElementTree.fromstring(
                Arena(world(tmp_path), model(tmp_path, 0.2), Muster(count, 1.3), 9002).text()
            ).findall("world/model")
        )
        == count
    ), "the arena does not hold a copter for every place of the muster"


def test_keeps_what_the_world_already_holds(tmp_path):
    assert (
        ElementTree.fromstring(
            Arena(world(tmp_path), model(tmp_path, 0.2), Muster(randint(1, 5), 1.3), 9002).text()
        ).find("world/include/uri").text
        == "model://runway"
    ), "the arena loses what the world already holds"


def test_names_the_copters_as_their_namespaces(tmp_path):
    count = randint(2, 6)
    assert [
        copter.get("name")
        for copter in ElementTree.fromstring(
            Arena(world(tmp_path), model(tmp_path, 0.2), Muster(count, 1.3), 9002).text()
        ).findall("world/model")
    ] == [f"uav{number}" for number in range(1, count + 1)], "the copters are not named as their namespaces"


def test_stands_the_second_copter_one_spacing_away(tmp_path):
    spacing = uniform(1.0, 3.0)
    assert sum(
        float(part) ** 2
        for part in ElementTree.fromstring(
            Arena(world(tmp_path), model(tmp_path, 0.2), Muster(3, spacing), 9002).text()
        )
        .findall("world/model")[1]
        .find("pose")
        .text.split()[:2]
    ) ** 0.5 == approx(spacing), "the second copter does not stand one spacing away"


def test_keeps_the_height_of_the_model(tmp_path):
    height = uniform(0.05, 0.5)
    assert float(
        ElementTree.fromstring(
            Arena(world(tmp_path), model(tmp_path, height), Muster(3, 1.3), 9002).text()
        )
        .findall("world/model")[2]
        .find("pose")
        .text.split()[2]
    ) == approx(height), "the copter does not keep the height of its model"


def test_cannot_give_two_copters_the_same_port(tmp_path):
    count = randint(2, 6)
    assert (
        len(
            {
                copter.find("plugin[@name='ArduPilotPlugin']/fdm_port_in").text
                for copter in ElementTree.fromstring(
                    Arena(world(tmp_path), model(tmp_path, 0.2), Muster(count, 1.3), randint(9000, 9100)).text()
                ).findall("world/model")
            }
        )
        == count
    ), "two copters talk to their autopilots on the same port"


def test_gives_the_third_copter_the_port_of_the_third_autopilot(tmp_path):
    port = randint(9000, 9100)
    assert ElementTree.fromstring(
        Arena(world(tmp_path), model(tmp_path, 0.2), Muster(4, 1.3), port).text()
    ).findall("world/model")[2].find("plugin[@name='ArduPilotPlugin']/fdm_port_in").text == str(
        port + 20
    ), "the third copter does not talk on the port of the third autopilot"
