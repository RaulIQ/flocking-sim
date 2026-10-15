from threading import Thread

from config import copters, sortie
from flocking_ros.flight.client_link import ClientLink
from flocking_ros.flight.latest import Latest
from flocking_ros.flight.mavros_vehicle import MavrosVehicle
from flocking_ros.flight.online import Online
from flocking_ros.flight.persistent import Persistent
from flocking_ros.flight.placed import Placed
from flocking_ros.flight.takeoff import Takeoff
from geometry_msgs.msg import PoseStamped
from mavros_msgs.msg import State, SysStatus
from mavros_msgs.srv import CommandBool, CommandTOL, SetMode
import rclpy
from rclpy.executors import MultiThreadedExecutor
from rclpy.qos import qos_profile_sensor_data


def main() -> None:
    rclpy.init()
    node = rclpy.create_node('liftoff')
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
    executor = MultiThreadedExecutor()
    executor.add_node(node)
    Thread(target=executor.spin, daemon=True).start()
    node.get_logger().info('The liftoff starts')
    Persistent(
        Takeoff(
            Online(
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
            ),
            sortie(copters()).hold.altitude,
        ),
        120.0,
        3.0,
    ).fly()
    node.get_logger().info(f'The copter hovers at {sortie(copters()).hold.altitude} meters')
    rclpy.shutdown()
