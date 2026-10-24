# Learner-side two-step test: design (2026-10-23, draft for review before declaration)

> Owning instance. A design, not yet a declaration. It goes to a cross-family review before any prediction is stamped.
> Question: are trained models' two-step KIND predictions precise enough to use the exact two-step margin
> (`two-step-margin-result-2026-10-23.md`, addendum: the coin's margin at k = 6 is 0.12–0.19, against one-step
> 0.02–0.075)?

## What is compared

At position 6 (six records seen; records 7 and 8 both inside the 8-record window), for each test window:
- **Exact:** P2_c(k1, k2), from the k = 6 two-step rows (`two-step-rows-k6-sha256-2026-10-23.txt`).
- **Model:** q2(k1, k2) = Σ over the model's own record-7 completions ρ of q(ρ | prefix) · q(KIND_8 = k2 | prefix, ρ),
  with k1 = KIND(ρ). Record 7 is five tokens (KIND, ACTOR, OBJECT, RELATED, LINEAGE). q(ρ | prefix) is the product of
  the model's five conditionals. q(KIND_8 | …) is renormalised over KINDS, as in the one-step convention.

## Why exact enumeration, not sampling

The margin to beat is about 0.12 TV over up to 81 cells. Monte Carlo with N samples per window has TV error of order
√(cells/N), so N in the thousands per window would be needed. Enumerating record-7 completions over the model's
support is exact up to a reported truncation.

## Enumeration

A depth-5 token tree under the model:
- At each field, keep tokens with conditional probability ≥ θ = 1e-3, and record the dropped mass per window.
- **Fresh entity names** (names not yet in the window) are interchangeable under renaming. The model should treat them
  alike, but nothing forces it to. The design keeps one representative fresh token per entity type, weighted by the
  model's total fresh-name mass for that type.
  - This is an **invariance assumption about the model.** It is checked on a sample of windows by comparing the
    downstream q(KIND_8) under three different fresh representatives (max TV reported).
  - If the max TV exceeds 0.01 on more than 5 % of the sampled windows, the design falls back to full enumeration on
    those windows.
- Expected leaves: tens to a few hundred per window. A subsample of 10,000 test windows per model, fixed by seed
  before any output is seen, keeps CPU cost to about an hour per model.

## Monitors and scoring (two-step versions of what exists)

Truth and kind labels are per class, as before (pure: G < 1e-12, H\* > 1e-12; withheld: G ≥ 0.1; one-step G at k = 6).
- **Mass-blind, two-step:** the nearest pure vs the nearest withheld two-step law, margin 0.005. Compare it with the
  same monitor at one step on the *same* windows and k.
- **Prior-aware, two-step:** as in `prior-aware-monitor-declared-2026-10-23.md`, on two-step laws, with τ2 fitted on
  val two-step outputs.
- **Model precision:** the TV(P2_c, q2) distribution, set against the exact two-step margin.

## The question it settles

Does the two-step query make randomness certifiable *without a prior* for these learners? That is, does the mass-blind
two-step monitor reach what only the prior-aware one-step monitor reached? If the models' two-step error is of the
same order as the margin (about 0.12), it will not, and the lever exists exactly but not for these learners.

## Open points for review

1. Is θ = 1e-3 with dropped mass reported adequate? Or should the tree be cut by cumulative mass instead?
2. Is the fresh-name representative check strong enough, and is the 0.01 / 5 % fallback sensible?
3. Should OBJECT / RELATED / LINEAGE at record 7 be marginalised at all on interfaces where they are masked (r1 shows
   only KIND and ACTOR)? On masked fields the token is the placeholder, so the tree has one branch. That is what the
   design does. Confirm.
4. Subsample size and the train/val/test separation of τ2.

---

# v2 (same day), after the Codex review (`learner-two-step-design-codex-review-2026-10-23.md`)

Every finding is accepted. The changes:

1. **Normalisation (blocking).** Each record-7 slot's conditional is renormalised over its legal set:
   - KIND over KINDS (as the one-step convention, `learner_kind_classifier.py`); entity slots over non-PAD tokens.
   - **Masked slots are forced to the placeholder with weight one.** This is a constrained rollout: masking is a known,
     deterministic property of the interface, not something the model is asked to predict.
   - Record-8 KIND is renormalised over KINDS.
   - **Invariants, asserted per window:** Σ q2 = 1, and Σ_k2 q2(k1, k2) = q1(k1), where q1 is the one-step
     KIND-renormalised output at position 6.
2. **Fresh names.** No representative compression. Names are enumerated under the cumulative rule (3), with bindings
   growing within each branch, as the evaluator does. Compression is considered later only if a complete-rollout
   comparison on val bounds its effect on q2.
3. **Error budget.**
   - At each tree node, keep tokens in decreasing probability until their cumulative conditional mass reaches
     1 − 1e-4. The rest of that node is pruned.
   - η_w, the prefix-probability-weighted mass of all pruned subtrees, is computed per window. The normalised
     approximation is within TV η_w of the full q2.
   - Every distance comparison carries ±η_w. The mass-blind monitor abstains if |d_pure − d_withheld| ≤ 0.005 + 2η_w.
   - The η_w distribution is reported.
4. **Scope of the claim.** Success supports *this monitor on this population*. Failure does not show that the learners
   cannot exploit two-step information. Classwise, report the share of pure windows meeting the sufficient condition
   2·TV(P2_c, q2) + 0.005 + 2η_w < μ2_c, not error against the median margin. Labels remain one-step (G at k = 6), and
   the claim is about separating one-step-pure classes from one-step-substantially-withheld ones.
5. **Population.**
   - Eligible windows are those with at least 8 records.
   - The exact family's prior masses are corrected: RESET-class masses are halved before regrouping. At law (40, 8, 2),
     RESET windows with at least 8 records end at T = 8 only, against T ∈ {6, 8} for at least 6 records. Verified
     against `window_process.prefix_law_aggregate`'s docstring.
   - The conditional laws P1 and P2 are unchanged.
6. **Code adaptation.** The k = 6 family is read from the k = 6 two-step rows: one-step groups by `p_star`, two-step
   groups by `p2`. One-step and two-step monitors use the **same declared rule** and run on the **same windows**.
7. **Sampling and separation.**
   - A uniform sample of eligible windows, by a fixed seed, after eligibility filtering (not `--n`, which takes the
     first N before filtering).
   - 10,000 per model on test, and the same indices for every method.
   - Order of work: val first, to measure enumeration cost and η_w and to fit τ2. Settings are then frozen and the
     predictions declared, and only then is test run.
   - Results are reported with label denominators and seed-level spread.
