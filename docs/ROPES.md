# Stage: the cloud on ropes

Issue: #11.

## Goal

Let the leader fly through its own cloud. Today a leader flown into the cloud
pushes it ahead, as a blade pushes snow. It should look as if every follower
hangs on a rope from the leader: the leader pulls a follower that lags behind
and never pushes one, and when it flies into the cloud the followers step
aside, let it through and close up behind it.

Done when, in the 2D simulator and then on the four Iris copters in Gazebo,
the leader flies through the middle of its cloud and gets past the followers
in its way with no breached frame, the cloud follows it again afterwards, and
the cloud keeps its copters apart while the leader is rocked forward and back
as in #9.

## Why

A pilot needs to fly the leader anywhere around and through the cloud, not
only ahead of it. The specification asks for the same thing from a moving
object passing through the cloud: the drones part and close up behind it. And
the collisions of #9 come from the same place: a follower that stands on the
line of the leader backs away along that line instead of leaving it.

## What pushes the cloud today

Three things in the agent of a follower move it away from a leader that comes
at it, all of them along the line between the two:

1. The spring to the leader in `Instinct`: closer than its rest distance it
   shoves the follower straight away from the leader.
2. The matching of the leader's velocity in `Instinct`: a follower adds the
   velocity of its leader to whatever else it wants, so a follower ahead of a
   leader flying at it flies away at the leader's speed.
3. The shield in `Shield.kept`: a follower that the leader closes on too fast
   gives way along the line between them.

A rope does none of this. It pulls only when it is taut, it does not drag a
follower along while it hangs slack, and it does not push at all.

## Steps

Each step ends with something that runs and is checked by a test or a
scenario. The 2D simulator comes first: its runs take seconds.

1. A scenario that flies the leader through the middle of its cloud, and the
   numbers that tell pushing from passing: how far the cloud moves ahead of
   the leader before the leader gets in, how many followers the leader gets
   past, the closest pair and the breached frames. Measured on the cloud as it
   flies now, for eight drones and for the four Iris of the stands.
   Done: the scenario `through` flies the leader 2 m ahead, turns it and
   flies it at 1 m/s straight through its cloud to 8 m behind the start.
   `Push` in `scenarios` counts how far the leader drives a follower ahead of
   it: while a follower is ahead of the flying leader and within the length of
   its rope from the line of its flight, its move along that flight adds up,
   and the longest such stretch is the push. On the formula, as the cloud
   flies now, with the closest pair, the breached frames and the push:

   | Scenario | Eight drones | Four freestyle | Four Iris |
   |---|---|---|---|
   | `through` | 0.23 m, 179, 9.4 m | 0.67 m, 0, 5.0 m | 1.04 m, 0, 7.7 m |
   | `rock` | 0.07 m, 313, 0.9 m | 0.65 m, 0, 1.0 m | 1.07 m, 0, 1.2 m |
   | `reverse` | 0.34 m, 55, 7.0 m | 0.51 m, 0, 0.4 m | 0.93 m, 0, 3.5 m |
   | `cruise` | 0.30 m, 38, 11.4 m | 0.60 m, 0, 0.4 m | 1.04 m, 0, 3.0 m |
   | `gap` | 0.28 m, 123, 1.7 m | 0.72 m, 0, 1.9 m | 0.86 m, 0, 2.2 m |
   | `pillars` | 0.36 m, 123, 3.8 m | 0.69 m, 0, 1.5 m | 0.88 m, 0, 1.5 m |

   Most followers are passed untouched; the one on the line of the leader is
   driven ahead of it for metres, which is the blade the pilot sees. A test of
   the catalogue asks for a push under 1 m in `through` and is marked as
   expected to fail until the ropes hold.
2. A slack rope: the spring to the leader stops shoving, and pulls only
   beyond its length. Tried and dropped: with no shove the followers drift up
   to the leader until only the shield stops them, and the breached frames
   grow from none to hundreds, for every length of rope tried, 1.2 to 3.0 m.
   The spring keeps its shove for a follower out of the way of the leader.
3. Matching on a taut rope only: a follower takes on the velocity of its
   leader only as far as the leader flies away from it, not toward it.
4. Stepping aside: a follower in the way of the leader moves off the line of
   the leader's flight, to the side it already stands on, and the shield
   gives way sideways as well.

   Steps 3 and 4 are done together by `Tow` in `agent`. A follower stands in
   the way while it is ahead of the flying leader, within the rest of the
   spring of the line of its flight, and no farther ahead than the rest plus
   what the leader flies in the horizon of the `Rope`, 1.5 s. Such a follower
   is neither carried along with the leader nor held by the spring; it steps
   off the line to its own side at the speed of the leader plus the gain of
   the rope, 2 m/s for every metre still inside the way, no faster than a
   drone flies. Every other follower flies along with the leader and is held
   by the spring, as before. The shield is left as it was. The ropes grow
   longer: 2.0 m for the copters of the stands, 3.0 m for the Iris, 1.2 m for
   the drones of the simulator as before. The scenario `circle` flies the
   leader twice around a circle 5 m across at 1.5 m/s. On the formula, with
   the closest pair, the breached frames and the push:

   | Scenario | Four freestyle, rope 2.0 m | Four Iris, rope 3.0 m |
   |---|---|---|
   | `circle` | 0.87 m, 0, 7.1 m | 0.95 m, 0, 10.4 m |
   | `through` | 1.04 m, 0, 0.0 m | 1.13 m, 0, 0.3 m |
   | `rock` | 1.20 m, 0, 0.5 m | 1.20 m, 0, 0.4 m |
   | `reverse` | 0.97 m, 0, 0.0 m | 1.13 m, 0, 0.1 m |
   | `cruise` | 1.03 m, 0, 0.0 m | 1.02 m, 0, 0.0 m |
   | `pillars` | 0.91 m, 0, 0.0 m | 1.02 m, 0, 0.0 m |
   | `gap` | 0.78 m, 0, 0.0 m | 0.87 m, 0, 0.0 m |

   The leader flies through its cloud and no scenario breaches a bubble.
   The push on the circle is likely the measure, not a blade: the turning
   leader keeps flying toward the followers inside its turn. Eight drones of
   the simulator still breach bubbles in every scenario, as they did before.
5. The other scenarios: `cruise`, `reverse`, `rock`, `gap` and `pillars` do
   not get worse, and the tests of the catalogue still pass.
6. Gazebo: the four Iris fly through the cloud, along `rock`, and from the
   keyboard. Tried before the wedge: the copters swayed and two of them
   breached, because the tracker takes the velocity of a neighbour from the
   difference of two measurements, which turns their centimetre of noise into
   half a metre a second. Left for later; the 2D simulator comes first.
7. A wedge instead of a ring, asked for after the pilot flew the eight drones
   of the simulator: the followers stood too far from the leader, and those on
   the side it turned to got in its way. Done in `agent`:

   - `Wings`: behind a flying leader the followers are pulled, at the pull of
     the `Wedge`, toward the nearest point of two wings that leave its line of
     flight backward at 45°, start a spring rest behind it and run for 4 m.
     The wing on the inside of a turn folds toward the track of the leader, the
     more the harder the pilot turns, and lies right behind it at the top spin.
     A hovering leader still holds its followers around it by the spring.
   - `Way`: the way of the leader bends into the arc of the turn the pilot
     asks for. Every drone hears the pilot, so a follower knows the bend as
     soon as the leader does.
   - `Sweep`: while the pilot holds a turn, a follower inside the circle the
     leader goes round, widened by the clearance of the `Wedge`, flies along
     and moves straight out of it.
   - All ropes are 1.2 m again, for the Iris as well.

   In the prototype, with no wall, eight drones and four Iris fly U-turns of
   1.1 to 6 m radius, a left and right zigzag and two full circles in a row at
   full speed with no breached frame. With walls the wedge is often worse: its
   wings spread the cloud sideways and press it into the wall beside a gap.
   The catalogue, closest pair and breached frames, before and after:

   | Scenario | Ring | Wedge |
   |---|---|---|
   | `cruise` | 0.26 m, 120 | 0.16 m, 106 |
   | `reverse` | 0.14 m, 69 | 0.09 m, 24 |
   | `gap` | 0.21 m, 149 | 0.36 m, 62 |
   | `gap_fast` | 0.54 m, 0 | 0.18 m, 76 |
   | `gap_ten` | 0.26 m, 103 | 0.43 m, 42 |
   | `gap_sideways` | 0.14 m, 180 | 0.05 m, 93 |
   | `gap_back` | 0.24 m, 25 | 0.21 m, 183 |
   | `two_gaps` | 0.45 m, 69 | 0.28 m, 93 |
   | `rock` | 0.01 m, 124 | 0.22 m, 184 |
   | `pillars` | 0.38 m, 58 | 0.32 m, 176 |
   | `wall` | 0.44 m, 41 | 0.56 m, 0 |

   Two tests are marked as expected to fail: in `wall` a follower slips
   through the gap beside the wall, and in `Flock` a leader flown back through
   its wedge at full speed brings two followers 0.44 m apart.

## Where to pick up

- Put the scenarios of the prototype into the catalogue: U-turns, the
  zigzag and full circles, on open ground with no wall. They need a helm
  that turns, which `Route` cannot, and a course with nothing in it.
- Narrow the wedge near walls, so that the cloud passes a gap as it did
  before.
- Tune the wedge for eight drones flying straight and stopping, `cruise`
  and `through`.
- The Iris at 1.2 m: after the leader stops, the shield can pin a follower
  between the leader and a peer, since its hard bubble of 0.4 m leaves the
  shield little room.
- Gazebo: the noise of the measured velocity, then the four Iris.

## Open questions

- How long a rope is: the rest distance of the leader spring today, 2.0 m for
  the Iris and 1.2 m for the micro drones, or longer.
- How wide the way of the leader is, and how far ahead of it a follower starts
  to step aside: a fixed width, or as far as the leader covers in the reaction
  of a follower.
- What a follower does that cannot step aside, with walls or peers on both
  sides: the shield must still keep it from the leader.
- Whether the leader should slow down, as a last resort, when a follower is
  still in its way: it would break the rule that the pilot is obeyed exactly.
- Whether a follower should rather rise out of the way than step aside, and
  sink back to the height of the cloud once the leader has passed: it needs
  the third dimension, which the simulator does not have yet.
