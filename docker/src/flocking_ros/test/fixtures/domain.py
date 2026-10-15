from dataclasses import dataclass
from threading import Thread
from types import TracebackType
from typing import final
from uuid import uuid4

import rclpy
from rclpy.context import Context
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node


@final
@dataclass(frozen=True)
class Domain:
    """Private ROS domain that spins one node until the block ends."""

    number: int
    context: Context

    def __enter__(self) -> Node:
        rclpy.init(context=self.context, domain_id=self.number)
        node = rclpy.create_node(f'node_{uuid4().hex}', context=self.context)
        executor = MultiThreadedExecutor(context=self.context)
        executor.add_node(node)
        Thread(target=executor.spin, daemon=True).start()
        return node

    def __exit__(
        self,
        kind: type[BaseException] | None,
        error: BaseException | None,
        trace: TracebackType | None
    ) -> None:
        rclpy.shutdown(context=self.context)
