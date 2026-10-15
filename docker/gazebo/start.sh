#!/bin/bash
set -e
source /opt/ros/jazzy/setup.bash
exec gz sim -v 3 -r ${HEADLESS:+-s} "${WORLD:-empty.sdf}"
