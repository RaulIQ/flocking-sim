#!/bin/bash
set -e
source /opt/ros/jazzy/setup.bash
source /ws/install/setup.bash
export PYTHONPATH=/app/flocking:$PYTHONPATH
exec ros2 run flocking_ros ground
