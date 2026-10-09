# flocking-sim

A 2D simulator of a drone swarm that flies as a cloud behind its leader.
The full plan lives in [docs/SPEC.md](docs/SPEC.md); this stage holds a leader
flown from the keyboard and followers that fly after it as a cloud. Each
follower is shoved away by close neighbours, pulled toward distant ones up to a
limit, pulled harder toward the leader, and shoved away by a wall that comes
close. A wall with one gap stands across the way: fly the leader through the gap
and the cloud stretches into a file, squeezes through and gathers again. For now
the followers are told the true places of the others and the true nearest point
of each wall; the noisy sensors come later.

The leader cannot be flown into a wall: its request is cut so that it never
closes on a wall faster than it can brake, and it stops a hard bubble away. It
still slides along the wall and flies away from it freely. The followers are
only shoved away by walls, nothing yet guarantees that they keep clear.

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

## Scenarios

A scenario is a scripted flight: the leader follows a fixed route instead of the
keyboard, so the same run can be repeated and compared after every change.
Nothing in a run is random, the same scenario always gives the same numbers.

```bash
python -m scenarios                # list the scenarios
python -m scenarios gap            # run one and print its summary
python -m scenarios gap wall       # run several
python -m scenarios all            # run every one
python -m scenarios gap --watch    # run it, then play it in a window
```

Each run writes two files into `scenarios/logs/`:

| File | Holds |
|------|-------|
| `<name>.txt` | the summary: closest pair, closest wall, breached frames, who got beyond the wall |
| `<name>.csv` | where every drone was and how fast it flew, ten times a second |

The summaries are small and kept in git, so `git diff scenarios/logs` shows how
a change in the code moved the numbers. The traces are large and ignored.

A frame counts as breached when two hard bubbles overlap or when a wall reaches
into the hard bubble of a drone. New scenarios go into
`scenarios/catalogue.py`.

## Layout

| Path | Holds |
|------|-------|
| `agent/` | the algorithm of one drone: `Mind.command(Senses)` gives a `Command`; standard library only, blind to the simulator |
| `simulator/` | the world, the dynamics and the picture |
| `scenarios/` | scripted flights and their logs |
| `tests/` | one test file per feature file |
| `config.py` | every tunable number |
| `run.py` | the interactive run |
