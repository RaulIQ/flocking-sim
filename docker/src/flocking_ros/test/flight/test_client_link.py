import random
from threading import Event
from uuid import uuid4

from domain import Domain
from flocking_ros.flight.client_link import ClientLink
from flocking_ros.flight.refusal import Refusal
from hamcrest import assert_that, calling, equal_to, raises
from mavros_msgs.srv import CommandBool, CommandTOL
from rclpy.context import Context


def test_returns_response_of_service() -> None:
    name = f'/service_{uuid4().hex}'
    result = random.randint(1, 200)
    with Domain(random.randint(1, 100), Context()) as node:
        node.create_service(
            CommandTOL, name, lambda request, response: CommandTOL.Response(result=result)
        )
        answer = ClientLink(node.create_client(CommandTOL, name), 10.0).ask(CommandTOL.Request())
    assert_that(answer.result, equal_to(result), 'Link did not return the response of service')


def test_cannot_ask_absent_service() -> None:
    name = f'/service_{uuid4().hex}'
    with Domain(random.randint(1, 100), Context()) as node:
        assert_that(
            calling(ClientLink(node.create_client(CommandBool, name), 0.2).ask).with_args(
                CommandBool.Request()
            ),
            raises(Refusal, pattern=name),
            'Link did not refuse to ask the absent service'
        )


def test_cannot_wait_for_silent_service_forever() -> None:
    name = f'/service_{uuid4().hex}'
    with Domain(random.randint(1, 100), Context()) as node:
        node.create_service(
            CommandBool,
            name,
            lambda request, response: CommandBool.Response(success=Event().wait(3.0))
        )
        assert_that(
            calling(ClientLink(node.create_client(CommandBool, name), 0.5).ask).with_args(
                CommandBool.Request()
            ),
            raises(Refusal, pattern=name),
            'Link did not stop waiting for the silent service'
        )
