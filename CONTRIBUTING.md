# Contributing to faultline

Thanks for helping make this reproducible stochastic simulation project easier to inspect and reproduce.
Small documentation fixes and reproducible bug reports are useful contributions.

## Before changing behavior

Read the README, input/model contract and measured-results report. Open an issue for a
substantial behavior or format change so the scope can be discussed first. These are
educational engineering projects; production readiness is not established.

## Report a bug

Include: All five parameters (N, shortcuts, beta, gamma, seed), Python/compiler versions, the first divergent CSV event and expected behavior.

Use the smallest synthetic input that reproduces the problem. State expected and actual
behavior, and include the exact command and commit/version. Screenshots may supplement
text output, but should not replace a reproducible command.

## Development checks

Follow the README build instructions for your OS, then run:

```sh
python -m unittest discover -s tests -v
```

Keep C11 builds warning-free using the flags in the README. Linux CI also runs address
and undefined-behavior sanitizers. A documentation-only change needs a link/command
review; a behavior change needs a regression check that exercises the changed behavior.

Example entry point (run from the repository root):

```sh
python python/faultline.py 200 2 3 1 314159
```

## Evidence required for behavior changes

Keep the documented PRNG stream and canonical event ordering. Validate full trajectories in both languages and independent replay, not only the final counts. Explain any topology/rate confounding; results are synthetic-model experiments, not forecasts.

For performance claims, retain the raw samples, workload, environment, measurement
boundary and reproduction command. Do not generalize one workload into a universal
speedup. Avoid committing large generated files unless they are an agreed reference.

## Starter ideas

### Clarify parameter examples

Add two complete commands showing beta=0 and a seeded small network, with the expected invariants and a reference to MODEL.md.

### Propose incremental SI tracking

Start with a design issue describing event ordering and parity checks; benchmark on fixed seeds only after correctness is established.

These are suggestions, not assigned tasks or promised roadmap commitments. Check open
issues before starting. A pull request should explain the problem, change, validation
and limitations. Keep unrelated edits separate and respond respectfully to review.

AI-assisted contributions are welcome when the author checks the code and can explain
the implementation and evidence. Contributions are made under this repository's MIT license.
