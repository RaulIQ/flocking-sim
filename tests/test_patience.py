from pytest import raises

from autopilot.patience import Patience


def test_asks_again_until_the_answer_is_yes():
    answers = iter((False, False, True, False))
    Patience(5.0, 0.01).until(lambda: next(answers), "The answer never came")
    assert next(answers) is False, "the asking does not stop at the first yes"


def test_cannot_ask_longer_than_its_seconds():
    with raises(TimeoutError, match="The answer never came after 0.1 seconds"):
        Patience(0.1, 0.01).until(lambda: False, "The answer never came")
