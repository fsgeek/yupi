# Three-arm prereg v0.1: blocked before stamp (2026-10-05)

> **Status: RECORD.** Owner: the instance of 2026-10-05. `docs/three-arm-prereg-v0.1.md` and
> `scripts/three_arm_score.py` were reviewed before stamping by a Claude reviewer and a Codex (GPT) reviewer.
> Both said "do not stamp". No three-arm model has been trained.

## Blocking findings (both reviewers; adopted after the owner re-derived the core numbers)

1. **Between-model variance dominates, and the inference ignored it.** The windows-as-units errors (HC1 or CR1 by
   class) on seed-mean differences treat about 85k windows as independent and never count the 3-vs-3 draw of
   models. On the 10-02 relay models at 5 epochs, re-derived from `review-2026-10-04/arrays.npz`:
   - r1 seed means are 0.0244, 0.0244 and 0.0152;
   - two r1 seeds, with no field difference at all, differ by 0.009, which is larger than the relay effect;
   - across the 9 r1 × r1R pairings, the mean gain runs from −0.002 to +0.011 and the |Δι| slope from 0.002 to
     0.045. Codex: the seed-based se of the mean slope is 0.011, against a CR1 se of 0.003.
2. **The severity simulation cannot produce this noise.** Class-level sign flips average a model offset away. So
   the power and severity in `three-arm-severity-2026-10-05.json` condition on the trained models and are
   **not valid** for a new draw of models. "Conservative" was wrong: noise from a shared r1 baseline can push the
   ratio either way.
3. **The scorer's reading logic was unsafe:**
   - no override when P_V fails, so a failed replication still produced a mechanism verdict;
   - no protection against a sign flip or a small denominator in slope_D / slope_R;
   - P_null used failure to reject as evidence of equivalence. A planted field effect of 0.0003 read as H_bind
     93 % of the time (Codex).
4. **The scorer's gates were too weak.** Codex got a scored `H_move` from inputs that all declared the wrong rung,
   ε, budget and seed.

Should-fix items, also adopted:
- the H_field rival's size;
- arm-specific noise and tail leverage (the top 1 % of windows carries 36–52 % of |Δι| variance);
- HC1 was dropped without saying so;
- calling the post-hoc |Δι| refit "the V".

## What the owner checked next: offset-cancelling contrasts

Per model, the gain on a class set minus the gain on the set where both arms move nothing (S0, 9.6 % of windows):

| | contrast on relay-only set (4.2 %) | on decoy-only set (**0.4 %**) | on both-move set (16.4 %) |
|---|---|---|---|
| 5 ep, r1R seeds vs r1 mean | 0.0156, 0.0185, 0.0155 | 0.0055, 0.0043, 0.0055 | 0.0075, 0.0096, 0.0090 |
| 5 ep, **null**: an r1 seed vs the other two | −0.0137, −0.0096, +0.0233 | −0.0154, +0.0119, +0.0035 | −0.0036, −0.0099, +0.0135 |
| 15 ep, r1R seeds vs r1 mean | 0.0055, 0.0106, 0.0066 | 0.0060, 0.0080, −0.0138 | 0.0079, 0.0092, 0.0018 |
| 15 ep, **null** | +0.0073, −0.0093, +0.0020 | +0.0035, +0.0001, −0.0036 | +0.0002, +0.0025, −0.0026 |

The null contrasts are as large as the effects. The r1R rows agree with each other partly because they share one
r1 baseline. The decoy-only set is too small to carry a test.

## What this means

- **For the three-arm test:** with 3 seeds per arm it cannot be informative at either budget. A rough calculation
  from the null spread: model sd per contrast is about 0.012 at 5 epochs and about 0.007 at 15. A test with useful
  power needs roughly 12 or more seeds per arm at 5 epochs (48+ runs, about 5 GPU hours at 4 parallel), or a
  stronger lever. The redesign (v0.2) must:
  - use the model as the unit, as model-level contrasts;
  - test equivalence with a stated margin;
  - gate mechanism readings on the relay replicating;
  - validate manifests and recipes;
  - simulate severity by resampling model deviations, not windows.
- **For the 10-02 relay verdict:** its *qualitative* conclusions survive per pairing. Measured against the zero
  set of the same pairing, the V's arms are positive in 8/9 (5 ep) and 9/9 (15 ep) pairings, and R4's wrong sign
  holds in 9/9 and 8/9. Its stated t-values reflect window-level precision only. A CORRECTIONS note on that
  verdict is owed.
- **For every paired or seed-mean analysis since 09-30:** the same caution applies, including the plateau fits,
  the V diagnosis and the count comparison's transformer side. Seed spread at 5 epochs is the first thing to
  check.

## Addendum (same day): seed matching, and why 5 epochs is the wrong budget

On the 10-02 relay models, per pairing (r1 seed i vs r1R seed j), the window-level correlation of excess is
0.52–0.62 for **matched** seeds (i = j) and 0.35–0.46 for unmatched. Seed-matched pairs share a random component,
so a v0.2 design should pair arms by seed.

At **5 epochs**, every pairing against r1 seed 2 shows no relay gain, matched or not. Mean gains are −0.002 to
+0.002, and the |Δι| > 0.1 minus zero-set contrast is −0.002 to +0.002. Against seeds 0 and 1 the gains are
0.007–0.011. Seed 2's excess (0.0152) is already at the relay models' level. The likeliest reading is that at 5
epochs the learners are in a mixed phase: some seeds have acquired the long-range structure the relay supplies, and
some have not. Between-seed variance there is mostly *which phase a seed is in*. This is a reading, not a test.

At **15 epochs**, all 9 pairings are positive: mean gain 0.0017–0.0063, contrast 0.0028–0.0091.

**Consequence for v0.2:** the confirmatory budget is 15 epochs, with seed-matched pairs, and 5 epochs is at most
descriptive. This reverses v0.1's choice, which was made on window-level power. A rough calculation: the contrast
has a per-pairing sd of about 0.0025 against a mean of about 0.006, so about 8 seeds per arm gives a t of about 5.
That is 32 runs at 15 epochs, about 6.5 GPU hours in all. Per Tony's guidance, it runs as short, staggered leases
of one or two waves (about 50–100 min each), with gaps between them, and never close to the single-lease cap.
