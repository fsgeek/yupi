# Paper 1 (methods), §2 draft v0.1 (2026-10-15): The instrument

> **Status: DRAFT v0.1, owning instance.** Governed by `paper1-skeleton-v0.9.md` §2. Compressed from
> `paper1-draft-s2-v0.3.md` (reviewed three times by both families); the full experiment table and the scoring details
> move to Appendix A. Not yet reviewed in this form.

## 2. The instrument

### 2.1 The world

Yupana is a small stochastic operating-system kernel whose state and transition law we own: four threads, two CPUs,
two locks and one asynchronous device, with a request pool of four and a device queue of depth two. Each thread runs
a fixed looping program, giving four contention roles. The kernel makes two kinds of random choice: which thread
runs next (round-robin with probability 1 − ε, uniform over runnable threads with probability ε; we report ε = 1 and
ε = ½), and whether the device completes a pending request on a step (probability 1/3). Every choice is labelled in
the next record by its kind and actor, so the future stays random however much is observed.

An episode runs 40 records from reset. The observer sees a *window*: the last 8 records ending at an endpoint drawn
uniformly from {2, 4, …, 40}, with a RESET token when the window reaches back to the reset. This window law was
fixed before any learner was trained.

### 2.2 Interfaces

Every record has five fields: KIND, ACTOR, OBJECT (which lock or device), RELATED (the thread woken, or the owner)
and LINEAGE (the request identifier). Interface r0 shows only KIND, and each of r1–r4 shows one more field; hidden
fields are rendered as a placeholder, so every record is five tokens on every interface. Before any learner existed,
each added field was shown to change some posterior or some finite-horizon predictive distribution.

Entity names carry no identity across episodes: they are drawn per episode from pools much larger than the entity
counts (64 thread names for four threads, for example).

### 2.3 Exact quantities and their validation

Two observers appear. The *structural observer* sees structural identities; we use it only for state uncertainty
(§3.2). The *pattern observer* sees each entity renamed by order of first appearance, so that only the pattern of
who recurs remains. Because names are redrawn every episode, it is the learner's comparison point, and every other
quantity in this paper is for it, at position 7 (after seven records, predicting the eighth). The *ceiling* is the
law-mass-weighted entropy of the exact predictive law given the pattern class, a Bayes predictive loss.

| quantity | validation | coverage |
|---|---|---|
| structural window posteriors | the filtering recursion agrees with an independent path summation | exhaustive: 8,542,940 windows, all ten (interface, ε) cells |
| pattern-class predictive laws | agree exactly with an independent pattern filter | exhaustive class by class at a small law (8, 4, 2); at the frozen law, a random sample of 82–91 test windows per cell, all exactly equal |
| lag profile ι_m = H_m − H\* | the KL route and the entropy route agree | every row, to 3 × 10⁻¹⁴ |
| ceiling-holding rewrites | equal KIND marginal per class; equal multiset of record probabilities per class; an independent construction checked by brute force | exhaustive over classes |
| the R/G split (§3.1) | each interface's mean H\* reproduces the ceiling; G ≥ −10⁻¹⁵ per class (a mutual information, up to rounding) | every class, both ε |

**What none of this validates is the kernel.** Every route calls the same kernel functions. The gates check the
computation *given* the kernel; the kernel rests on its tests, reviews, and one property tested directly: from a
reset, the r1 projection determines the structural state for every transition path up to eight records, at both ε.

### 2.4 Learners

A decoder-only transformer (4 layers, width 128, 838,940 parameters) is trained from scratch on 2 M windows per
cell with AdamW and a cosine schedule, for 5 or 15 epochs; at 15 epochs validation loss is still falling slowly, so
we write "at 15 epochs" rather than "at convergence". The measurement is the KIND shortfall at position 7: the
realised log-ratio between the exact law and the model's prediction, whose class mean estimates KL(P\* ‖ q). On the
content interfaces it runs at about 1–4 % of the ceiling. The trained model is the unit of inference: three seeds per
cell, and inference per model or per matched seed pair. Which experiment was pre-registered, on which models and at
what budget, is tabulated in Appendix A.

---

## Provenance

- All of §2: `paper1-draft-s2-v0.3.md` §2.1–2.5 and its provenance; Appendix A (`paper1-appendix-A-instrument-v0.1.md`).
- R/G validation row: `kind-uncertainty-split-40-8-2-k7-eps*-2026-10-15.json` (minimum class G −8.9 × 10⁻¹⁶).
- Injectivity: `reset-injectivity-r1-2026-10-13.jsonl`.
