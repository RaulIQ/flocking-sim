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
│ flight, board        │ │         │ │         │ │         │
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
`use_sim_time`. Gazebo publishes its clock on every step of the physics, a
thousand times a second, while the nodes tick twenty times a second; every
message woke every node and the whole machine lagged. The bridge therefore
writes `/gazebo/clock`, and `throttle` of `topic_tools` passes a hundred of
them a second on to `/clock`.

## The machine

The graphics card is an Intel UHD 730, passed into the container through
`/dev/dri`. It should carry a simple world with four copters and a window;
cameras on every copter would be too much for it, which is one more reason
to leave sensors to the next stage.

## Steps

Each step ends with something that runs and is checked by hand or by a test.

1. Gazebo in a container. An image with Gazebo Harmonic and the ArduPilot
   plugin; an empty world opens in a window on the screen. Done in part:
   `docker/gazebo/Dockerfile` builds `flocking-gazebo` on the official
   `ros:jazzy` with `ros-gz` (Gazebo Harmonic) installed over it and
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

   What sets the pace is not settled. Measured with one copter:

   - With the world at a real time factor of 1, simulated time runs at 1.00
     a wall second, and the copter obeys targets up and down.
   - `SIM_SPEEDUP` of SITL set to 0.5 or to 2 through MAVROS changes nothing:
     still 1.00, and Gazebo reports a real time factor of 0.999.
   - The world slowed to a real time factor of 0.5 slows simulated time to
     0.50, and then the copter climbs at 0.8 to 1 m/s whatever it is asked,
     with the board or with targets sent by hand, with `no_time_sync` of the
     plugin set either way.

   So in this setup Gazebo, not SITL, keeps the pace, and the autopilot loses
   its height when Gazebo runs slower than the wall clock. The documentation
   of ArduPilot speaks of setting the world free with a real time factor of
   0 or -1 and pacing the run with `SIM_SPEEDUP`; that way is not tried yet.
   Until then the stand needs Gazebo at full speed, and a drop of its real
   time factor, which Gazebo publishes on `/stats`, is to be watched for.
4. The answer of the copter. Its answer to a step of speed is measured in
   Gazebo, and the lag of the formula and the reaction of the agent are
   fitted to it.
   Done: measured through the whole chain, MAVROS and a loop at 20 Hz,
   which adds about 0.3 s to both frames, for a step of 1 m/s forward:

   | Copter | Nothing for | Half of the speed | Nine tenths | Back under 0.1 m/s | Peak |
   |---|---|---|---|---|---|
   | freestyle, SITL physics | 0.40 to 0.50 s | 0.65 to 0.70 s | 1.31 to 1.41 s | 1.13 to 1.18 s | 0.98 m/s |
   | Iris, Gazebo, as it comes | 0.55 to 0.65 s | 0.86 to 0.96 s | 1.16 to 1.26 s | 1.18 to 1.28 s | 1.08 m/s |
   | Iris, Gazebo, `autopilot/gazebo_iris` | 0.45 to 0.55 s | 0.71 to 0.81 s | 0.86 to 0.96 s | 0.88 to 0.98 s | 1.20 m/s |

   The tuned Iris takes `WP_ACC` 5, `PSC_JERK_NE` 50, `PSC_NE_VEL_P` 3 and
   `PSC_NE_VEL_I` 1, the speed control of the freestyle frame. It starts
   0.05 to 0.1 s later than the freestyle frame and settles sooner, so the
   lag of the formula, 0.15 s and 0.33 s, and the reaction of the agent,
   0.5 s, are kept. Its overshoot of a fifth did not change with
   `PSC_NE_VEL_P` 2 or `PSC_NE_VEL_I` 0.5.
5. Four copters and the ground. The cloud flies as it does on SITL physics;
   `cruise` and `reverse` are compared with the earlier runs. Done in part:
   the gazebo container builds its world at the start with `Arena`, which
   lays one copy of `cloud_iris` into `cloud.sdf` at every place of the
   muster, named `uav1` to `uav4`, the plugin of each on its own port from
   9002 by tens; the drone passes its port to SITL as `--sim-port-out`. The
   plugin tells SITL the position of a copter in the world, not its
   latitude and longitude, and SITL adds it to its home, so under Gazebo
   every drone takes the shared origin as its home from the node `origin`,
   and the world alone sets the places. All four took off, hovered at
   3.0 m and gathered into a cloud around the leader, with Gazebo at a real
   time factor of 1.00; their positions from MAVROS matched those in Gazebo
   within 0.1 m.

   The plugin of `main` sent the state of every copter to the container that
   spoke last: it kept the address of its autopilot in the one buffer of
   `inet_ntoa` that the whole process shares, so every other copter waited
   50 ms a step and the world crawled at 0.005 of real time. The fix waits in
   ArduPilot/ardupilot_gazebo#181 and #166, and the image builds the plugin
   from the commit of #181 until one of them is merged.

   The stand took 131 to 143 s from the start until all four hovered,
   against 47 s on SITL physics, since the world ran at 0.13 of real time
   while the copters stood on the ground and at 1.00 once they flew. Gazebo
   spends its time on the contacts of the standing copters, and the world
   had two planes for them: the runway and a `ground` model that came in
   with the first world by mistake. Gazebo alone, with no autopilots and no
   limit on its pace, ran four copters on the ground at 0.14 of real time
   with both planes and at 0.48 with the runway alone, and at 10.8 with the
   copters held in the air. Without the second plane all four hovered 46 s
   after the start. The collision detector `bullet` instead of `ode` ran the
   copters on the runway at 2.24 of real time but is not needed now.

   One run of each route on four copters, against the stand on SITL physics:

   | Route | Stand | Closest pair | Breached frames | Farthest at the end | Fastest follower at the end |
   |---|---|---|---|---|---|
   | `cruise` | Gazebo, Iris | 0.31 m | 51 | 1.29 m | 0.33 m/s |
   | `cruise` | ROS, SITL physics | 0.81 m | 0 | 1.21 m | 0.05 m/s |
   | `reverse` | Gazebo, Iris | 0.10 m | 92 | 1.90 m | 0.75 m/s |
   | `reverse` | ROS, SITL physics | 0.42 m | 6 | 1.32 m | 0.08 m/s |

   Every copter stayed in the air at 3.0 m, but the cloud holds far worse:
   at 0.10 m two Iris frames, 0.55 m across, touch. The agent is fitted to
   the freestyle frame, which reaches half of a step of speed in 0.35 s,
   while the Iris needs 0.65 s and starts 0.1 s later, so the agent asks for
   less room than the Iris takes to stop; this is what step 4 is for.

   With the Iris tuned at step 4, three runs of `cruise` and six of `reverse`:

   | Route | Closest pair | Breached frames | Farthest at the end | Fastest follower at the end |
   |---|---|---|---|---|
   | `cruise` | 0.37, 0.49, 0.49 m | 15, 2, 2 | 1.31, 1.33, 1.31 m | 0.15, 0.15, 0.21 m/s |
   | `reverse` | 0.30 to 0.39 m | 5 to 18 | 1.3 m, or 6 to 17 m | 0.05 to 0.12 m/s |

   Of the six runs of `reverse`, in three the third copter ended on the ground,
   which is what the farthest drone of 6 to 17 m shows. Logged once more, it
   came within 0.41 m of the leader flying back through the cloud and
   dropped half a metre a second later. The rotors of the Iris reach 0.355 m
   from its centre, so two of them touch when their centres come within
   0.71 m, while the hard bubble of 0.25 m lets the agent bring two drones to
   0.5 m: the bubbles are sized for the micro drones, not for the Iris.

   `frames()` in `config.py` now holds the settings of every frame, and under
   `GAZEBO` the board and the ground take those of the Iris, with a hard
   bubble of 0.4 m. It did not keep the copters apart: three runs of
   `reverse` brought them to 0.37 to 0.39 m and dropped a copter in two.
   The formula shows the same, 0.52 m in `reverse` with a hard bubble of
   0.4 m against 0.51 m with 0.25 m. A follower counts on half of the room
   to a neighbour, trusting the neighbour with the other half, while the
   leader flies what its pilot asks and gives way to no sighted neighbour,
   so a leader flying back through its cloud leaves a follower half the room
   it needs.

   That reading was wrong: halving the room makes a follower more careful,
   not less. The leader turns back and speeds up at a follower 1.2 m away,
   and a follower that answers half a second late cannot get out of its way
   in time. The user chose that the followers give way to the leader, so
   the followers of the Iris keep 2.0 m from it instead of 1.2 m, and the
   leader still flies what its pilot asks. In the formula, with the bubbles
   of the Iris:

   | Followers from the leader | `cruise` | `reverse` |
   |---|---|---|
   | 1.2 m | 0.58 m, 18 frames | 0.52 m, 49 frames |
   | 1.6 m | 0.89 m, 0 frames | 0.71 m, 18 frames |
   | 2.0 m | 1.04 m, 0 frames | 0.93 m, 0 frames |
   | 1.2 m, the leader giving way too | 0.97 m, 0 frames | 0.80 m, 3 frames |

   In Gazebo with 2.0 m, closest pair and breached frames:

   | Route | Runs | Every copter in the air |
   |---|---|---|
   | `cruise` | 0.92 m, 0; 0.87 m, 0 | yes |
   | `reverse` | 0.72 m, 6; 0.80 m, 0; 0.38 m, 74 | yes |

   The third run of `reverse` still brought two copters within 0.38 m for a
   long while; which pair it was is not known yet.
6. Walls. The walls of the barrier stand in the Gazebo world where the
   virtual walls are, so a copter that misses the gap hits one.
7. Landing. A key lands every copter, `RTL` brings them home, and stopping
   the stand lands every copter; `Transition` of `drone-control-ros2` with
   `LAND` and `RTL` is brought over for it.
   Done: the node `liftoff` became `flight`. Started with
   `command:=takeoff` it takes off once and quits, as `liftoff` did, and the
   board starts after it; started with no command it stays and answers the
   words `takeoff`, `land` and `rtl` on `flight_command` through `Dispatch`
   with `Persistent(Takeoff)` and `Transition` to `LAND` or `RTL`, both
   brought over from `drone-control-ros2`. The keys T, L and H of the ground
   send these words to every copter, by scancode. All four landed where they
   were, took off again to 3.0 m and gathered into the cloud, and flew home
   and landed.

   A takeoff after a landing first failed: the board went on asking for a
   speed, and a speed asked in GUIDED cancels the takeoff the autopilot has
   begun. The board now asks for nothing until the autopilot says the copter
   is in the air, through `EXTENDED_SYS_STATE`, which ArduPilot sends only
   when asked, so `flight` asks for it five times a second after the first
   takeoff. `RTL` brings a copter to where it last armed, since ArduPilot
   sets its home then. Stopping the stand stops the autopilots with it, so
   there is nothing left to land.

   The words first went one at a time, and a takeoff asked while the copters
   still came down kept switching them back to GUIDED for two minutes under
   `Persistent`, while the landing waited behind it. Now only the first
   takeoff is persistent, the takeoff of the key is tried once, and the
   words run side by side, so a landing is never kept waiting.

## Open questions

- Which copter model to fly: the Iris that comes with the plugin, or a
  small frame closer to the micro drones. The answer of the copter, and with
  it step 4, depends on it.
- How SITL finds its copter across containers is settled: the plugin
  listens on every address at its own port, and SITL sends to the gazebo
  host at that port.
- The homes are settled: every drone takes the shared origin as its home,
  which is the origin of the world, and the copters stand at their places
  in the world, so `Census` reads them as it did.
- Whether the ground keeps its own window once Gazebo shows the cloud, or
  draws only the bubbles over it.
