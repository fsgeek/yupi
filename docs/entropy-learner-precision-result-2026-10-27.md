# Entropy observers at learner precision: result (2026-10-27)

> Declared in `entropy-learner-precision-declared-2026-10-27.md` (stamped b27de93 before running). Script
> `scripts/entropy_learner_precision.py`; per-learner numbers in `entropy-learner-precision-2026-10-27.json`.

**All three predictions held, 22 of 22 learners.**

| | range over 22 learners | same score on the true laws |
|---|---|---|
| S1, one-step entropy | 0.848–0.922 | 0.878–0.905 |
| S2, joint two-step entropy | 0.441–0.597 | 0.453–0.529 |
| S3, per-step profile H(K7) − H(K8\|K7) | 0.907–0.948 | 0.915–0.948 |

- **L1 (22/22).** Learners' one-step entropy ranks within 0.03 of the true laws' entropy.
- **L2 (22/22).** The profile beats one step in every learner. The resolve-vs-persist signature survives learner
  error. The smallest margin is the d256 lr 1e-4 ladder learner (0.907 against 0.904).
- **L3 (22/22).** The joint entropy cancels in learners as it does exactly.

## What it says

- In this world, the exported scalar behaves like a coarse but robust summary. Learners reproduce what entropy
  carries, nearly exactly.
- The summary is only as good as its shape: one number per step and kept apart, not summed. Summed over the horizon,
  it is near chance.
- Not compared here: the full-distribution certifier. It is scored by certified share and balanced accuracy, not by
  AUC, so the numbers are not on one scale. Putting them on one scale (AUC of the nearest-law margin) is the next
  comparison.

## What it points to

Arm B on real models has a concrete, two-part question. Does first-token entropy separate fabrication from
determined-but-open answers? Does the per-step profile (resolve vs persist) separate them better than any single
step or any sum?
