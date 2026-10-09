# flocking-sim

A 2D simulator of a drone swarm that flies as a cloud behind its leader.
The full plan lives in [docs/SPEC.md](docs/SPEC.md); this stage holds a leader
flown from the keyboard and followers that fly after it as a cloud. Each
follower is shoved away by close neighbours, pulled toward distant ones up to a
limit, pulled harder toward the leader, and shoved away by a wall that comes
close. A wall with one gap stands across the way: fly the leader through the gap
and the cloud stretches into a file, squeezes through and gathers again. For now
the followers are told the true places of the others and the true nearest point
of each wall; the noisy sensors come later. Walls only shove the followers away,
nothing stops a drone that is flown into one, the leader included.

On screen the red ring is the hard bubble, the blue ring is the soft one, the
amber drone is the leader and the pale line is the wall.

## Install

```bash
pip install -r requirements.txt
```

## Run

```bash
python run.py
```

## Keys

| Control | Meaning |
|---------|---------|
| `W` / `S` or `Up` / `Down` | forward and backward along the nose |
| `A` / `D` or `Left` / `Right` | sideways, left and right |
| mouse | the nose of the leader turns toward the pointer |
| `Tab` | pass the lead to the next drone |
| left click | hand the lead to the drone under the pointer |
| `Esc` | close the window |

The pointer sets the heading the drone wants, not the heading it has: the nose
swings around under the same spin and twist limits as the rest of the flight.

Keys are read by scancode, by the physical place of a key rather than the letter
a layout prints there, so the drone flies under a Cyrillic layout too.

## Tests

```bash
python -m pytest
```

## Layout

| Path | Holds |
|------|-------|
| `agent/` | the algorithm of one drone, standard library only, blind to the simulator |
| `simulator/` | the world, the dynamics and the picture |
| `tests/` | one test file per feature file |
| `config.py` | every tunable number |
| `run.py` | the interactive run |
