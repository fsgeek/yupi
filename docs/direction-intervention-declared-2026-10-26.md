# Matched-error direction intervention: declared before running (2026-10-26)

> Owning instance. Codex 10-26's recommended next experiment: does benign error *direction* explain why certification
> exceeds the predictor? 22 models (12 cell models, 10 ladder learners), k = 6, one and two steps, q = 0.95, the same
> val-fitted B and prior-free certifier as `certified_bound.py`. Pure-truth test windows.

**Three outputs per pure window,** all at the model's real per-window error e = TV(P_c, q):
- **real:** the model's q.
- **adversarial:** P_c + α(P_W − P_c), where P_W is the nearest withheld law to P_c and α = min(1, e / TV(P_c, P_W)).
  This is a convex combination, so it lies in the simplex, at TV exactly α·TV(P_c, P_W) from P_c.
- **random:** P_c + α(R − P_c), with R ~ Dirichlet(1) over the same support dimension and α = min(1, e / TV(P_c, R)).
  The seed is fixed (20261026).

Each is certified with the same rule and B. Reported: the certified pure share of each arm.

## Predictions

- **I1 (direction matters).** Certified share real − adversarial ≥ 0.10 at two steps in at least 18 of 22 models.
- **I2 (real errors are not biased toward hidden state).** |real − random| ≤ 0.05 at two steps in at least 16 of 22
  models.
- **I3 (adversarial matches the worst-case predictor).** At two steps, the adversarial share is within 0.05 of the L3
  predictor for at least 16 of 22 models. The predictor assumes worst direction with real error sizes.

**Readings:**
- If I1 and I2 hold, the excess certification is identified as non-adversarial direction.
- If real < random clearly, learners *do* lean toward hidden state relative to chance. That would reverse F11's
  reading.
