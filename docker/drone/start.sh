#!/bin/bash
set -e
: "${DRONE_ID:?The drone container needs DRONE_ID, the number of its drone}"
: "${HOME_SPOT:?The drone container needs HOME_SPOT, the place it starts at as lat,lon,alt,yaw}"
: "${ALTITUDE:?The drone container needs ALTITUDE, the height in metres it hovers at}"
source /opt/ros/jazzy/setup.bash
mkdir -p /run/sitl
cd /run/sitl
cp /app/tuning/frame.json .
/app/bin/arducopter --wipe --model +:frame.json --speedup 1 --sysid "$DRONE_ID" --home "$HOME_SPOT" \
    --defaults /app/defaults.parm,/app/tuning/copter.parm,/app/streams.parm > /run/sitl/sitl.log 2>&1 &
ros2 launch mavros apm.launch fcu_url:=tcp://127.0.0.1:5760 tgt_system:="$DRONE_ID" namespace:="uav$DRONE_ID" &
python3 /app/nodes/liftoff.py "$ALTITUDE" 120 --ros-args -r __ns:="/uav$DRONE_ID"
wait -n
