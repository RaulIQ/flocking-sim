# flocking-sim

A 2D simulator of a drone swarm that flies as a cloud behind its leader.
The full plan lives in [docs/SPEC.md](docs/SPEC.md); this stage holds a leader
flown from the keyboard and followers that fly after it as a cloud. Each
follower is shoved away by close neighbours, pulled toward distant ones up to a
limit, and pulled harder toward the leader. For now the followers are told the
true places of the others; the noisy sensors come later.

On screen the red ring is the hard bubble, the blue ring is the soft one, and
the amber drone is the leader.

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
