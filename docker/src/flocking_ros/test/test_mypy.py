from ament_mypy.main import main
import pytest


@pytest.mark.mypy
@pytest.mark.linter
def test_mypy() -> None:
    rc = main(argv=[])
    assert rc == 0, 'Found type errors!'
