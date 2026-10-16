from random import choice, randint
from uuid import uuid4

from fake_radio import FakeRadio
from flocking_ros.ground.orders import Orders
from hamcrest import assert_that, empty, has_length, only_contains
from pygame import KEYDOWN, KEYUP, KSCAN_H, KSCAN_L, KSCAN_T
from pygame.event import Event


def test_sends_the_word_of_a_pressed_key_to_every_drone():
    word = uuid4().hex
    key = choice((KSCAN_H, KSCAN_L, KSCAN_T))
    sent: list = []
    Orders(
        tuple(FakeRadio(sent) for _ in range(randint(2, 6))), {key: word}
    ).given([Event(KEYDOWN, scancode=key, key=0)])
    assert_that(
        [message.data for message in sent],
        only_contains(word),
        'a pressed key does not send its word',
    )


def test_reaches_every_drone_with_one_order():
    count = randint(2, 6)
    sent: list = []
    Orders(tuple(FakeRadio(sent) for _ in range(count)), {KSCAN_L: uuid4().hex}).given(
        [Event(KEYDOWN, scancode=KSCAN_L, key=0)]
    )
    assert_that(sent, has_length(count), 'an order does not reach every drone')


def test_cannot_send_anything_for_a_key_with_no_word():
    sent: list = []
    Orders((FakeRadio(sent),), {KSCAN_L: uuid4().hex}).given(
        [Event(KEYDOWN, scancode=KSCAN_T, key=0)]
    )
    assert_that(sent, empty(), 'a key with no word sends an order')


def test_cannot_send_anything_when_a_key_is_released():
    sent: list = []
    Orders((FakeRadio(sent),), {KSCAN_L: uuid4().hex}).given(
        [Event(KEYUP, scancode=KSCAN_L, key=0)]
    )
    assert_that(sent, empty(), 'a released key sends an order')
