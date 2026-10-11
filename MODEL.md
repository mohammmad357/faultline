# Reproducibility contract

## State and rates

States are S=0, I=1, R=2. Start with node 0 infected. For each SI edge, infection occurs at beta; each I node recovers at gamma. Let m be the number of SI edges and i the number of infected nodes. The total rate is `a = beta*m + gamma*i`. Gamma is positive, so a is positive whenever i>0.

The direct method draws `dt = -log(U)/a` and chooses one event by its rate. An integer ticket in `[0,a)` selects an infection if it is less than `beta*m`, otherwise a recovery. Multiple infected neighbors give a susceptible node multiple SI-edge entries, correctly increasing its infection rate.

## Random stream

Seed is a nonzero uint32. For each next draw:

```
x ^= x << 13
x ^= x >> 17
x ^= x << 5
```

Truncate left shifts and state to 32 bits. The nonzero domain is `1..4294967295`; zero seeds are rejected. For bounded sampling with bound b, set `L=floor(4294967295/b)*b`. Draw `z=next()-1`; reject z>=L; return z modulo b. Using the usual 2^32 cutoff without adjusting this domain would introduce a small mapping bias.

For each waiting time, consume one raw draw and set `U=next()/4294967296.0`, strictly between zero and one. Then consume bounded draws for the ticket, including any rejected proposals. This is a finite PRNG approximation, not an ideal source of independent real-valued randomness.

## Graph and event ordering

1. Add all ring pairs `(j,(j+1)%N)`.
2. Make exactly N*shortcuts random-pair attempts. Each consumes `below(N)` for a, then for b. Ignore loops and duplicates, including ring duplicates.
3. Canonicalize each pair to a<b and sort the final edges lexicographically. The N=2 ring is a single edge.
4. Every event scans edges in that order and collects the susceptible endpoint of each SI edge. Candidate duplicates remain because each edge contributes rate.
5. Infection selects candidate `ticket//beta`. With beta=0 the infection branch cannot occur.
6. Recovery selects the infected node at ascending-node index `(ticket-beta*m)//gamma`.

No extra random draws, graph regeneration, node randomization or hash traversal occurs during simulation. Each node is infected at most once and recovered at most once: at most 2N-1 transitions after the initial row.

## Equality and numerical limits

Event numbers, node IDs, transitions and S/I/R counts must match exactly. Times are doubles, printed with 12 decimal places. Tests use `rel_tol=1e-11`, `abs_tol=2e-12`; libm implementations and summation rounding can differ. Times never control event selection, so those differences cannot change the discrete trajectory.

CLI inputs must be ASCII unsigned decimal strings within documented limits. Seed zero, negative signs, fractional rates, Unicode digits and malformed suffixes are rejected before output. Bounds prevent uint32 propensity overflow; graph storage capacity is N*(shortcuts+1).

These rules apply to v0.1.0. A new RNG, ordering, topology generator or draw schedule would be a reproducibility-breaking change even if marginal distributions looked similar.
