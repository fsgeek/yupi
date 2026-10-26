# Worst-case certification across cells: result (2026-10-25)

> Owning instance. Scores `certified-bound-cells-declared-2026-10-25.md` (stamped at a309740 before running). Raw:
> `certified-bound-cells-2026-10-25.json`. 12 models (d128, 15 epochs, 3 seeds per cell); val 2,000 / test 10,000
> windows each; k = 6. The certifier uses no prior.

## Certified share of pure windows at q = 0.95, one step → two steps (seeds 1 / 2 / 3)

| cell (coin's exact margin at k = 6, one step → two) | one step | two steps | false certificates (max) |
|---|---|---|---|
| r1, ε = 1 (0.045 → 0.175) | 0.075 / 0.082 / 0.102 | 0.787 / 0.800 / 0.810 | 0.16 % |
| r1, ε = ½ (0.023 → 0.167) | 0.000 / 0.000 / 0.000 | 0.746 / 0.744 / 0.670 | 0.21 % |
| r3, ε = 1 (0.075 → 0.192) | 0.264 / 0.745 / 0.178 | 0.742 / 0.784 / 0.720 | 0.35 % |
| r3, ε = ½ (0.027 → 0.134) | 0.001 / 0.001 / 0.000 | 0.319 / 0.327 / 0.345 | 0.44 % |

## Predictions

- **C1 (two steps > one, every model): holds, 12 of 12.**
- **C2 (one step ≤ 0.15, every model): fails at r3 ε = 1,** with 0.178–0.745. It holds in the other three cells.
- **C3 (two steps ≥ 0.4, every model): fails at r3 ε = ½,** with 0.319–0.345. It holds in the other three.
- **C4 (false certificates ≤ 0.06): holds.** The maximum is 0.44 %.

## Reading

- **"A single output almost never certifies randomness" is cell-dependent.** It holds where the exact one-step margin is
  narrow (0.023–0.045: r1 at both ε, r3 at ε = ½). It fails where the margin is widest (0.075, r3 ε = 1): there a
  precise learner can certify up to 75 % with one output. The seed spread at r3 ε = 1 (0.18–0.75) suggests the
  outcome sits near a threshold, where small differences in learner precision decide.
- **The second step helps in every cell. How much follows the exact two-step margin:** 0.134 at r3 ε = ½, the
  narrowest, gives the lowest two-step share (about ⅓).
- **The ordering is suggestive, not tested:** across cells, certifiability appears to be set by the exact margin
  relative to the learner's error bound. The margin is a pre-training quantity, so this is a candidate *prospective*
  rule: from the exact tables and a bound on learner error, predict which queries can certify before running any
  monitor. That is the next declared test, not a finding yet.

## The story after this

Without a prior, a single answer certifies "randomness, not hidden state" only where the world's exact one-step margin
is wide relative to the learner's error. A second question widens the margin in every cell, and certification follows
it. Both margins can be computed before training.
