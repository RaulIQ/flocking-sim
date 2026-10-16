from dataclasses import dataclass
from typing import final


@final
@dataclass(frozen=True)
class Push:
    """How far the leader drives a follower ahead of it, as a blade drives snow, instead of getting past it.

    A follower stands in the way while it is ahead of the flying leader and
    within the length of its rope from the line of its flight. For as long as
    it stays there, its own move along the flight of the leader adds up; the
    longest such stretch of any follower is the push. A follower that the
    leader gets past without moving it is not pushed at all.
    """

    trial: object

    def distance(self) -> float:
        reach = self.trial.scenario.settings.swarm.cloud.leader.spring.rest
        stretches: dict = {}
        places: dict = {}
        worst = 0.0
        for _, flock in self.trial.frames():
            leader = flock.leader().body
            speed = leader.velocity.length()
            for index, drone in enumerate(flock.drones):
                if drone.leader:
                    continue
                place = drone.body.position
                offset = place.minus(leader.position)
                way = (
                    speed > 0.1
                    and offset.dot(leader.velocity) > 0.0
                    and abs(offset.x * leader.velocity.y - offset.y * leader.velocity.x) / speed
                    < reach
                )
                stretches[index] = (
                    stretches.get(index, 0.0)
                    + place.minus(places[index]).dot(leader.velocity) / speed
                    if way and index in places
                    else 0.0
                )
                places[index] = place
                worst = max(worst, stretches[index])
        return worst
