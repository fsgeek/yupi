# Entropy observers at learner precision: declared before computing (2026-10-27)

> Follows `entropy-only-observer-result-2026-10-27.md`. That result was exact (no learner). This test asks whether
> its two findings survive learner error: one-step entropy separates fairly well, and the per-step entropy profile
> (high now, low next) separates better while joint entropy cancels.

## Population

- Learners: every `*-test.npz` in `~/.cache/yupi-scratch/learner-two-step-2026-10-23/` (12 cell models, r1/r3 ×
  ε ∈ {1, ½}) and `learner-quality-2026-10-25/` (ladder). Fields `q1` (8 KINDs) and `q2` (8 × 8 joint, index
  a·8 + b).
- Truth: the label and the true laws of each window's class from the k = 6 two-step rows, via
  `learner_two_step_score.family`. Windows labelled pure or withheld (G ≥ 0.1) only. Unweighted, since windows are
  sampled from the world.

## Observers (scores; AUC for withheld vs pure)

- **S1** = H(q1): one-step entropy.
- **S2** = H(q2): joint two-step entropy.
- **S3** = H(m) − (H(q2) − H(m)), where m is q2's marginal on the first KIND: the per-step profile difference.
- Each is also computed on the true laws for the same windows (S1*, S2*, S3*).

## Predictions (n = number of learners)

- **L1.** |AUC(S1) − AUC(S1*)| ≤ 0.03 in at least 90 % of learners. A scalar is robust to learner error.
- **L2.** AUC(S3) > AUC(S1) in at least 90 % of learners. The resolve-vs-persist signature survives learner error.
- **L3.** AUC(S1) − AUC(S2) ≥ 0.15 in at least 90 % of learners. Joint entropy cancels in learners too.

## What each outcome points to

- If L2 fails, the profile signature is too fine for learners to reproduce. Arm B should then not lean on entropy
  trajectories.
- If L1 fails, learner error moves entropy in a class-dependent way. That links to the class-dependent precision in
  F11.
