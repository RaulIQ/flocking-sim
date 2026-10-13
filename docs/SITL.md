# Stage: the cloud on ArduPilot SITL

## Goal

Fly the same agent on real autopilots. The kinematic body in `simulator/body.py`
is replaced by ArduPilot SITL copters: the agent's command goes to an autopilot
over MAVLink, and the next state of the drone comes back from its telemetry.
The window, the keyboard, the virtual walls, the scenarios and the tally stay
as they are.

Done when the leader is flown from the keyboard and three SITL copters follow
it as a cloud in the same window, and the `hover`, `cruise` and `gap` scenarios
run on SITL and write their summaries next to the kinematic ones.

## Why

The agent was built to see only what a drone can measure. This stage checks
that the boundary holds: if `Mind` flies autopilots without a change, the
boundary is right. It also brings the first real imperfections: the autopilot
lags and limits the request, and the loop ticks in real time, not in exact
steps.

## Out of scope

- No ROS, no MAVROS, no Gazebo.
- No sensor noise, no delays beyond those SITL brings by itself.
- No third dimension: every drone holds one altitude.
- Walls stay virtual: SITL has no walls, the simulator computes what a drone
  would feel from the same geometry as now.
- No real hardware.

## Architecture

The motion of the drones becomes an interface with two implementations.

- The kinematic one is today's `Body.moved`. It stays the default, and every
  existing test and scenario keeps running on it unchanged.
- The autopilot one sends each drone's command to its SITL copter and builds
  the drone's next `Body` from the latest telemetry of that copter.

`Stage` picks one of them from the settings. Nothing in `agent/` changes, and
`agent/` keeps importing nothing from the simulator.

## Transport

One MAVLink connection per copter through pymavlink, all in one process.

Each SITL instance is started without MAVProxy and listens on its own TCP port.
For instance `I` the port is expected to be `5760 + 10 * I`; check it in the
SITL output before relying on it.

## Starting SITL

Start one instance per drone with its own number and system id, and with a
start location that matches `Muster.places()`, so that the copters stand where
the kinematic drones start. The built copter is run directly, without
`sim_vehicle.py`, so that nothing is rebuilt at the start and every instance
is a child process that can be stopped:

    build/sitl/bin/arducopter --wipe --model + --speedup 1 --base-port 5760 -I 0 --sysid 1 --home LAT,LON,0,90 --defaults Tools/autotest/default_params/copter.parm

The yaw of 90 degrees points the nose to the east, where the kinematic drones
look at the start.

`python -m autopilot` starts all of them from the settings and stops them on
Ctrl-C. Each instance keeps its files and its output in a folder of its own
under `autopilot/logs/`.

## Frames

The simulator uses a flat frame: `x` east, `y` north, angles counterclockwise
from `x`. The drone's own frame has `x` along the nose and `y` to the left.
ArduPilot uses north, east, down, with yaw clockwise from north, and its body
frame has `y` to the right.

- Position: latitude and longitude become metres around one reference point
  shared by all copters (a flat approximation is enough at these distances).
- Velocity: `x` is the east speed and `y` the north speed.
- Heading: the simulator heading is a quarter turn minus the autopilot yaw.
- Spin: the simulator spin is the autopilot yaw rate with the opposite sign.
- Command: the forward speed stays, the sideways speed and the yaw rate
  change sign.

Every conversion is covered by unit tests before any copter is connected.

## Telemetry

Each copter is asked for `GLOBAL_POSITION_INT` and `ATTITUDE` at 20 to 50 Hz
through `MAV_CMD_SET_MESSAGE_INTERVAL`. The latest message of each kind is
kept with the time it arrived.

## Flight

1. Wait for a heartbeat and a ready position estimate from every copter.
2. Switch every copter to GUIDED, arm it and take off to the set altitude.
3. Wait until every copter holds the altitude, then hand control to the agents.
4. Every tick send each copter `SET_POSITION_TARGET_LOCAL_NED` in its body
   frame with the horizontal speed and the yaw rate from its command, and a
   vertical speed from a simple altitude hold: the gap to the set altitude
   times a gain, capped.
5. Send the target every tick: ArduPilot stops a speed target that is not
   repeated within a few seconds.

## Loop

The loop ticks in real time at a fixed rate, 20 Hz to start. The time between
ticks is measured and logged. The tracker still assumes a fixed step; the
difference between the assumed and the measured step is part of what this
stage observes.

## Safety

- A key lands every copter at once.
- A copter whose telemetry is older than half a second gets a zero speed
  target until fresh telemetry arrives.
- Closing the window lands every copter.

## Scenarios

A scenario runs on SITL through the same `Trial` and the same `Tally`, with its
logs in `scenarios/logs/sitl/`. Runs on SITL are no longer exact, so each one
is run three times and the summaries are compared as a spread, not as one
number.

## Settings

A new block in `config.py` holds: the number of copters, the base port, the
reference point, the altitude, the loop rate, the altitude gain and its cap,
and the age after which telemetry counts as stale.

## Milestones

1. Frames: the conversions with their tests, no SITL needed.
2. Link: connect to every running copter and print positions in the shared
   frame.
3. Takeoff: every copter takes off, holds the altitude and obeys a fixed
   command.
4. Swap: the autopilot motion behind the interface, the window flies on SITL.
5. Scenarios: `hover`, `cruise` and `gap` on SITL, three runs each.
6. Safety: the landing key, the stale telemetry rule, landing on close.

## Expected surprises

- ArduPilot accelerates and turns slower than the kinematic body, so followers
  may lag or sway. The agent's `Limits` and the autopilot's own limits must be
  brought into line; the names of those parameters are to be checked in the
  documentation of the ArduPilot version in use.
- SITL copters do not collide: they fly through each other. A breached bubble
  shows only in the tally.

## Open questions

- How many copters the machine carries in real time: start with three.
- Which ArduPilot parameters to change, and whether to keep them in a file
  in the repository.