# Portfolio evidence

Suggested bullet, after you can explain and maintain the implementation:

> Built and validated Python/C11 engines for event-driven SIR simulation on synthetic networks; specified a shared 32-bit RNG and canonical event ordering, verified 300 complete cross-language trajectories, and published reproducible scenario analyses, raw benchmarks and sanitizer-backed CI.

This repository was prepared with AI coding assistance. Do not claim independent authorship, real-world epidemiological validation, production deployment or a universal performance gain. If a timing ratio is mentioned, cite the machine, workload and report.

| Interview topic | Evidence to demonstrate |
|---|---|
| Why SI edges rather than susceptible nodes? | Multiple infected neighbors contribute separate hazards |
| Why not use Python random and C rand? | Different streams, domains and implementation contracts |
| Why adjust the rejection cutoff? | Xorshift's nonzero state domain has 2^32-1 outputs |
| Why can times differ without paths differing? | Integer event selection never branches on time |
| Why include tiny outbreaks in the chart? | Conditioning on survival would change the question |
| What would you optimize? | Incremental SI indexing, with explicit event ordering and regression evidence |
| What is missing for a real forecast? | Empirical calibration, temporal networks and uncertainty validation |

Reproduce the tests, inspect an event replay, and regenerate the measurements before using this as interview evidence.
