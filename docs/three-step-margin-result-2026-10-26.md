# Does asking more keep paying? Three-step margins: result (2026-10-26)

> Owning instance. Scores `three-step-margin-declared-2026-10-26.md` (stamped at b344ff6 before computing). Rows by
> `scripts/three_step_split.py` at k = 5 (hashes `three-step-rows-k5-sha256-2026-10-26.txt`; smoke: exact marginals on
> 87 classes). Analysis: `scripts/three_step_margin.py` (memory-bounded chunks). Raw: `three-step-margin-k5-2026-10-26.json`.

## The coin's median margin, one → two → three steps (floor 0)

| | ε = 1 | ε = ½ |
|---|---|---|
| r0 | 0.033 → 0.173 → 0.326 | 0.027 → 0.156 → 0.285 |
| r1 | 0.110 → 0.216 → 0.374 | 0.051 → 0.203 → 0.287 |
| r2 | 0.052 → 0.172 → 0.372 | 0.038 → 0.188 → 0.285 |
| r3, r4 | 0.052 → 0.166 → 0.363 | 0.038 → 0.160 → 0.236 |

Medians over all pure classes agree to within 0.015.

## Predictions

- **D0 (μ1 ≤ μ2 ≤ μ3 for every pure class): holds,** with no violations.
- **D1 (the coin's μ3/μ2 < μ2/μ1, r1–r4, both ε): holds** (ratios 1.42–2.18 against 1.96–4.97). **But only as a
  ratio.** In absolute TV, at ε = 1 the third step adds *more* than the second (+0.158 to +0.201 against +0.106 to
  +0.120). At ε = ½ it adds less (+0.076 to +0.096 against +0.122 to +0.152). "Diminishing returns" is true of ratios
  everywhere, and of absolute gains only at ε = ½.
- **D2 (μ3 ≥ μ2 + 0.03): holds** everywhere (+0.076 at least).
- **D3 (all-pure median μ3 > μ2): holds** everywhere.

## Reading

- **Asking more keeps paying in this world through three steps.** The third step's margin is 0.24–0.37, against
  0.16–0.22 at two steps and 0.04–0.11 at one (r1–r4).
- **At k = 5 the one-step margins are wider than at k = 6 or 7** (fewer, less rare classes in a shorter prefix). The
  depth comparison is within k = 5.
- **Whether a learner can use the third step depends on its error at three steps,** which has not been measured.
  Two-step error was about 3–5× one-step error (val, 10-23). If three-step error grows as fast again (about
  0.15–0.25 TV), it would roughly match the three-step margin's gain. The optimal depth would then be about two for
  these learners. That is a prediction for a learner-side test. Three-step enumeration is about 5× more tree per
  window, and it must be memory-sized before running.
