# Stage: the cloud in containers on ROS 2

Issue: #2.

## Goal

Fly the same agent the way a real swarm would carry it: every drone in a
container of its own, with its autopilot, MAVROS and its agent inside, and
the drones and the ground talking over ROS 2 across a network.

Done when four drone containers and one ground container start with one
command, the leader is flown from the keyboard and three copters follow it as
a cloud, the same as `python -m autopilot` does today.

## Why

Today one program thinks for all four drones in one tick. On a real swarm
every drone thinks on its own board, at its own pace, and hears its
neighbours over a link that is late and loses messages. This stage checks
that `Mind` holds up when nothing is shared but what is sent over the
network, and it builds the stand on which delays and losses can be added on
purpose.

## Out of scope

- No Gazebo: SITL keeps its own physics, the walls stay virtual.
- No real hardware.
- No third dimension: every drone holds one altitude.
- No new behaviour of the agent: `agent/` is mounted as it is.

## Architecture

```
┌─ container uav1 ──────────┐  ┌─ uav2 ─┐  ┌─ uav3 ─┐  ┌─ uav4 ─┐
│ ArduPilot SITL            │  │  same  │  │  same  │  │  same  │
│   ▲ MAVLink, inside       │  │        │  │        │  │        │
│   ▼                       │  │        │  │        │  │        │
│ MAVROS          (/uav1)   │  │ /uav2  │  │ /uav3  │  │ /uav4  │
│   ▲ ROS 2 topics          │  │        │  │        │  │        │
│   ▼                       │  │        │  │        │  │        │
│ agent node: Mind          │  │        │  │        │  │        │
└──────────▲────────────────┘  └───▲────┘  └───▲────┘  └───▲────┘
           │                       │           │           │
═══════════╧════ Docker network, ROS 2 over DDS, one ROS_DOMAIN_ID ═══════
           │
┌─ ground container ────────────────────────────────────────────┐
│ world  — reads where every drone is, sends each drone what    │
│          its own sensors would measure: ranges, bearings,     │
│          roles, the nearest points of the walls               │
│ pilot  — keyboard → the request of the leader                 │
│ viewer — the window with the cloud                            │
└───────────────────────────────────────────────────────────────┘
```

- SITL stands in for the flight controller; MAVROS and the agent node stand
  for the companion computer, and only they would move onto a real drone.
- The agent of drone N hears only its own MAVROS, its own senses from
  `world`, and, for the leader, the pilot. Agents never talk to each other.
- `world` replaces the sensors SITL does not have. On real drones it goes
  away and the camera and the radio of each drone take its place.

## What comes from where

Everything that changes often is mounted from the machine read-only, so a
change needs a restart of the containers, not a new image.

| Mounted from the machine | Into every drone container |
|---|---|
| `~/code/ardupilot/build/sitl/bin/arducopter` | the firmware |
| `~/code/ardupilot/Tools/autotest/default_params/copter.parm` | ArduPilot's defaults |
| `autopilot/freestyle/` | the frame and its parameters |
| `agent/` | the agent |

The drone image holds ROS 2 Jazzy, MAVROS, the agent node and the start
script, and is built once. The four drone containers run the same image and
differ only by `DRONE_ID`, from which the start script takes the instance,
the system id, the namespace `/uavN` and the place in the muster.

The SITL binary built on this machine needs glibc 2.38 and GLIBCXX 3.4.21 at
most; `ros:jazzy` carries glibc 2.39 and GLIBCXX 3.4.33. Mounted into that
image, the binary starts, loads the freestyle frame from its folder and waits
on port 5760. Check it again after ArduPilot is rebuilt on a newer system.

## Layout

```
docker/
  compose.yml          four drones and the ground
  drone/
    Dockerfile         ROS 2, MAVROS, the agent node
    start.sh           SITL, MAVROS and the agent by DRONE_ID
    agent_node.py      Mind behind ROS 2 topics
  ground/
    Dockerfile         ROS 2, pygame
    start.sh
    world_node.py      the virtual sensors
    pilot_node.py      the keyboard
    viewer_node.py     the window
```

## Steps

Each step ends with something that runs and is checked by hand or by a test.

1. Access. The user can run Docker without `sudo`, `ros:jazzy` is pulled,
   and `ros2 topic list` answers inside a container. Done: Docker 29.8, the
   image takes 888 MB, and a shell started before the user joined the
   `docker` group reaches Docker through `sg docker -c "..."`.
   Docker must be installed once only: a second Docker from snap took the
   socket, and AppArmor kept it from stopping its own containers.
2. One copter. The drone image is built, one container starts SITL from the
   mounted binary and MAVROS beside it, and MAVROS reports the autopilot as
   connected under `/uav1`. Done: `docker compose up` in `docker/` starts
   `uav1`; from another container on the same network `/uav1/mavros/state`
   reads `connected: true` and `/uav1/mavros/local_position/pose` comes at
   20 Hz, while a container in another `ROS_DOMAIN_ID` sees none of it.
   SITL sends nothing until asked, so `docker/drone/streams.parm` sets the
   stream rates of its first MAVLink channel; ArduPilot 4.8 names them
   `MAV1_POSITION`, `MAV1_EXTRA1` and so on, older versions `SR0_...`.
3. Takeoff from ROS. A small node in the container sets GUIDED, arms, takes
   off to the altitude and holds it, through the services of MAVROS. Done:
   `docker/drone/nodes/liftoff.py` waits for MAVROS to connect and for a
   position, then asks for GUIDED, arming and takeoff, each again every two
   seconds until the state says it is done, each within two minutes. The
   copter armed at the first ask, reached 2.85 m about four seconds later and
   held 2.98 m within a centimetre. The start script and the nodes are
   mounted, so a change to them needs a restart, not a new image.
4. The agent on board. The agent node wraps `Mind`: it builds `Senses` from
   the topics, ticks on its own timer at 20 Hz and sends the speed target in
   the frame of the copter. With no neighbours and a fixed request, the
   copter flies that request. Done: `docker/drone/nodes/board.py` builds `Senses`
   from `velocity_body`, hands them to `Mind` with the request from
   `REQUEST`, holds the altitude with `Hold` and sends the target to
   `setpoint_raw/local` in the frame of the copter, twenty times a second.
   Asked for 0.5 m/s forward and 0.3 m/s to the left with the nose to the
   east, the copter flew 0.47 forward and 0.28 to the left, which is 0.47 to
   the east and 0.28 to the north, at 3.00 m; asked to turn at 0.3 rad/s, it
   turned at 0.30 counterclockwise. `docker/test.sh` runs the tests of the
   nodes inside the drone image, since this machine has no ROS.
5. Four copters. Compose starts four drone containers in `/uav1` to `/uav4`,
   each at its place in the muster, all of them airborne.
6. The ground. The ground container runs `world`, `pilot` and `viewer`; the
   window shows the four copters, `world` sends every drone its senses.
7. The cloud. The leader is flown from the keyboard and three copters follow
   it; the result is compared with `python -m autopilot` on the same route.
8. A bad link. Delays and losses are put on the network of every container
   with `tc netem`, and the cloud is watched as they grow.
9. Safety. A key lands every copter, a drone whose senses are older than half
   a second asks for zero speed, and stopping the stand lands every copter.

## Open questions

- How senses travel. `Senses` has no ready ROS 2 message: either a package of
  own messages, which needs a build step in the images, or standard messages
  in a fixed layout. A lone copter needs none, so it is decided at step 6,
  where `world` first sends them.
- The frame of the speed target is settled: MAVROS takes forward, left and
  up with turns counterclockwise, the frame of the agent, and turns it into
  that of ArduPilot itself. `Target` and its sign changes are not needed on
  this side.
- The topics of MAVROS live under `/uavN/mavros/`. Its position comes with
  the QoS of sensor data, best effort, and a subscriber must ask for the
  same or hear nothing.
- How the window of `viewer` reaches the screen: through the X11 socket, or
  through Wayland, which this machine may use.
- Whether the safety milestone of `docs/SITL.md` is done first, so that the
  plain SITL stand can land too.
