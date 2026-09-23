# Probe v0.1: lock ownership in the residual stream (sub-project 3, first target)

> Status: design, 2026-09-23 12:45 PDT, by the instance of 2026-09-21. Motivated by first-results note §13–15: the learner's r2 penalty
> sits on lock-contention records; at r3 the owner is printed and the penalty falls; r4's worse basin over-pays on BLOCK.
> Hypothesis under test: **lock ownership is less linearly accessible in the residual stream at r2 than at r3**, and less
> in r4's high basin than its low one. Proposal §8.3 (OIR) is the metric.

## Target Z
For a window prefix of k records and each lock pattern index l visible in it (B = 2 locks per episode at (40, 8, 2)),
Z = owner of lock l after the k records, in the pattern observer's names: one of {none, t0, t1, t2, t3, unseen}
("unseen": owned by a thread that has not appeared in the prefix). Exact posterior P*(Z | prefix) from
`filter_pattern_window(..., prefix=True).joint_marginal()` over (state, binding): kernel lock = binding[1][l],
owner = state.lock_owner[kernel lock], mapped back through binding[0]. Labels are a function of the class, so they are
computed once per class and shared by every seed of a cell.

## Activations A
Residual stream of the trained Decoder (`return_hidden=True`: embedding + 4 blocks, 5 layers) at input position
p0 = offset + 5k — the position that predicts the (k+1)-th record's kind, i.e. the state after k records. One vector
of d = 128 per (window, k); the same vector serves both locks' probes.

## Probe family
Affine map A → logits over the 6 classes, one probe per (layer, lock index l), fit by minimizing the expected
cross-entropy against the exact posterior (soft labels) with L2 penalty λ, full-batch L-BFGS in torch (no new
dependency). Fit on the corpus **val** split (10⁴ windows), evaluate on the first 3·10⁴ windows of the **test** split.
λ chosen on a held-out fifth of val from {1e-4, 1e-3, 1e-2, 1e-1}; reported.

## Reported per (cell, seed, k, layer, l)
CE(Z | A) on test (bits per example), H(Z) (entropy of the test-set marginal of P*), H(Z | h) (mean exact posterior
entropy), OIR = (H(Z) − CE) / (H(Z) − H(Z | h)); argmax accuracy against the posterior argmax; the same CE split by
whether the prefix determines the owner (H(Z | h) = 0) or not. Baseline: the constant probe (CE = H(Z), OIR = 0).
Ceiling: OIR = 1 (the probe reproduces P*).

## Cells
r2, r3, r4 at ε = 1, all seeds that exist (3, 3, 6); k = 7 first, k = 1..6 after if the k = 7 result warrants it.
r1 is excluded (locks masked: Z is not in the pattern observer's names at r1).

## Gates
- Labels: for every class the posterior masses over Z sum to 1; a window whose prefix contains ACQUIRE(t, l) with no
  later RELEASE(·, l) has P*(Z = t) = 1 (test); at k = 0 every visible lock is "invisible" (no examples).
- Probe: on synthetic data where A encodes P* linearly, OIR → 1; on A independent of Z, OIR → 0 (≤ small positive).
- Raw prefix `learner-probe-owner` registered as non-measurement.

## Out of scope for v0.1
Causal patching (§8.5); belief-geometry alignment over the whole posterior (§8.2); r1; ε = ½; other latent facts.

## Amendment v0.2 (2026-09-23 13:16 PDT): the readout must be in the model's coordinates

The v0.1 linear probe to pattern classes {none, t0..t3, unseen} scored OIR 0.35 on r2 (layer 3, three seeds),
and a **control** with the same probe family on Z' = pattern index of the actor of record k — a fact the model has
just read — scored OIR 0.15 (r2 seed 1, layer 3–4; raws under ~/.cache/yupi-scratch/probes/control-*). The
pattern observer's first-appearance index is not what the model represents; a linear map cannot recover it even
for the most recent actor. v0.1's owner number is therefore uninformative about ownership.

v0.2 readout: the owner as a **thread token**, decoded through the model's own token-embedding matrix E:
for each example the candidate set is {none, unseen} ∪ {thread tokens seen in the prefix}; logit(τ) = hᵀ W E_τ + b_tok
for a token τ, and free scalars b_none, b_unseen; softmax over the candidate set. Parameters W (d × d) + 3 scalars.
The exact posterior's t_i maps to the i-th thread token in first-appearance order (binding[0]'s pattern order is the
surface order by construction). Fit, λ selection, splits and the OIR report as in v0.1. Control: the same readout on
Z' = actor token of record k (expected OIR ≈ 1 if the readout works). Raw prefix unchanged; the raw records
`readout: "bilinear"`.
