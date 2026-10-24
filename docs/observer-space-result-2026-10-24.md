# The observer's design space: result (2026-10-24)

> Owning instance. Scores `observer-space-declared-2026-10-24.md`. Script: `scripts/observer_space.py`. Raw:
> `observer-space-40-8-2-k6-2026-10-24.json`. 12 models × 10,000 test windows at k = 6; 32 observers each; the metric is
> conservative balanced accuracy.

## Predictions

- **O1 holds as declared, but the declared form overstates it.** Observer range ÷ learner (seed) range is 11.4
  (r1 ε = 1), 14.0 (r1 ε = ½), 36.9 (r3 ε = 1) and 10.7 (r3 ε = ½). The grid includes deliberately poor observers (c = 2,
  β = 0) that sit at chance (≈ 0.50). Restricted to reasonable observers (β ≥ ½, c ≤ ½; 12 per model; **post hoc**),
  the ratio is 2.6, 5.4, 5.9 and 3.1. The observer still moves the verdict more than the seed does, by about 3–6×, not
  10–37×. One cell falls below the declared 3×.
- **O2 fails in one cell.** At two steps with the best c, ignoring the prior costs 0.009 / 0.003 / −0.009 (r1 ε = 1),
  0.015 ×3 (r1 ε = ½), 0.008 / 0.011 / 0.024 (r3 ε = 1), but 0.029 / 0.060 / 0.040 at r3 ε = ½. Asking more substitutes
  for the prior almost everywhere, but not fully at r3 ε = ½.
- **O3 fails if read strictly; holds on cell means.** At one step with the best c, ignoring the prior costs, per seed:
  0.148 / 0.033 / 0.023 (r1 ε = 1), 0.262 / 0.168 / 0.448 (r1 ε = ½), 0.053 / 0.047 / 0.052 (r3 ε = 1), and
  0.277 / 0.399 / 0.249 (r3 ε = ½). Every seed is ≥ 0.05 in 2 of 4 cells, and the cell mean is ≥ 0.05 in 4 of 4. The
  declaration did not say which reading it meant. The strict reading, the one that does not favour the prediction, is
  the verdict: **fails.**
- **O4 holds.** The best c is ¼ for 23 of 24 (model, query) pairs, and ½ for one. The declared τ = mean error is too
  broad everywhere. ¼ is the grid's edge, so the true optimum may be lower.

## What the grid shows beyond the predictions

- **The best observer overall is one-step, sharp noise (c = ¼), and *over*-trusting the prior (β = 2),** for 10 of 12
  models: 0.949–0.984. With a good prior and a good noise model, one step is enough. The second step's value is for
  observers *without* a prior. At β = 0 with the best c, two steps give 0.872–0.966, against 0.517–0.953 for one step.
- **The noise model matters as much as the prior.** One step at the declared scale (c = 1, β = 1) gave 0.862–0.961
  (the 10-23 result). At c = ¼, the same observer gives 0.916–0.975.
- **Over-trusting the prior (β = 2) and sharpening the noise (c = ¼) both help.** A plausible reading, not checked: the
  learners' errors are heavy-tailed (most windows near exact, a few far off), so a mean-matched exponential kernel is
  too flat for the typical window.

## Status of the ledger's story hypothesis

Partly supported. Within a fixed learner quality, reasonable observer choices (prior use, query depth, noise scale)
move the verdict 3–6 times more than the training seed does, and the best observer is not the one the declarations
assumed. Untested, and the decisive next step: learners of genuinely different *quality* (e.g. under-trained
checkpoints, smaller widths, the GRU baselines). Only that comparison says whether "the observer decides" survives
when the learner differences are real rather than seed noise.
