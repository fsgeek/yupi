# The three-arm intervention: design v0.2 (2026-10-05)

> **Status: DESIGN.** It supersedes v0.1 §5–§7. v0.1 §1–§4 stand: the question, the rungs, the code and the exact
> side, which is done with gates passed (9fd95d8). The fresh paired corpus, run 0582ffbeb4693d27, is built and its
> four pairing gates pass (3a19419). Why v0.2: `docs/three-arm-prereg-review-2026-10-05.md` and its addendum. Prereg
> v0.1's inference ignored between-model variance. At 5 epochs that variance is dominated by which training phase a
> seed is in. Seed-matched pairs share variance. Written by the instance of 2026-10-05.

## 1. Unit, budget, seeds

- **The unit is the seed.** A seed s is trained on all four rungs (r1, r1R, r1D, r1S) with the same `--seed`. That
  gives the same initialization and data order, and the four corpora differ only in the OBJECT slot.
- **Budget:** 15 epochs, d = 128, lr 1e-3. That is the converged recipe; 5 epochs is not used.
- **Seeds:** n from the power analysis in §4, provisionally 8, giving 32 runs.

## 2. The matched control is the self-copy, not r1

The self-copy field moves zero information and has the same field count, token budget and format as the relay and
the decoy. For an arm A ∈ {R, D} and seed s, with y the realized KIND excess per test window:

  D_A,s(w) = y_S,s(w) − y_A,s(w)        (positive: arm A beats the self-copy on window w)

Then:
- the field-count effect cancels, because both arms have the field;
- the model-level offset cancels to the extent the seed-matched pair shares it;
- the r1 baseline does not enter at all.

The primary statistic per seed is an **offset-cancelling contrast over class sets fixed by the exact side**:

  K_A,s = mean of D_A,s over windows with |Δι_A| > τ   −   mean of D_A,s over windows with Δι_A = 0 exactly

Δι_A = 0 is decided on the exact Fraction mixtures. The difference of the two set means removes any offset that
survives. The two sets differ in class type, but the self-copy model sees the same windows, so a difficulty
difference that any field-bearing model would show appears in both y_S and y_A. τ = 0.1 bits unless §4 says
otherwise. Per-bit form: k_A,s = K_A,s / (mean |Δι_A| on the moved set).

## 3. Readings and tests (model-level, across seeds)

- **Gate, P_V (the relay replicates):** mean_s K_R,s > 0, one-sample t across seeds ≥ 3. If it fails, no mechanism
  reading is made.
- **H_move vs H_bind, on per-bit effects:** ρ = mean_s k_D,s / mean_s k_R,s, with a seed-bootstrap (resampling
  seeds, 10,000 draws) 90 % interval.
  - H_move: the interval excludes 0 and includes 1, or lies within [0.5, 2].
  - H_bind: K_D is equivalent to 0 by TOST at a margin ±m stated in the prereg, sized as a fraction of the relay's
    K_R, and the interval for ρ lies below 0.25.
  - Anything else is unresolved, with no forced reading.
- **H_field (secondary):** mean_s (y_r1,s − y_S,s) over all windows, as a seed-level t-test, with equivalence at
  ±0.001 bits by TOST. This is now separate from the mechanism question, because the self-copy control has removed
  the field from every comparison above.
- **Reported:** every seed's K and k values, the per-seed table, the 5-epoch numbers if they are ever run (they are
  not planned), and r1-baseline versions of the V for continuity with the relay verdict.

## 4. Power and severity, before the prereg

Resample models, not windows. Templates are the 10-02 15-epoch models: 3 seed-matched (r1, r1R) pairs. Their
per-seed deviation vectors give the between-model sd of K. With only 3 templates the sd is uncertain, so the power
calculation uses the upper end of an 80 % interval for it. n is the smallest seed count giving power ≥ 0.8 for P_V
and severity ≥ 0.8 for each mechanism reading against its rival. Rivals are planted at:
- ρ = 1 (H_move);
- ρ = 0 (H_bind);
- ρ = 0.4 (intermediate, which must come out unresolved, not mislabelled).

If n > 10, the design is reconsidered before anything trains. Options: a stronger lever, or class sets with more
mass.

## 5. Scorer requirements (both reviewers' gates)

The scorer must:
- validate each census's manifest rung, ε, corpus run, seed, step, d, lr and epochs against the prereg table, and
  refuse any mismatch or duplicate;
- check identical window sets, with each class key recomputed from the r1 corpus;
- take Δι from sha-gated caches, and recompute the self-copy's Δι = 0 set from the exact mixtures;
- gate every mechanism reading on P_V, with no ratio ever computed on a non-positive relay effect;
- carry tests for: mislabelled inputs (refused), a failed P_V (no mechanism reading), sign flips, a tiny
  denominator, an intermediate ρ (unresolved), and planted H_move, H_bind and H_field.

## 6. GPU footprint (per Tony, 2026-10-05: the card is the ayllu's)

32 fifteen-epoch runs take about 49 min each, four at a time, so about 6.5 h in all. Schedule:
- leases of one wave of four runs, about 50–55 min, with an honest `--expected-until`;
- at least an hour between leases, so the qwen door can wake;
- seed by seed, so every completed lease leaves complete matched quadruples;
- `--ckpt-every` and `--resume` throughout.

Never more than one lease at a time. Nothing trains until the prereg is stamped after its pre-stamp review.
