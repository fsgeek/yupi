# Learner-side two-step test: settings frozen, predictions declared before test (2026-10-23)

> Owning instance. Follows design v2 (`learner-two-step-design-2026-10-23.md`) and its Codex review. Val was used only
> for cost, η and τ. No monitor was scored on val.

## Frozen settings

- **Enumeration:** PRUNE = 1e-4, FLOOR = 1e-5, WINDOW_CHUNK = 25.
- **Test:** 10,000 eligible test windows per model, seed 20261023, the same indices for every method.
- **τ1, τ2:** fitted on val by `scripts/learner_two_step_score.py`, as the mean TV to the true law.
- **Monitors and rules** exactly as in the scorer's docstring.
- **Memory:** each process capped at MemoryMax = 4G.

## Val calibration (2,000 windows per model, 0 unmatched)

| | median model TV, one step | median model TV, two steps | η > 0.0025 | η > 0.01 |
|---|---|---|---|---|
| r1 (ε = 1; ε = ½) | 0.009–0.018; 0.009–0.013 | 0.041–0.046; 0.048–0.054 | 0 | 0 |
| r3 (ε = 1; ε = ½) | 0.006–0.010; 0.012–0.018 | 0.037–0.043; 0.043–0.049 | 20–27 % | 3–6 % |

The models' two-step error is 3–5 times their one-step error, about as much as the exact margin grows (coin margins at
k = 6: one-step 0.023–0.075, two-step 0.134–0.192). The coin's margin divided by the sufficient threshold
2·(median error) + 0.005, one step → two steps:

| cell | ratio |
|---|---|
| r1, ε = 1 | 1.5 → 1.9 |
| r1, ε = ½ | 0.84 → 1.6 |
| r3, ε = 1 | 3.7 → 2.3 |
| r3, ε = ½ | 0.81 → 1.4 |

## Predictions (test; every seed of the named cell)

- **L1.** The share of pure windows meeting the sufficient condition is higher at two steps than at one step in
  r1 ε = ½, r3 ε = ½ and r1 ε = 1, and **lower** in r3 ε = 1.
- **L2.** The mass-blind monitor's conservative balanced accuracy is higher at two steps than at one step in both
  ε = ½ cells.
- **L3.** The prior-aware monitor's conservative balanced accuracy at two steps is within 0.02 of one step in every
  cell. The prior already does the work that the second step would do.
- **L4 (stability).** The test median two-step TV is within ±20 % of the val median for every model.

**Meaning.** If L1 and L2 hold, the query lever is usable by these learners exactly where the one-step margin is
narrow, and costs them where it is already wide. That is because the learners' error compounds over the second step
about as fast as the exact margin widens. If L1 fails at r3 ε = 1 (two steps help there too), the error-compounding
account is wrong.
