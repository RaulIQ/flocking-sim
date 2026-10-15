#!/bin/bash
set -e
source /opt/ros/jazzy/setup.bash
export GZ_SIM_RESOURCE_PATH=/app/flocking/docker/gazebo/models:/app/flocking/docker/gazebo/worlds:$GZ_SIM_RESOURCE_PATH
export PYTHONPATH=/app/flocking:$PYTHONPATH
python3 /app/flocking/docker/gazebo/world.py \
    "/app/flocking/docker/gazebo/worlds/${WORLD:-cloud.sdf}" \
    /app/flocking/docker/gazebo/models/cloud_iris/model.sdf > /tmp/cloud.sdf
ros2 run ros_gz_bridge parameter_bridge '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock' &
gz sim -v 3 -r ${HEADLESS:+-s} /tmp/cloud.sdf &
wait -n
