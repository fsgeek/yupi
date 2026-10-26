# Worst-case certification across cells: declared before running (2026-10-25)

> Owning instance. Generalisation check of `certified-bound-result-2026-10-25.md` (r1 ε = 1, ten learners) to the 12
> models of 10-23: r1 and r3 at ε ∈ {1, ½}, 3 seeds each, k = 6. Existing val (2,000) and test (10,000) dumps; the test
> windows were never used for calibration. Same certifier and q values; the script gains a per-cell family and a
> no-exclusion mode only.

## Predictions (q = 0.95)

- **C1.** In every cell, two steps certify a larger share of pure windows than one step, for every seed.
- **C2.** In every cell, the one-step certified pure share is at most 0.15 for every seed.
- **C3.** In every cell, the two-step certified pure share is at least 0.4 for every seed.
- **C4.** The false-certificate rate is ≤ 0.06 for every model, at both s (B2's bound at q = 0.95).

These predictions extrapolate from r1 ε = 1. In particular, r3 ε = 1 had the widest one-step margin (0.075 at k = 6),
so C2 is the most at risk there.
