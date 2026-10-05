# Is the learner's long-range difficulty a property of the relay-free history? Results v0.1 (2026-10-04)

> **Status: EXPLORATORY, suggested by the data.** This applies `docs/relay-free-difficulty-design-v0.1.md`,
> committed and OTS-stamped (e86759c) before the script first ran. The script `scripts/relay_free_difficulty.py`
> ran once and was not edited after its commit. The relay_paired gates passed. Raw:
> `docs/relay-free-difficulty-2026-10-04.json`, log beside it. The question came from the V diagnosis's numbers,
> so **this cannot be confirmatory.** A confirmatory version needs new seeds or a fresh corpus pair.

## Result under the pre-declared reading: H-free stands out

Model F, CR1 errors clustered by r1 class, response = seed-mean KIND excess, n = 84,949:

| fit | ι4_r1 (relay-free) | ι4_r1R (relayed) | 1[ι4_r1 > 0] |
|---|---|---|---|
| r1, 5 epochs (control) | +0.0335 (t 6.1) | −0.0039 (t −0.6) | +0.0157 (t 11.9) |
| **r1ʀ, 5 epochs (read)** | **+0.0167 (t 3.6)** | **+0.0003 (t 0.0)** | +0.0129 (t 12.4) |
| r1, 15 epochs | +0.0141 (t 3.3) | −0.0006 (t −0.1) | +0.0118 (t 11.8) |
| r1ʀ, 15 epochs | +0.0146 (t 3.7) | −0.0044 (t −1.0) | +0.0079 (t 9.1) |

The model also controls both rungs' short-range parts, the exact KIND entropy and log2 class mass. Without the
indicator, the pattern is the same (r1ʀ 5 epochs: ι4_r1 t 4.6, ι4_r1R t −0.2).

The reading's conditions hold. At r1ʀ, ι4_r1 > 0 with t ≥ 3, and ι4_r1R has t < 2. The r1 control does not show
ι4_r1R > 0. The 15-epoch fits agree in sign.

## What this suggests (not shown, given its status)

1. **The relayed learner's long-range difficulty is indexed by the relay-free history, not by the exact
   accounting of what it is shown.** The relay leaves the exact quantity of the learner's own trace (ι4_r1R) with
   no detectable weight.
2. **The relay acts as a speed-up, not a relocation.** At 5 epochs it halves the per-bit cost of relay-free
   long-range information (0.0335 → 0.0167). At 15 epochs the r1 learner, with no relay, has reached the same cost
   (0.0141 against 0.0146). That is why the paired slope is 0 at 15 epochs, and why the gain at 5 epochs tracked
   ι4_r1 (`docs/relay-v-diagnosis-results-v0.1.md`).
3. **Much of the long-range cost is a step, not a slope.** Classes with *any* information beyond lag 4 cost
   0.008–0.016 bits more per window, independent of how much (t 9–12 in every fit), on top of the per-bit term.
   Long-range dependence costs the learner as a structural property of the history. Its exact magnitude adds
   less.

Read together with the two verdicts of 2026-10-02: exact long-lag information measured on the relay-free
history predicts the learner's difficulty within cells. Showing the binding fact explicitly makes that difficulty
faster to overcome, but by convergence it gives no lasting advantage. Nothing here identifies the mechanism.
"The learner must assemble binding history across records" is consistent with all of it and has not been tested.

## Caveats

- The test was suggested by the data and the same windows were reused.
- ι4_r1 and ι4_r1R correlate at 0.79, so the separation rests on t ≈ 3.6 at the read cell.
- Three seeds per rung-arm, averaged.
- One interface (r1, ε = 1).
- The step term's size depends on the model (it absorbs part of the intercept). Its sign and significance do
  not.
