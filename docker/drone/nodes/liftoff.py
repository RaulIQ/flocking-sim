import sys
from time import monotonic

import rclpy
from geometry_msgs.msg import PoseStamped
from mavros_msgs.msg import State
from mavros_msgs.srv import CommandBool, CommandTOL, SetMode
from rclpy.qos import qos_profile_sensor_data


class Liftoff:
    """Takes one copter from the ground to its altitude through MAVROS and leaves it hovering there.

    The copter is asked again and again, a few seconds apart, until it does
    what it is asked: an autopilot refuses to arm until its position estimate
    is ready, and a request lost on the way is simply sent again. Every wait
    is bounded and fails loudly.
    """

    def __init__(self, node, altitude: float, patience: float):
        self.node = node
        self.altitude = altitude
        self.patience = patience
        self.heard = {}

    def listen(self) -> None:
        self.node.create_subscription(
            State, "mavros/state", lambda state: self.heard.update(state=state), qos_profile_sensor_data
        )
        self.node.create_subscription(
            PoseStamped,
            "mavros/local_position/pose",
            lambda pose: self.heard.update(pose=pose),
            qos_profile_sensor_data,
        )

    def until(self, check, story: str, act) -> None:
        end = monotonic() + self.patience
        due = monotonic()
        while not check():
            if monotonic() > end:
                raise TimeoutError(f"{story} after {self.patience} seconds")
            if monotonic() >= due:
                act()
                due = monotonic() + 2.0
            rclpy.spin_once(self.node, timeout_sec=0.1)

    def ask(self, kind, name: str, request) -> None:
        client = self.node.create_client(kind, name)
        if not client.wait_for_service(timeout_sec=self.patience):
            raise TimeoutError(f"The service {name} did not appear in {self.patience} seconds")
        client.call_async(request)

    def run(self) -> None:
        self.listen()
        self.until(
            lambda: "state" in self.heard and self.heard["state"].connected,
            "MAVROS is not connected to the autopilot",
            lambda: None,
        )
        self.until(
            lambda: "pose" in self.heard,
            "The copter has no position estimate",
            lambda: None,
        )
        self.node.get_logger().info("The copter knows where it is")
        self.until(
            lambda: self.heard["state"].mode == "GUIDED",
            "The copter does not switch to GUIDED",
            lambda: self.ask(SetMode, "mavros/set_mode", SetMode.Request(custom_mode="GUIDED")),
        )
        self.node.get_logger().info("The copter is in GUIDED")
        self.until(
            lambda: self.heard["state"].armed,
            "The copter does not arm",
            lambda: self.ask(CommandBool, "mavros/cmd/arming", CommandBool.Request(value=True)),
        )
        self.node.get_logger().info("The copter is armed")
        self.until(
            lambda: self.heard["pose"].pose.position.z >= 0.95 * self.altitude,
            f"The copter does not reach {self.altitude} metres",
            lambda: self.ask(CommandTOL, "mavros/cmd/takeoff", CommandTOL.Request(altitude=self.altitude)),
        )
        self.node.get_logger().info(
            f"The copter hovers at {self.heard['pose'].pose.position.z:.2f} metres"
        )


if __name__ == "__main__":
    rclpy.init(args=sys.argv)
    Liftoff(rclpy.create_node("liftoff"), float(sys.argv[1]), float(sys.argv[2])).run()
    rclpy.shutdown()
