# Belief geometry, coordinate-free: the next-kind belief at the record boundary (v0.1)

> Status: design, 2026-09-24, by the instance of 2026-09-23. Paper 1's belief-geometry slice of Milestone 5
> (proposal §8.2), in the form §16–§19 of the first-results note have shown to be the model's own: no entity
> coordinates, exact targets from the ceiling tables, and the *output* at the same position measured beside the
> representation so gap 2 (accessible representation) and gap 3 (exposure) are read on one quantity.

## Question
At the record boundary p0 (the position that predicts record k + 1's kind), does the residual stream linearly carry
the exact observer's belief about what comes next, P*(kind_{k+1} | prefix), and how does what is linearly *there*
compare with what the model *emits* there?

## Target Z
P*(kind_{k+1} | prefix): the ceiling table's `kind_marginal(star)` for the window's class, a point on the 9-simplex of
event kinds. Exact, coordinate-free (kinds are the model's own tokens), available for every test window from the
k = 7 tables without a labelling job. Later variants (same machinery): the horizon-2 kind belief P*(kind_{k+2} |
prefix) if the exact side can price it; the folded actor class {record k's actor, other seen, fresh}.

## Activations A
Residual stream at p0 at each of the 5 layers (embedding + 4 blocks), as in the probe (`return_hidden=True`),
d = 128. Same runs as §16–§19 (r1–r4 ε = 1, 2M, every seed with census rows; r0 excluded: no kinds beyond STEP-like
under its mask? — check r0's kind alphabet before including).

## Probe family and fit
Affine A → logits over the 9 kinds, expected cross-entropy against the soft target (existing `fit_probe`, L-BFGS,
λ ∈ {1e-4, 1e-3, 1e-2, 1e-1} on a held-out fifth). Fit on test windows 30,000–84,986 (never used by §16–§19's
evaluations); evaluate on the first 30,000 (the set every per-window artifact of this note is indexed on). Also
report a class-disjoint evaluation (windows whose class does not occur in the fit set) so representation is not
confused with memorized prefixes.

## Reported per (cell, seed, layer)
- OIR_kind = (H(Z̄) − CE) / (H(Z̄) − H(Z | h)) with Z̄ the eval-set kind marginal and H(Z | h) the mean exact kind
  entropy (as §16).
- KL_repr = mean KL(P*(kind) ‖ probe(h)) per window; KL_out = mean KL(P*(kind) ‖ P̃_M(kind | non-PAD) at p0), the
  evaluator's `kind_kl_bits` recomputed from the same forward pass; and the per-window join of the two (Spearman,
  KL_out − KL_repr by H*(kind) bins). KL_repr < KL_out at the best layer means the stream holds kind belief the
  output does not emit (an exposure gap at this position); KL_repr ≈ KL_out means the boundary exposes what it holds.
- Geometry (§8.2's alignment items): Spearman between pairwise distances of exact kind beliefs and of the probe's
  outputs on 2,000 sampled eval windows; layerwise.
- Splits, all prefix-only: H*(kind) bins; the §16 owner-state fold (all-determined / some-uncertain), for the r2
  story.

## Gates
- Target: P*(kind) sums to 1 for every eval window and equals `kind_marginal` of the window's star (exact).
- Probe: the existing synthetic gates (linearly encoded posterior → OIR → 1; independent → OIR → 0).
- Output: KL_out reproduces the run's evaluator `kind_kl_bits` mean at k = 7 to four decimals (the census gate).
- Raw prefix `learner-belief-kind` registered as non-measurement.

## Out of scope for v0.1
Full-state posteriors in kernel or pattern coordinates (§16.1 showed pattern coordinates are not the model's);
causal patching (Milestone 5 causal-use slice, paper 3 under the cut); horizon > 1 until the exact side prices it.
