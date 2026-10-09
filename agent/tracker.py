from dataclasses import dataclass
from typing import final

from agent.senses import Senses
from agent.tracks import Track, Tracks
from agent.vector import Vector


@final
@dataclass(frozen=True)
class Tracker:
    """Keeps the tracks of one drone up to date, tick after tick.

    Each track is first carried along with the drone's own turn and flight,
    as if the neighbour stood still, and then corrected: a range sets its
    length, a bearing sets its direction. A neighbour ranged but never sighted
    stays without a direction. This is the plainest filter that does the job;
    the uncertainty and the gains of an alpha-beta or a Kalman filter belong
    behind the same method.
    """

    lapse: float

    def after(self, tracks: Tracks, senses: Senses) -> Tracks:
        known = {track.tag: track for track in tracks.items}
        ranges = {echo.tag: echo.distance for echo in senses.signals.ranges}
        bearings = {sight.tag: sight.angle for sight in senses.signals.bearings}
        roles = {word.tag: word.leader for word in senses.signals.roles}
        return Tracks(
            tuple(
                self.track(tag, known, ranges, bearings, roles, senses)
                for tag in sorted(set(known) | set(ranges))
            )
        )

    def track(self, tag, known, ranges, bearings, roles, senses: Senses) -> Track:
        sighted = tag in bearings or (tag in known and known[tag].sighted)
        carried = (
            known[tag]
            .offset.turned(-senses.motion.spin * self.lapse)
            .minus(senses.motion.velocity.times(self.lapse))
            if tag in known and known[tag].sighted
            else known[tag].offset
            if tag in known
            else Vector(ranges[tag], 0.0)
        )
        length = ranges.get(tag, carried.length())
        return Track(
            tag,
            Vector(length, 0.0).turned(bearings[tag])
            if tag in bearings
            else carried.times(length / carried.length())
            if sighted and carried.length() > 0.0
            else Vector(length, 0.0),
            sighted,
            roles.get(tag, tag in known and known[tag].leader),
        )
