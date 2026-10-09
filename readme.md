# flocking-sim

A 2D simulator of a drone swarm that flies as a cloud behind its leader.
The full plan lives in [docs/SPEC.md](docs/SPEC.md); this stage holds one drone
flown from the keyboard.

## Install

```bash
pip install -r requirements.txt
```

## Run

```bash
python run.py
```

## Keys

| Key | Meaning |
|-----|---------|
| `W` / `S` | forward and backward along the nose |
| `A` / `D` | sideways, left and right |
| `Q` / `E` | turn left and right |
| `Esc` | close the window |

## Tests

```bash
python -m pytest
```

## Layout

| Path | Holds |
|------|-------|
| `agent/` | the algorithm of one drone, standard library only |
| `simulator/` | the world, the dynamics and the picture |
| `tests/` | one test file per feature file |
| `config.py` | every tunable number |
| `run.py` | the interactive run |
