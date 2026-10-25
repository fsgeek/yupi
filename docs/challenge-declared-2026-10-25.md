# Validation-calibrated challenge: nearest-law vs prior-aware monitors, declared before running (2026-10-25)

> Owning instance. The falsification experiment proposed by the Codex read (`story-codex-review-2026-10-25.md`).
> Same ten ladder learners (r1, ε = 1, k = 6). No retraining.

**Monitors** (all see only the model's output and the exact family):
- **NL1 / NL2:** nearest-law, one and two steps. Score s = d_withheld − d_pure; pure if s ≥ t_pure, withheld if
  s ≤ −t_withheld, else abstain. η is ignored here; it is reported.
- **PA\*:** the best prior-aware monitor over β ∈ {1, 2} and c ∈ {1/16, 1/8, ¼}, one step. The extension below ¼
  answers the reviewer's point about boundary optima. Score π_pure; pure if π ≥ t, withheld if π ≤ 1 − t.

**Calibration on val only** (the existing 2,000-window val dumps):
- For each monitor and learner, choose a symmetric threshold so that val coverage of the headline population is
  0.95.
- For PA\*, choose (β, c) by val conservative balanced accuracy at that coverage.
- Freeze everything.

**Fresh test:**
- A new sample of 10,000 eligible test windows per learner, drawn with seed 20261025.
- Windows already used on 10-25 are dropped, leaving about 8,800, paired across monitors.
- **Metric:** covered balanced accuracy at the frozen thresholds, plus test coverage and conservative balanced
  accuracy.

## Predictions

- **N1.** NL2 ≥ PA\* − 0.005 (covered balanced) in at least 8 of 10 learners. A second step can replace the prior.
- **N2.** NL1 is within 0.01 of PA\* in at most 3 of 10 learners. At one step, the prior adds something for most
  learners.
- **N3.** NL2 > NL1 in all 10 learners.

**What would defeat what:**
- If N2 fails (NL1 within 0.01 of PA\* in most learners), neither the prior nor the second step is needed at k = 6
  with a well-calibrated nearest-law monitor. The certification story then reduces to *the observer's calibration*,
  with the k = 7 rare-neighbour trap as its main exhibit.
- If N1 fails, the prior does carry information that the second step does not.
