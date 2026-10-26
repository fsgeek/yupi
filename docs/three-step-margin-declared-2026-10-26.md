# Does asking more keep paying? Three-step margins, declared before computing (2026-10-26)

> Owning instance. Exact side only. Position k = 5 (records 6, 7 and 8 all inside the window), r0–r4, both ε, from
> `scripts/three_step_split.py`. Kinds as before (pure: G < 1e-12, H\* > 1e-12; withheld: G ≥ 0.1; one-step G at
> k = 5). μ_d is the TV from a pure class's d-step law to the nearest withheld class's d-step law, at floor 0
> (existential). The coin is the one-step law (⅔ DISPATCH, ⅓ IO_COMPLETE).

## Predictions

- **D0 (check, by data processing).** μ1 ≤ μ2 ≤ μ3 for every pure class.
- **D1 (diminishing returns).** The coin's median μ3/μ2 < μ2/μ1 at every content interface r1–r4 and both ε.
- **D2 (still worth asking).** The coin's median μ3 ≥ μ2 + 0.03 at every content interface and both ε.
- **D3 (beyond the coin).** Over all pure classes (mass-weighted median), μ3 > μ2 at every content interface and
  both ε.

**Why it matters.** If D1 and D2 hold, there is an optimal query depth per learner, the depth at which learner error
compounding overtakes the widening margin. That depth can be computed from the exact tables and the learner's
per-depth error. If D2 fails, two steps already capture what asking can give in this world.
