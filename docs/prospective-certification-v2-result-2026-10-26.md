# A tighter prospective floor from the error distribution: result (2026-10-26)

> Owning instance. Scores `prospective-certification-v2-declared-2026-10-26.md` (stamped at 40c8d5d before computing).
> Script: `scripts/prospective_certification_v2.py`. Raw: `prospective-certification-v2-2026-10-26.json`.

## Predictions (44 pairs: 22 models × one and two steps)

- **V1 (observed ≥ L2 − 0.03 in ≥ 42 of 44): holds, 44 of 44.**
- **V2 (two-step median gap ≤ 0.30): holds, 0.246,** against 0.553 for the size-worst-case floor L. L2 ranges
  0.001–0.63 at two steps.
- **V3 (Spearman(L2) ≥ Spearman(L) within each step): fails at one step** (0.74 against 0.91) and holds at two steps
  (0.93 against 0.87). The one-step comparison is fragile: 11 of 22 one-step L values are 0, and the rank computation
  breaks ties arbitrarily. It was declared, so it stands as a failure.

## Reading

- **About half of the two-step floor's looseness came from assuming every error is as large as the bound.** Using the
  learner's actual val error distribution (still assuming the worst direction) closes the median gap from 0.55 to
  0.25.
- **The remaining gap is direction plus the independence assumption.** It has a size now: about 0.25 at two steps.
  That is the ledger's item 3 (do learners err toward or away from hidden-state alternatives?), and it now has a
  target.
- **The prospective rule, as it stands:** from the exact tables, a val error distribution and a stated risk q, one
  can compute before running any monitor a floor that is valid in every case tried and within about 0.25 (median) of
  what a prior-free certifier achieves at two steps.
