# Validation-calibrated challenge: result (2026-10-25)

> Owning instance. Scores `challenge-declared-2026-10-25.md` (stamped at dedf52e before running). Script:
> `scripts/challenge_score.py`. Raw: `challenge-2026-10-25.json`.
>
> Ten learners; 8,836 fresh paired test windows each (the 10-25 windows dropped). Thresholds were set on val to 0.95
> coverage and frozen; test coverage came out at 0.943–0.956. PA\* chose β = 2, c = ¼ for every learner. The grid
> {1/16, 1/8, ¼} with the earlier ½ shows the optimum is interior at ¼, which answers the boundary concern.

## Covered balanced accuracy on fresh test windows

| learner (val one-step mean TV) | NL1 | NL2 | PA\* |
|---|---|---|---|
| d128, 45 epochs (0.023) | 0.990 | 0.998 | 0.997 |
| d128, 5 epochs (0.026) | 0.990 | 0.994 | 0.994 |
| d256, 45 epochs (0.029) | 0.979 | 0.997 | 0.998 |
| d128, lr 3e-4 (0.030) | 0.983 | 0.994 | 0.992 |
| d256, 15 epochs (0.031) | 0.980 | 0.997 | 0.995 |
| d64, 15 epochs (0.033) | 0.976 | 0.992 | 0.993 |
| GRU 256×2 (0.040) | 0.956 | 0.991 | 0.993 |
| d64, 5 epochs (0.042) | 0.956 | 0.982 | 0.985 |
| d64, lr 3e-4 (0.061) | 0.915 | 0.968 | 0.978 |
| d256, lr 1e-4 (0.077) | 0.887 | 0.932 | 0.945 |

Conservative balanced accuracy (abstention counts as error): NL1 0.791–0.895, NL2 0.861–0.926, PA\* 0.882–0.938.

## Predictions

- **N1 (NL2 ≥ PA\* − 0.005 in ≥ 8 of 10): holds, 8 of 10.** PA\* − NL2 ranges from −0.002 to 0.013. The two
  exceptions are the two worst learners (0.010, 0.013).
- **N2 (NL1 within 0.01 of PA\* in ≤ 3 of 10): holds, exactly 3.** PA\* − NL1 ranges from 0.004 to 0.063.
- **N3 (NL2 > NL1 in all 10): holds.**

**Exploratory (not declared):** the second step's gain for the nearest-law monitor rises with learner error
(Spearman +0.88 against val one-step TV). It runs from about +0.004 to +0.008 for the best learners to +0.045 to
+0.053 for the two worst.

## What survives the reviewer's attack

With calibrated thresholds at matched coverage, in this world, at k = 6:
1. A plain nearest-law monitor with no prior is already good at one step (0.887–0.990).
2. A prior and a second step are near-substitutes: each lifts it, and together they add little more. Two steps
   without a prior match the best prior-aware monitor in 8 of 10 learners.
3. Their value grows as the learner gets worse. Gains are 0.004–0.063 over NL1, largest for the worst learners. This
   is now true for the calibrated nearest-law monitor too (exploratory), not only for the uncalibrated summed observer
   that F10 withdrew.

Still not shown: necessity (finding 2); anything outside this oracle-assisted family (finding 5); other cells or
worlds.
