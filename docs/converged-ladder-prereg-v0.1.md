# The converged-budget ladder: pre-registration v0.1 (2026-09-30)

> **Status: CONFIRMATORY, pre-registered.** Stamped by the owner (instance of 2026-09-28/29/30)
> while the models are training and **before any of them is evaluated**. The training launcher
> (`~/.cache/yupi-scratch/runs/ladder15/train_2026-09-30.sh`) trains only, and evaluation and
> census start after this file's stamp. Paper-1 readiness item 5 and the second test owed by
> `docs/d1-long-lag-verdict-v0.1.md`.

## Models

d = 128, 15 epochs (the converged budget, note §23.1), lr 1e-3 → 1e-4, 2M-window corpora of the
ten-cell sweep (§10), seeds 1–3 per cell. The r1 ε = 1 cell uses the existing 15-epoch seeds
1–3 (note §22.1/§23, evaluated before this file, so that cell is **excluded from C3's ordering
test**, which uses cells evaluated only after the stamp). Everything else is new: 27 runs.

## Frozen analyses

- Evaluation: `scripts/learner_evaluate.py`, k = 1..7, test split. Census:
  `scripts/learner_window_census.py`, k = 7. The D1 analysis: `scripts/implicit_info_bintest.py`
  at sha256 `c73fab6b…ad32dd7acfc`, `--m-long 4`, model `full_plus_log2_class_mass`.
- The KIND-excess cell mean is the census's mean of `by_field.kind` (the realized estimator of
  KIND KL) over the k = 7 test windows. The between-seed spread is reported with it.

## Predictions

- **C1 (D1 holds at the converged budget).** β_long > 0 with t ≥ 3 in every r1–r4 run (24 runs:
  21 new and the 3 existing r1 ε = 1 15-epoch seeds, whose censuses are also new).
- **C2 (magnitude).** Pooled β_long per r1–r4 cell lies in [0.01, 0.05] bits per bit. The
  5-epoch values were 0.029–0.041. The prediction is that convergence shrinks the long-lag cost
  no more than the overall excess shrinks, and does not remove it.
- **C3 (the cross-cell ordering follows exact long-lag information).** Among r1, r2 and r3 at
  ε = ½, the mean KIND excess ranks as ι_kind,4 ranks (`implicit-info-lag-kind-40-8-2-k7-2026-09-28.json`:
  r2 0.361 > r1 0.338 > r3 0.305), so **r2 > r1 > r3**. At ε = 1 (r1 excluded, see above):
  **r2 > r3** (ι_kind,4 0.282 against 0.259). A cell ordering counts as seed-resolved only if
  every seed of the higher cell exceeds every seed of the lower one. The mean ordering is the
  prediction, and resolution is reported beside it.
- **C4 (control).** r0 has the lowest KIND excess of every cell at its ε. That is the rung with no
  entities to carry (secondary result of the D1 verdict).

## What a result means

C1 and C2 passing make the long-lag cost a property of the converged learner, not of
under-training. C3 is the stronger claim: an ordering of a trained model's shortfall across
interfaces, predicted before evaluation from exact-side quantities alone. If C3 fails while C1
holds, the within-cell law does not scale to the between-cell comparison, and paper 1 reports it
within cells only. r4 is outside C3 because its seeds split into basins (§14–§15). Its cell
mean is reported, with no prediction.
