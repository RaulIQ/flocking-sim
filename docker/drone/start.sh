#!/bin/bash
set -e
: "${DRONE_ID:?The drone container needs DRONE_ID, the number of its drone}"
source /opt/ros/jazzy/setup.bash
source /ws/install/setup.bash
export PYTHONPATH=/app/flocking:$PYTHONPATH
HOME_SPOT=$(ros2 run flocking_ros home "$DRONE_ID")
mkdir -p /run/sitl
cd /run/sitl
if [ -n "$GAZEBO" ]; then
    ADDRESS=$(getent hosts "$GAZEBO" | awk '{print $1}')
    : "${ADDRESS:?The drone container cannot find the Gazebo host named in GAZEBO}"
    MODEL="JSON:$ADDRESS"
    TUNING=/app/flocking/autopilot/gazebo_iris
else
    MODEL=+:frame.json
    TUNING=/app/flocking/autopilot/freestyle
    cp "$TUNING/frame.json" .
fi
/app/bin/arducopter --wipe --model "$MODEL" --speedup 1 --sysid "$DRONE_ID" --home "$HOME_SPOT" \
    --defaults "/app/defaults.parm,$TUNING/copter.parm,/app/streams.parm" > /run/sitl/sitl.log 2>&1 &
ros2 launch mavros apm.launch fcu_url:=tcp://127.0.0.1:5760 tgt_system:="$DRONE_ID" namespace:="uav$DRONE_ID" &
ros2 run flocking_ros liftoff --ros-args -r __ns:="/uav$DRONE_ID"
ros2 run flocking_ros board --ros-args -r __ns:="/uav$DRONE_ID" ${GAZEBO:+-p use_sim_time:=true} &
wait -n
