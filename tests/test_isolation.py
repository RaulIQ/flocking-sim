from ast import Import, ImportFrom, parse, walk
from pathlib import Path
from sys import stdlib_module_names


def test_cannot_import_anything_but_itself_the_config_and_the_standard_library():
    assert {
        name.split(".")[0]
        for path in [*Path(__file__).parent.parent.joinpath("agent").glob("*.py")]
        + [Path(__file__).parent.parent / "config.py"]
        for node in walk(parse(path.read_text()))
        if isinstance(node, (Import, ImportFrom))
        for name in (
            [node.module] if isinstance(node, ImportFrom) else [alias.name for alias in node.names]
        )
    } - set(stdlib_module_names) <= {
        "agent",
        "config",
    }, "the agent imports something beyond itself, the config and the standard library"
