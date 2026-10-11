# Faultline

**One network. Two engines. The same stochastic history.**

[![Verify both engines](https://github.com/mohammmad357/faultline/actions/workflows/ci.yml/badge.svg)](https://github.com/mohammmad357/faultline/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/Python-3.11%2B-53d9df)
![C](https://img.shields.io/badge/C-11-fcad61)
[![License: MIT](https://img.shields.io/badge/License-MIT-b6a1ff)](LICENSE)

[فارسی](README.fa.md) · [Measured results](results/RESULTS.md) · [Reproducibility contract](MODEL.md) · [Portfolio notes](RESUME.md)

![Faultline experiments](assets/experiment.svg)

Faultline simulates susceptible → infected → recovered transitions on a generated undirected network using the Gillespie direct method. The interesting engineering problem is reproducibility: Python and C share the graph, random-number stream, canonical event ordering and every discrete transition. Times agree within a documented floating-point tolerance.

Both engines are dependency-free. Plot regeneration optionally requires matplotlib. This is an educational mathematical simulator with arbitrary rates and synthetic networks; it is not a disease forecast or a calibrated intervention tool.

## Run in a minute

Requires Python 3.11+ and GCC (or a compatible C11 compiler). Start from a fresh clone:

```sh
git clone https://github.com/mohammmad357/faultline.git
cd faultline
mkdir -p build
gcc -std=c11 -O2 -Wall -Wextra -Wpedantic -Werror c/faultline.c -lm -o build/faultline
python python/faultline.py 200 2 3 1 314159 > python.csv
./build/faultline 200 2 3 1 314159 > c.csv
python -m unittest discover -s tests -v
```

PowerShell with Python and GCC installed (clone and enter the repository first):

```powershell
git clone https://github.com/mohammmad357/faultline.git
cd faultline
New-Item -ItemType Directory -Force build | Out-Null
gcc -std=c11 -O2 -Wall -Wextra -Wpedantic -Werror c/faultline.c -lm -o build/faultline.exe
python python/faultline.py 200 2 3 1 314159
./build/faultline.exe 200 2 3 1 314159
python -m unittest discover -s tests -v
```

Arguments: `N shortcuts beta gamma seed`. `shortcuts` means attempted random pairs per node; duplicate pairs and self-loops are discarded. A ring guarantees connectedness. Node zero starts infected; everyone else starts susceptible. Infection has rate `beta` per susceptible–infected edge, and recovery has rate `gamma` per infected node.

| Argument | Range |
|---|---|
| N | 2–2000 |
| shortcuts | 0–4 |
| beta | 0–100 |
| gamma | 1–100 |
| seed | 1–4294967295 |

CSV contains `event,time,node,transition,S,I,R`, including the initial state and every event through extinction. There are at most `2N-1` transitions. Python also exposes `simulate(...)` as a streaming generator; validate untrusted API arguments with `parameters(...)` first.

## Why this is more than a plot

- **300 paired runs** compare complete Python/C event histories, including edge cases and randomly sampled inputs. An independent replay validates graph adjacency, legal state transitions, count conservation and increasing event times.
- **Analytical checks:** beta zero yields exactly one recovery with a known waiting time; a two-node network has a known first-infection probability, checked over 2,000 seeded runs.
- **Canonical reproducibility:** explicit 32-bit xorshift, rejection sampling adjusted for its nonzero domain, sorted edges and sorted recovery candidates. No dependence on language built-in RNGs or hash iteration order.
- **Honest experiments:** 180 runs across three scenarios, every seed retained, plus seven end-to-end performance trials per engine. Early extinction is included, and topology/density confounding is called out.
- **CI:** Python 3.11/3.13, strict C warnings, AddressSanitizer and UndefinedBehaviorSanitizer on Linux.

## Regenerate results

```sh
python -m pip install -r requirements-plot.txt
python tools/experiment.py
```

The script rewrites CSVs, the environment manifest, the report and SVG/PNG figures. Simulation needs no pip packages. Timing values will vary. [Read the actual measurements](results/RESULTS.md).

## Model and engineering boundaries

This reference implementation rescans edges per event: `O(N(E+N))` worst-case time across a trajectory. Python stores `O(N+E)` data; C temporarily uses an `N×N` byte matrix during graph construction (about 4 MB at the limit), then frees it and retains `O(N+E)` data. Incremental SI tracking would improve scale but needs its own ordering contract and tests.

The graph is static; rates are integer constants; recovery is absorbing. There are no demographics, reinfection, empirical calibration, interventions, temporal contacts or population forecasts. Xorshift32 is a small reproducibility mechanism with finite period and correlations, not a cryptographic generator or a gold-standard generator for large scientific studies. Floating logarithms and finite random draws approximate continuous distributions.

Algorithm background: [Gillespie's 1977 direct-method paper](https://pubs.acs.org/doi/10.1021/j100540a008). Implementation, tests and experiments here were prepared with AI coding assistance; the portfolio claims are tied to executable evidence.

## Project map

| Path | Purpose |
|---|---|
| `python/faultline.py` | Readable reference engine and CSV CLI |
| `c/faultline.c` | C11 engine with matching event selection |
| `tests/test_faultline.py` | Parity, replay, analytical and input checks |
| `tools/experiment.py` | Seeded scenarios, benchmarks, publication plots |
| `results/` | Raw data, environment and interpretation |
| `MODEL.md` | Exact RNG and event-order contract |

MIT licensed. Suggestions and reproducible bug reports are welcome.

## Help improve this project

Try the quick start, report a reproducible issue, or pick a small documentation improvement.
See [CONTRIBUTING.md](CONTRIBUTING.md) for reporting details, development checks and evidence expected for changes.
