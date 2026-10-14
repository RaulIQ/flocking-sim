#!/bin/bash
set -e
source /opt/ros/jazzy/setup.bash
source /ws/install/setup.bash
export PYTHONPATH=/app/flocking:/app/flocking/docker/ground/nodes:$PYTHONPATH
exec python3 /app/flocking/docker/ground/nodes/ground.py --ros-args -r __node:=ground
