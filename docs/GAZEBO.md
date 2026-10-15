# Stage: the cloud in Gazebo

## Goal

Fly the same cloud with the physics of Gazebo instead of the physics built
into SITL. Every drone keeps its container with ArduPilot, MAVROS and its
board; the copters themselves live in one shared Gazebo world, in a container
of its own, where they can touch each other and the walls.

Done when four copters take off in one Gazebo world, the leader is flown
from the keyboard and three follow it as a cloud, the `cruise` and `reverse`
routes are compared with the stand on SITL physics, and a key lands every
copter.

## Why

SITL gives each copter a world of its own: copters fly through each other
and through walls, and a breached bubble shows only in the tally. Gazebo puts
all of them into one world, so a mistake of the agent ends in a collision
that can be seen. It is also the ground the next stage needs, where cameras
and range finders of Gazebo replace the virtual senses of `world`.

## Out of scope

- No sensors of Gazebo: `world` keeps sending the virtual senses.
- No new behaviour of the agent beyond fitting its reaction to the new
  frame.
- No third dimension: every drone holds one altitude.
- No real hardware.

## Architecture

```
┌─ container gazebo ────────────────────────────────────────────┐
│ Gazebo Harmonic, one world: the ground, the walls, four       │
│ copters, each with the ArduPilot plugin on its own UDP port   │
└──────▲───────────────▲───────────────▲───────────────▲────────┘
       │ UDP: motors down, the state of the copter up            │
┌─ uav1 ┴──────────────┐ ┌─ uav2 ┴─┐ ┌─ uav3 ┴─┐ ┌─ uav4 ┴─┐
│ ArduPilot SITL,      │ │  same   │ │  same   │ │  same   │
│ physics from Gazebo  │ │         │ │         │ │         │
│ MAVROS               │ │         │ │         │ │         │
│ liftoff, board       │ │         │ │         │ │         │
└──────────▲───────────┘ └───▲─────┘ └───▲─────┘ └───▲─────┘
           │                 │           │           │
═══════════╧══════ Docker network, ROS 2 over DDS, one ROS_DOMAIN_ID ═════
           │
┌─ container ground ────────────────────────────────────────────┐
│ world, pilot and viewer, as on the stand with SITL physics    │
└───────────────────────────────────────────────────────────────┘
```

- SITL no longer moves the copter. It sends the commands of its motors to
  the plugin of its copter in Gazebo and takes back the state of the copter.
- Nothing changes in `agent/`, in the board or in the messages. Gazebo is a
  new air, as SITL was a new air for the formula.
- Gazebo shows the cloud in its own window; the window of `ground` stays,
  since it shows the bubbles, the trails and the leader.

## Time

With Gazebo, SITL runs in lockstep: the firmware waits for every step of the
physics. When Gazebo is slower than real time, the whole world slows down,
while the board and the ground now tick by the wall clock and would run
ahead of it. They move to the time of the simulation: Gazebo publishes its
clock, a bridge brings it into ROS as `/clock`, and every node runs with
`use_sim_time`.

## The machine

The graphics card is an Intel UHD 730, passed into the container through
`/dev/dri`. It should carry a simple world with four copters and a window;
cameras on every copter would be too much for it, which is one more reason
to leave sensors to the next stage.

## Steps

Each step ends with something that runs and is checked by hand or by a test.

1. Gazebo in a container. An image with Gazebo Harmonic and the ArduPilot
   plugin; an empty world opens in a window on the screen. Done in part:
   `docker/gazebo/Dockerfile` builds `flocking-gazebo` on the local image
   `jazzy-gz` (ROS 2 Jazzy desktop-full with `ros-gz`, Gazebo Sim 8.11) and
   compiles `ardupilot_gazebo` from source, which needs the development
   files of GStreamer for its camera plugin. The service `gazebo` runs only
   under the profile `gazebo` until the copters fly in it; headless, its
   server keeps the clock and the topics of the world. Whether the window
   opens on this screen is for the user to see:
   `docker compose --profile gazebo up gazebo`.
2. One copter. A copter model in the world, SITL in the drone container
   taking its physics from Gazebo; the copter takes off through `liftoff`
   and hovers. Done: `docker/gazebo/worlds/cloud.sdf` is the runway world of
   the plugin with its origin on the shared spot and one copter,
   `docker/gazebo/models/cloud_iris`, a copy of `iris_with_ardupilot` whose
   plugin listens on every address instead of the local host only. With
   `GAZEBO` naming the gazebo host, the drone starts SITL as
   `--model JSON:<address of that host>` with `autopilot/gazebo_iris`, the X
   frame of the Iris, and the copter took off to 3.18 m and held it.

   Three things were found on the way. The runway model is also the ground:
   a world without it lets the copter fall forever. ArduCopter refuses to
   arm before its checks pass, so `Placed` now waits for the bit of
   `sys_status` that says they did. And it refuses a takeoff for a while
   after those checks pass, with no sign of when it will accept one, while
   it disarms idle motors after some seconds on the ground; `Persistent`
   flies the whole takeoff again, three seconds apart, for up to two
   minutes.
3. The time of the simulation. The board and the ground tick by `/clock`;
   slowing Gazebo down slows the cloud down with it, without a breach. Done in part:
   the gazebo container bridges its clock into ROS as `/clock`, and with
   `GAZEBO` set the board and the ground run with `use_sim_time`; the ground
   now keeps its beat with a `Rate` of its node instead of the clock of
   pygame. The board sent 19.8 targets a wall second at full speed and 10.1
   at half speed, twenty a simulated second in both, and held the copter at
   3.00 m at full speed.

   Slowing Gazebo down does not work: at half speed the copter climbs at
   0.8 to 1 m/s whatever it is asked, with the board or with targets sent by
   hand, and with `no_time_sync` of the plugin set either way. SITL keeps the
   pace of the wall clock while the physics runs slower. Until this is
   understood, the stand needs Gazebo at full speed, and a drop of its real
   time factor is to be watched for.
4. The answer of the copter. Its answer to a step of speed is measured in
   Gazebo, and the lag of the formula and the reaction of the agent are
   fitted to it.
5. Four copters and the ground. The cloud flies as it does on SITL physics;
   `cruise` and `reverse` are compared with the earlier runs.
6. Walls. The walls of the barrier stand in the Gazebo world where the
   virtual walls are, so a copter that misses the gap hits one.
7. Landing. A key lands every copter, `RTL` brings them home, and stopping
   the stand lands every copter; `Transition` of `drone-control-ros2` with
   `LAND` and `RTL` is brought over for it.

## Open questions

- The image stands on `jazzy-gz`, which lives only on this machine. Another
  machine needs the same image first, or the Dockerfile moves onto an
  official base such as `osrf/ros:jazzy-desktop-full`.

- Which copter model to fly: the Iris that comes with the plugin, or a
  small frame closer to the micro drones. The answer of the copter, and with
  it step 4, depends on it.
- How SITL finds its copter across containers: by default the plugin and
  SITL talk over the local host, so the address of the gazebo container and
  a port per copter are to be set on both sides; the names of these settings
  are to be checked at step 2.
- With the JSON physics, the position of a copter comes from Gazebo and
  is counted from the home given to SITL. Whether every copter then needs
  the shared origin as its home, rather than its place in the muster, is to
  be settled at step 5.
- Where the shared origin lies: the world of Gazebo has its own origin, and
  the homes of the copters and `Census` must agree with where the models
  stand.
- Whether the ground keeps its own window once Gazebo shows the cloud, or
  draws only the bubbles over it.
