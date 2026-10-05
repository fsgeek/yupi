# Why is the relay's gain V-shaped? Results v0.1 (2026-10-04)

> **Status: EXPLORATORY.** This applies `docs/relay-v-diagnosis-design-v0.1.md`, committed and OTS-stamped
> (e50204f) before the script first ran. Raw: `docs/relay-v-diagnosis-2026-10-04.json`. Script:
> `scripts/relay_v_diagnosis.py`, run once, unedited after its commit. The frozen relay_paired join was
> imported unchanged and all of its gates passed. ι4_r1 − ι4_r1R reproduces the Δι table exactly. Standard
> errors are clustered by r1 class (25,005 classes, 84,949 windows).

## Result under the pre-declared reading: MIXED. No candidate stands out.

Primary arm (5 epochs):

| model | ι4_r1 | ι4_r1R | n_relay | zero-set gap |
|---|---|---|---|---|
| A: Δι | slope +0.0163 (t 5.7) | (−slope) | | −13.0 se |
| M1 | **+0.0178 (t 6.4)** | −0.0025 (t −0.6) | | −9.3 se |
| M2 | | | +0.0020 (t 2.8) | −24.7 se |
| M3 | +0.0178 (t 6.3) | −0.0022 (t −0.5) | +0.0023 (t 3.1) | −9.0 se |

Each model also includes log2 class mass. In M1, b_r1 + b_r1R = +0.0154 (t 5.0). corr(ι4_r1, ι4_r1R) = 0.79, and
the VIFs are ≤ 2.6.

- **A (distance) does not stand out.** b_r1R is not negative at |t| ≥ 3, and the sum is far from zero.
- **B (long-range structure at either rung) does not stand out.** b_r1R is not positive.
- **C (explicitness) does not stand out.** n_relay reaches t 2.8 in M2. In M3 it reaches 3.1, but the ι4_r1 term
  stays strong there.

Secondary arm (15 epochs): no ι term reaches |t| 2 (ι4_r1 +0.0009, t 0.4; ι4_r1R +0.0043, t 1.4). n_relay
gives t 2.8–2.9. The gain is mostly uniform: intercept +0.0037 in the reference fit.

Per the design, **no confirmatory test is written from this.**

## What the numbers say, descriptively

1. **At 5 epochs the gain tracks how much long-range information the class had *without* the relay
   (ι4_r1), and is insensitive to where the relay leaves it (ι4_r1R).** This is what produces the V. Classes with
   Δι < 0 still have large ι4_r1 (the two ι's correlate at 0.79), so they gain too. The left arm is not the relay
   "pushing information back and helping anyway". It is the same ι4_r1 dependence seen from the other side.
2. **The exact accounting of the relayed trace does not index the relayed learner's difficulty.** If it did,
   b_r1R would be clearly negative. One reading, which this note did not pre-declare and therefore does not test:
   **the learner's long-range difficulty is a property of the underlying history (its binding structure),
   measured relay-free, and the relay grants a discount proportional to it.** R3 (r1ʀ's excess correlates with
   r1ʀ's own ι4) would then hold only through ι4_r1R's correlation with ι4_r1.
3. **The exact-zero set is the set of classes with no long-range information at all.** In all 8,166 of its
   windows, ι4_r1 = ι4_r1R = 0, against 9.6 % of windows overall (post-hoc check, the table below). The gain
   there is ≈ 0 (+0.0008 at 5 epochs, +0.00002 at 15). That fits point 1: **no long-range information, no
   gain.** The models' zero-set gaps (7–25 se) mean the dependence is not linear with a shared intercept. The
   gain jumps from ≈ 0 to ≈ 0.002–0.004 as soon as there is any long-range information, then grows roughly in
   proportion. (A draft of this note called the zero set "unexplained". The check below corrected that before
   commit.)

   Post-hoc descriptive check, primary arm, by decile of Δι (window means):

   | decile | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |
   |---|---|---|---|---|---|---|---|---|---|---|
   | Δι | −0.157 | −0.020 | −0.003 | +0.000 | +0.005 | +0.023 | +0.059 | +0.132 | +0.270 | +0.620 |
   | ι4_r1 | **0.382** | 0.126 | 0.039 | 0.003 | 0.043 | 0.132 | 0.224 | 0.359 | 0.466 | **0.793** |
   | ι4_r1R | 0.539 | 0.146 | 0.042 | 0.003 | 0.038 | 0.109 | 0.164 | 0.228 | 0.197 | 0.173 |
   | Δexcess | 0.0109 | 0.0033 | 0.0019 | 0.0007 | 0.0039 | 0.0023 | 0.0047 | 0.0082 | 0.0102 | 0.0153 |

   Both tails of the V are classes with large ι4_r1. The middle decile is the classes with almost no long-range
   information.
4. **At 15 epochs the class-dependent part is gone.** The relay leaves a small, roughly uniform gain
   (~0.003–0.004 bits per window), with a weak n_relay trend.

## Next, under the stop rule (new note, not this one)

Point 2 is testable on data that already exists, and is cleaner than anything run here. In the r1ʀ censuses
alone, regress the r1ʀ KIND excess on ι4_r1 and ι4_r1R jointly, with the bintest's controls. The reading in
point 2 predicts that ι4_r1 carries the effect and ι4_r1R does not. The same joint fit on the r1 censuses is the
control. That would be a design note, stamped first. It stays exploratory, because the idea came from these
numbers. A confirmatory version needs a fresh corpus pair or new seeds.

The same design should model the jump at ι4_r1 = 0 explicitly, with an indicator for any long-range information
next to the linear term, rather than letting a shared intercept absorb it.
