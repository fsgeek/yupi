# Worst-case certification with an error bound the observer can know: declared before running (2026-10-25)

> Owning instance. Tests the restored worst-case claim (`story-codex-review-2026-10-25.md`, owner's audit). The
> observer has no prior and does not know a window's true error. It knows only an error bound B fitted on val. Ten
> ladder learners, r1 ε = 1, k = 6. Val dumps for calibration, the fresh paired test windows (challenge run) for
> scoring.

**Bound:** B_s(q) = the q-quantile, over each learner's val windows, of TV(true law, output), separately for one
step (s = 1) and two steps (s = 2), with q ∈ {0.90, 0.95, 0.99}.

**Certifier (no prior):**
- Certify "pure" for a window iff some pure law is within B of the output *and* every withheld (G ≥ 0.1) law is
  farther than B.
- Certify "withheld" symmetrically.
- Otherwise, do not certify.
- If the true error is ≤ B, a certificate cannot be wrong: the true law is within B, and the other kind is not. So the
  false-certificate rate is bounded by the share of windows whose error exceeds B, which is about 1 − q if val and
  test errors match.
  *Correction 10-26 (Codex): that bounds the unconditional wrong-certificate rate; among certified windows the bound is
  P(e > B) / coverage. B2's numbers stand as an empirical observation, not as the stated guarantee.*

**Reported per learner, s and q:**
- certified share of pure windows (the coverage that matters);
- certified share of withheld windows;
- false-certificate rate among certified windows;
- the test share of windows with error > B, as a check on the bound.

## Predictions

- **B1.** At q = 0.95, the two-step certified share of pure windows exceeds the one-step share for at least 8 of 10
  learners.
- **B2.** At every q and s, the false-certificate rate is ≤ (1 − q) + 0.01 for at least 9 of 10 learners. The bound
  transfers from val to test.
- **B3.** At q = 0.95 and one step, the certified share of pure windows is below 0.5 for the four worst learners (val
  one-step mean TV ≥ 0.040).
- **B4.** The certified pure share falls as q rises (a looser bound, fewer certificates), at both s, for every
  learner. This is a check.

**What this would establish:** how much worst-case certification is actually available to an observer without a
prior, at a stated risk, and how much a second question buys. That is the auditor's version of the question, and the
one PACMI points to.
