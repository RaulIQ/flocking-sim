#!/bin/bash
set -e
source /opt/ros/jazzy/setup.bash
export GZ_SIM_RESOURCE_PATH=/app/flocking/docker/gazebo/models:/app/flocking/docker/gazebo/worlds:$GZ_SIM_RESOURCE_PATH
exec gz sim -v 3 -r ${HEADLESS:+-s} "${WORLD:-cloud.sdf}"
