# D1 held-out test: long-lag information predicts learner excess — pre-registration v0.1 (2026-09-29)

> **Status: CONFIRMATORY, pre-registered.** Written and OTS-stamped by the instance of
> 2026-09-28/29 **before** any window census of the held-out runs below exists. The
> analysis was chosen on the ε = 1 censuses (`docs/implicit-info-bintest-k7-2026-09-29.json`,
> `docs/implicit-info-bintest-freqctl-k7-2026-09-29.json`), and is frozen here.

## Hypothesis

Within an interface cell, a small transformer's excess over the exact ceiling on the next
event KIND rises with the exact information about that KIND lying **more than four records
back** in the window (ι_kind,4, `docs/implicit-information-design-v0.1.md`). The effect holds
with the class's exact KIND entropy, the short-range part of the history information
(ι_kind,1 − ι_kind,4), and the class's log₂ law mass (a frequency control) held fixed.

## Frozen analysis

- Code: `scripts/implicit_info_bintest.py` at sha256 `c73fab6b…ad32dd7acfc` (last changed in
  commit 7b9c981), `--m-long 4`. The quantity tested is the coefficient β_long in the model
  `full_plus_log2_class_mass` (terms 1, ι_long, ι_short, H_kind, log₂ mass), OLS with HC1
  errors, one row per scored test window at k = 7.
- Census: `scripts/learner_window_census.py` (sha256 `8bbc3d88…d5bc0d8f9fad9ab0f140b260085`),
  k = 7, test split, all windows. ι tables: `yupi.implicit_info` (sha256 `0ebd04e3…2d0d87f86d55f00dfb90`),
  the KIND-target m = 1..6 caches produced for the committed lag raws.

## Held-out runs (never censused; excess raws exist, windows never analysed)

Primary, 21 runs: ε = ½, 2M windows, 5 epochs, d = 128 — r1 seeds 1–3, r2 seeds 1–6, r3
seeds 1–3, r4 seeds 1–6; and ε = 1, r2 seeds 4–6.
Secondary (reported, not scored): r0 ε = ½ seeds 1–3, where every window's KIND is the whole
record.

## Predictions

- **P1.** β_long > 0 with t ≥ 3 in **every** primary run. Falsified by any primary run with
  β_long ≤ 0. Any run with 0 < t < 3 is a partial failure, reported by count.
- **P2.** Pooled over the seeds of each primary cell (five cells), β_long > 0 with t ≥ 5.
- **P3 (distance, not history).** In each pooled primary cell, β_long > β_short.
- **P4 (magnitude, descriptive band).** Pooled β_long between 0.01 and 0.06 bits of excess per
  bit of long-lag information. The ε = 1 pooled values were 0.024–0.039.

## What a result means

If P1–P3 hold, the finding is that the learner's shortfall tracks how far back the relevant
information lies, not how much history information there is, or how rare the context is.
That goes into paper 1 §4 as a confirmed within-cell result, and the converged-ladder re-run
(readiness item 5) carries it as a stamped prediction at the new budget. If P1 fails in more
than two runs, or P3 fails, the ε = 1 result is reported as exploratory only, and D1 is
revised in skeleton v0.2.
