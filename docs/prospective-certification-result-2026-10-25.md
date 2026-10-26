# Predicting certifiability before running a monitor: result (2026-10-25)

> Owning instance. Scores `prospective-certification-declared-2026-10-25.md` (stamped at d273520 before computing).
> Script: `scripts/prospective_certification.py`. Raw: `prospective-certification-2026-10-25.json`. 44 (model, step)
> pairs: the 12 cell models and the 10 ladder learners, at one and two steps, q = 0.95.

## Predictions

- **P1 (observed ≥ L − 0.03 in ≥ 42 of 44): holds, 44 of 44.** The lemma's bound is never violated, even with the val
  bound under-covering test at one step.
- **P2 (Spearman(L, observed) ≥ 0.8): holds, 0.82** over all pairs. Within a step it is 0.91 (one step) and 0.87 (two
  steps).
- **P3 (median observed − L ≤ 0.25): holds as declared (0.21), but flattered.** 17 of 44 pairs have L = 0 (11 at one
  step, 6 at two), where both sides are near zero. Within two steps the median gap is **0.55**: L ranges 0–0.32 while
  observed ranges 0.02–0.84. At r3 ε = 1 one step, L = 0 against an observed 0.18–0.75.

## Reading

- **Valid and rank-informative, but loose.** From the exact tables and a val error quantile alone, the lemma gives a
  guaranteed floor on certifiability, and it orders models and queries correctly. It badly underestimates how much is
  certified.
- **What the looseness points to.**
  - The condition μ > 2B assumes the worst case on two counts: every window's error is as large as B, and every error
    points straight at the nearest withheld law.
  - Real errors are neither. Most are far below B (the median error is a fraction of the 95 % quantile), and their
    directions are not adversarial.
  - A tighter prospective rule needs the error *distribution*, for example Pr(μ_c > B + e) with e drawn from val
    errors, and eventually the error direction. That is ledger item 3 (do learners err toward hidden state?), which is
    now load-bearing.
- **For the story:** certifiability has a computable, guaranteed floor before any monitor runs: the prospective
  counterpart of the support audit. The gap between floor and reality is where learner behaviour, rather than
  geometry, enters.
