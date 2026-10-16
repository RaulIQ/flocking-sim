from random import uniform
from xml.etree import ElementTree

from pytest import approx

from autopilot.arena import Arena
from autopilot.columns import Columns
from simulator.muster import Muster
from simulator.posts import Posts


def arena(folder):
    (folder / "world.sdf").write_text(
        '<sdf version="1.9"><world name="cloud"><include><uri>model://runway</uri></include></world></sdf>'
    )
    (folder / "model.sdf").write_text(
        '<sdf version="1.9"><model name="copter"><pose>0 0 0.2 0 0 0</pose>'
        '<plugin name="ArduPilotPlugin" filename="ArduPilotPlugin"><fdm_port_in>9002</fdm_port_in></plugin>'
        "</model></sdf>"
    )
    return Arena(folder / "world.sdf", folder / "model.sdf", Muster(4, 1.2), 9002)


def test_stands_a_column_for_every_pillar(tmp_path):
    assert (
        len(
            ElementTree.fromstring(Columns(arena(tmp_path), Posts(4.0, 1.8, 0.6), 6.0).text()).findall(
                "world/model/link/collision/geometry/cylinder"
            )
        )
        == 2
    ), "the world does not stand a column for every pillar"


def test_keeps_the_copters_of_the_arena(tmp_path):
    assert (
        len(
            [
                model
                for model in ElementTree.fromstring(
                    Columns(arena(tmp_path), Posts(4.0, 1.8, 0.6), 6.0).text()
                ).findall("world/model")
                if model.get("name").startswith("uav")
            ]
        )
        == 4
    ), "the columns push the copters out of the world"


def test_makes_a_column_as_wide_as_its_pillar(tmp_path):
    radius = uniform(0.3, 1.0)
    assert float(
        ElementTree.fromstring(Columns(arena(tmp_path), Posts(4.0, 1.8, radius), 6.0).text())
        .find("world/model/link/collision/geometry/cylinder/radius")
        .text
    ) == approx(radius), "a column is not as wide as its pillar"


def test_stands_a_column_where_its_pillar_stands(tmp_path):
    across = uniform(2.0, 6.0)
    assert [
        float(part)
        for part in ElementTree.fromstring(
            Columns(arena(tmp_path), Posts(across, 1.8, 0.6), 6.0).text()
        )
        .find("world/model[@name='pillar1']/pose")
        .text.split()[:2]
    ] == [approx(across), approx(-1.5)], "a column does not stand where its pillar stands"


def test_stands_a_column_on_the_ground(tmp_path):
    height = uniform(4.0, 8.0)
    assert float(
        ElementTree.fromstring(Columns(arena(tmp_path), Posts(4.0, 1.8, 0.6), height).text())
        .find("world/model[@name='pillar2']/pose")
        .text.split()[2]
    ) == approx(height / 2), "a column does not stand on the ground"


def test_keeps_a_column_still(tmp_path):
    assert (
        ElementTree.fromstring(Columns(arena(tmp_path), Posts(4.0, 1.8, 0.6), 6.0).text())
        .find("world/model[@name='pillar1']/static")
        .text
        == "true"
    ), "a column moves when a copter hits it"
