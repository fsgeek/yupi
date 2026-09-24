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

## Amendment v0.3 (2026-09-23, recorded 2026-09-24): coordinate-free targets

Built and reported in the first-results note §16.2 before this entry was written. `--target held` (is lock l owned
by anyone) and `--target owner-is-actor` (is its owner the thread that just acted) fold the owner posterior into
facts that need no entity coordinates (`yupi.learner.probe.collapse`), read linearly at p0. Motivation: the v0.2
control showed entity identities are not held in the stream at the record boundary (recoverable at the actor's own
input position, CE 0.002; nothing at p0).

## Amendment v0.4 (2026-09-24, by the instance of 2026-09-23): need, not presence — and the per-window link

§16 measured whether lock state is **present** at the boundary. Two companions, both from artifacts that already
exist, before any which-thread probe is built:

1. **Value of the owner for the next record** (`yupi.learner.probe.next_dist_by_owner`, `mutual_information`;
   `scripts/learner_probe_voi.py`; raw prefix `learner-probe-voi`). From the same joint belief the labels come from,
   per (window, lock l): I(next record; owner of l | prefix) = H(P*(next)) − Σ_z P*(z) H(P*(next | Z = z)), in bits,
   with the owner folded to held / none and the record coarsened to its kind as variants, plus H(next) and H(kind).
   Exactness gate: the weighted mixture of the conditionals equals `next_pattern_dist` as Fractions
   (tests/test_learner_probe.py). Zero wherever the prefix determines the owner, so this is r2's number; r3 and r4
   run as zero gates. Reading: the share of the ceiling's next-record entropy that ownership accounts for, against
   the cell's excess and the r2 − r1 gap.
2. **Per-window link** (`scripts/learner_probe_owner.py --per-example`; `scripts/learner_probe_link.py`; raw prefix
   `learner-probe-link`). Join the probe's per-example CE on `held` at the best layer to the window census's
   per-window excess at the same k (the census scores the record predicted from p0). Spearman / Pearson of probe
   CE with structural excess and with KIND-field excess; mean excess by probe-CE quartile with a 200-draw
   permutation null on the top − bottom gap; separately on prefix-determined examples (probe CE is pure
   representational error there) and on uncertain ones (CE − H). Correlational; no causal claim. Cells: r2, r3, r4
   ε = 1, every seed.

Not changed: v0.1–v0.3 targets, splits, λ selection, the OIR report. The which-thread probe (a readout at an entity
token's position, with a positive control at that position) stays designed-in-words until these two say whether it
is worth building.

*Post hoc additions to v0.4 item 2 (2026-09-24, after the all-window link came back null; reported as exploratory
in the note's §17.3):* (i) the join restricted to the windows whose realized record k + 1 is an event on lock l
(`--corpus-dir`); (ii) residualization on 50 bins of log(1 + the class's training-corpus count)
(`scripts/learner_class_frequency.py`, `--class-freq`), added to control the shared-difficulty confound named in
§17.4, and a between-class analysis on class means (≥ 3 windows). The pre-specified all-window test is reported
first and unchanged.

## Amendment v0.5 (2026-09-24, by the instance of 2026-09-23): the which-thread question is an exposure question

§17.2 put the need on the owner's *identity* (0.073 of 0.121 bits per window at r2). Where would a model hold it?
The record layout is kind, actor, object, related, lineage. At the boundary p0 the model predicts the kind, and
the owner's identity matters there only through "held by someone other than the candidate actor", which is the
held / owner-is-actor fold already read in v0.3. The identity itself is needed one position later: having read
kind = RELEASE (or, at r3/r4, when emitting the related field of a BLOCK), the model must name the owner as the
actor. Its own output distribution at that position **is** the readout, and the evaluator already scores it: the
ACTOR-field excess on windows whose realized record k + 1 is a RELEASE (window census rows, `by_field.actor`).
A position-pair probe would ask whether identity is linearly present at a place the model has no reason to keep it;
the field excess at the point of need asks whether the model *uses* it, against the ceiling's own uncertainty.

Design: `scripts/learner_release_actor.py`. Per run (census rows of §13, k = 7) and per window whose realized
record k + 1 has kind ∈ {RELEASE, BLOCK, ACQUIRE}: the ACTOR-field excess from the census row; from the k = 7
ceiling table, H*(actor | kind, prefix) (the exact observer's residual uncertainty about the actor given the kind)
and P*(kind | prefix); for RELEASE records at r2, whether the released lock's owner is determined by the prefix
(H(owner | prefix) = 0 from the §16 labels) or not. Report per (cell, seed, kind): n, mean actor excess, mean
H*(actor | kind), and the exposure ratio 1 − excess / H* (the field-level analogue of the OIR: 1 = the model's
actor distribution matches the ceiling's, 0 = it carries none of the trace-available information about the actor);
for r2 RELEASE, the same split by owner-determined / uncertain. Cells r1–r4 ε = 1, every seed with census rows.
Gate: the ceiling table's star for a window's class reproduces `kind_marginal`'s P*(kind) and H*(actor | kind)
is ≤ log2(#threads seen + 1). Raw prefix `learner-release-actor` (non-measurement).

The position-pair probe is withdrawn from the plan unless this measurement says the model exposes less identity
than the boundary probe's held-bit deficit would explain.
