# Predicting certifiability before running a monitor: declared before computing (2026-10-25)

> Owning instance. All 22 models with k = 6 dumps (12 cell models, 10 ladder learners), q = 0.95, one and two steps.

**The rule (a lemma, not an empirical fit).**
- Let μ_c be the exact distance from a pure class's law to the nearest withheld (G ≥ 0.1) law, at step depth s.
- If μ_c > 2B and the window's error e ≤ B, the prior-free certifier must certify "pure". The true law is within B,
  and every withheld law is at least μ_c − e > B away.
- So the certified share of pure windows is at least Pr(μ_c > 2B and e ≤ B).

**Prediction from pre-monitor quantities:**
- The class masses and μ_c come from the exact tables (RESET masses halved). B comes from val.
- e ≤ B is taken as independent of class, with probability q:
  L = q × (pure mass with μ_c > 2B) / (pure mass).
- Computed without running the certifier.

## Predictions

- **P1 (the bound).** Observed certified pure share ≥ L − 0.03, for at least 42 of the 44 (model, step) pairs. The
  slack covers the independence assumption and val-to-test error shift.
- **P2 (the bound is informative).** Spearman(L, observed) ≥ 0.8 over the 44 pairs.
- **P3 (tightness).** The median of (observed − L) is ≤ 0.25. The bound is not vacuous.

**If P1 to P3 hold,** certifiability is predictable from the world and an error bound, before any monitor is run:
the prospective counterpart of the support audit, for monitors.
