from threading import Thread

from config import copters, sortie
from flocking_ros.flight.client_link import ClientLink
from flocking_ros.flight.dispatch import Dispatch
from flocking_ros.flight.latest import Latest
from flocking_ros.flight.mavros_vehicle import MavrosVehicle
from flocking_ros.flight.online import Online
from flocking_ros.flight.persistent import Persistent
from flocking_ros.flight.placed import Placed
from flocking_ros.flight.refusal import Refusal
from flocking_ros.flight.takeoff import Takeoff
from flocking_ros.flight.transition import Transition
from geometry_msgs.msg import PoseStamped
from mavros_msgs.msg import State, SysStatus
from mavros_msgs.srv import CommandBool, CommandTOL, MessageInterval, SetMode
from pymavlink.dialects.v20.common import MAVLINK_MSG_ID_EXTENDED_SYS_STATE
import rclpy
from rclpy.callback_groups import MutuallyExclusiveCallbackGroup
from rclpy.executors import MultiThreadedExecutor
from rclpy.qos import qos_profile_sensor_data
from std_msgs.msg import String


def main() -> None:
    rclpy.init()
    node = rclpy.create_node('flight')
    command = node.declare_parameter('command', '').value
    status = Latest(30.0)
    estimate = Latest(120.0)
    health = Latest(120.0)
    node.create_subscription(State, 'mavros/state', status.record, qos_profile_sensor_data)
    node.create_subscription(
        PoseStamped, 'mavros/local_position/pose', estimate.record, qos_profile_sensor_data
    )
    node.create_subscription(
        SysStatus, 'mavros/sys_status', health.record, qos_profile_sensor_data
    )
    vehicle = Online(
        Placed(
            MavrosVehicle(
                ClientLink(node.create_client(SetMode, 'mavros/set_mode'), 10.0),
                ClientLink(node.create_client(CommandBool, 'mavros/cmd/arming'), 10.0),
                ClientLink(node.create_client(CommandTOL, 'mavros/cmd/takeoff'), 10.0),
                status,
            ),
            estimate,
            health,
        ),
        status,
    )
    maneuvers = {
        'takeoff': Persistent(Takeoff(vehicle, sortie(copters()).hold.altitude), 120.0, 3.0),
        'land': Transition(vehicle, 'LAND'),
        'rtl': Transition(vehicle, 'RTL'),
    }
    executor = MultiThreadedExecutor()
    executor.add_node(node)
    if command:
        Thread(target=executor.spin, daemon=True).start()
        node.get_logger().info(f'The flight starts with {command}')
        maneuvers[command].fly()
        if not ClientLink(
            node.create_client(MessageInterval, 'mavros/set_message_interval'), 10.0
        ).ask(
            MessageInterval.Request(
                message_id=MAVLINK_MSG_ID_EXTENDED_SYS_STATE, message_rate=5.0
            )
        ).success:
            raise Refusal('Autopilot refused to tell whether the copter is in the air')
        node.get_logger().info(f'The copter flew {command}')
        rclpy.shutdown()
        return
    node.create_subscription(
        String,
        'flight_command',
        Dispatch(maneuvers, node.get_logger()).receive,
        10,
        callback_group=MutuallyExclusiveCallbackGroup(),
    )
    node.get_logger().info(f'The flight obeys {", ".join(maneuvers)}')
    executor.spin()
