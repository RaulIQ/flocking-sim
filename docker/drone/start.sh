#!/bin/bash
set -e
: "${DRONE_ID:?The drone container needs DRONE_ID, the number of its drone}"
source /opt/ros/jazzy/setup.bash
source /ws/install/setup.bash
export PYTHONPATH=/app/flocking:$PYTHONPATH
HOME_SPOT=$(ros2 run flocking_ros home "$DRONE_ID")
mkdir -p /run/sitl
cd /run/sitl
cp /app/flocking/autopilot/freestyle/frame.json .
/app/bin/arducopter --wipe --model +:frame.json --speedup 1 --sysid "$DRONE_ID" --home "$HOME_SPOT" \
    --defaults /app/defaults.parm,/app/flocking/autopilot/freestyle/copter.parm,/app/streams.parm > /run/sitl/sitl.log 2>&1 &
ros2 launch mavros apm.launch fcu_url:=tcp://127.0.0.1:5760 tgt_system:="$DRONE_ID" namespace:="uav$DRONE_ID" &
ros2 run flocking_ros liftoff --ros-args -r __ns:="/uav$DRONE_ID"
ros2 run flocking_ros board --ros-args -r __ns:="/uav$DRONE_ID" &
wait -n
