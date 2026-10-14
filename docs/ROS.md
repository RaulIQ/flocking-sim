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
2. One copter. The drone image is built, one container starts SITL from the
   mounted binary and MAVROS beside it, and MAVROS reports the autopilot as
   connected under `/uav1`.
3. Takeoff from ROS. A small node in the container sets GUIDED, arms, takes
   off to the altitude and holds it, through the services of MAVROS.
4. The agent on board. The agent node wraps `Mind`: it builds `Senses` from
   the topics, ticks on its own timer at 20 Hz and sends the speed target in
   the frame of the copter. With no neighbours and a fixed request, the
   copter flies that request.
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
  in a fixed layout. To be decided at step 4.
- The frame of the speed target. MAVROS turns frames of ROS (east, north, up;
  forward, left, up) into those of ArduPilot. The agent counts forward and
  left, which may make the sign changes of `Target` unnecessary. To be
  checked on the copter at step 4, not assumed.
- The names of the topics and services of MAVROS, of its packages and of the
  script that installs its geographic data are written from memory and are
  to be checked at steps 2 and 3.
- How the window of `viewer` reaches the screen: through the X11 socket, or
  through Wayland, which this machine may use.
- Whether the safety milestone of `docs/SITL.md` is done first, so that the
  plain SITL stand can land too.
