#!/bin/bash
set -e
source /opt/ros/jazzy/setup.bash
export GZ_SIM_RESOURCE_PATH=/app/flocking/docker/gazebo/models:/app/flocking/docker/gazebo/worlds:$GZ_SIM_RESOURCE_PATH
ros2 run ros_gz_bridge parameter_bridge '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock' &
gz sim -v 3 -r ${HEADLESS:+-s} "${WORLD:-cloud.sdf}" &
wait -n
