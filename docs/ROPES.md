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
2. A slack rope: the spring to the leader stops shoving, and pulls only
   beyond its length.
3. Matching on a taut rope only: a follower takes on the velocity of its
   leader only as far as the leader flies away from it, not toward it.
4. Stepping aside: a follower in the way of the leader moves off the line of
   the leader's flight, to the side it already stands on, and the shield
   gives way sideways as well.
5. The other scenarios: `cruise`, `reverse`, `rock`, `gap` and `pillars` do
   not get worse, and the tests of the catalogue still pass.
6. Gazebo: the four Iris fly through the cloud, along `rock`, and from the
   keyboard.

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
