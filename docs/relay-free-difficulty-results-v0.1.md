# Is the learner's long-range difficulty a property of the relay-free history? Results v0.1 (2026-10-04)

> **2026-10-04 CORRECTIONS, read first.** An adversarial review (Claude, independent code, CR1 verified against
> statsmodels; key numbers re-derived by the owner before adoption) found no code errors and confirms that the
> pre-declared rule was applied correctly: H-free "stands out" *under model F*. The interpretation does not survive:
> - **The H-free separation is specification-fragile.** Adding fixed effects for the kind of the last prefix record,
>   a trivial observable class property, gives at r1ʀ 5 epochs ι4_r1 +0.0062 (t 1.2) and ι4_r1R +0.0097 (t 1.6).
>   Neither reaches t 2. Alone, each regressor is strongly significant (t 6.8, 5.4). At a correlation of 0.79 the
>   data cannot say which of the two indexes the learner. **Point 1 below is withdrawn as a suggestion: H-free vs
>   H-acct is unresolved.**
> - **"Speed-up, not relocation" and "no lasting advantage" are withdrawn.** About 60 % of the paired gain
>   remains at 15 epochs (+0.0041 off the zero set), and in the paired fit the step-shaped advantage persists
>   (indicator +0.0039, t 5.9). The per-bit *slope* converges; the step does not. "Relocation" was never tested.
> - **The step marks a class type, not an amount of information.** Binned against ι4 = 0, classes with ι4_r1 in
>   (0, 0.001] bits already cost +0.022 bits (t 8.0). Less than a millibit of information cannot cost 20 millibits,
>   so the magnitude of ι4 is not the operative quantity at the low end. About half the step is absorbed by
>   last-kind fixed effects (0.0157 → 0.0088), but it survives (t 4.5–6.8).
> - **The cost profile (r1, 5 epochs, bins vs ι4_r1 = 0):** +0.022 (0–0.001 bits], +0.018, +0.015, +0.017, +0.020,
> +0.024 (0.2–0.4], +0.030 (0.4–0.6], +0.049 (> 0.6), every bin t ≥ 8. The same shape holds in all four fits. It is a
>   **plateau with a rise at the top**, not a line through the origin.
> What survives: no long-range information, no gain (both arms); a relay gain concentrated in classes with any
> long-range dependence, persisting at convergence in step form; and a learner cost that behaves more like the
> *presence* of long-range dependence than like its quantity in bits.

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
