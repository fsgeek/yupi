# The escape hatch's scalar against the full distribution, on one scale: declared before computing (2026-10-27)

> `entropy-learner-precision-result-2026-10-27.md` scored entropy observers by AUC. The full-distribution certifier
> was scored by certified share, so the two could not be compared. This puts both on the AUC scale, on the same 22
> learners and the same test windows.

**Full-distribution score:** M = d_pure − d_withheld, where d is the TV distance from the learner's output to the
nearest pure law and to the nearest withheld law (G ≥ 0.1), from the k = 6 family as in `scripts/certified_bound.py`.
A larger M is more withheld-like. M1 uses q1 and the one-step laws; M2 uses q2 and the two-step laws. The entropy
scores S1 and S3 are as declared in `entropy-learner-precision-declared-2026-10-27.md`.

## Predictions (22 learners)

- **C1.** AUC(M1) ≥ AUC(S1) in at least 20. At one step, the distribution carries more than its entropy.
- **C2.** AUC(M2) ≥ AUC(S3) in at least 20. With depth, the distribution beats the best scalar profile.
- **Estimand (no prediction):** the median of AUC(M2) − AUC(S3), which is what the exported scalar costs once a
  second question is asked.

If C2 fails, a two-number entropy profile is as good as the whole distribution for this separation. That would be a
strong result for the escape hatch, provided the profile is exported.
