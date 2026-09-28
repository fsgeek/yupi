# Paper 1 — skeleton, decisions, and readiness (v0.1, 2026-09-28)

> **Status: GOVERNING for paper 1's shape until superseded by a versioned revision.**
> Written by the instance of 2026-09-28. The PI's terms (2026-09-28) are these. Paper 1
> is "ready" when we judge it ready for **external review**. The owner of the project
> defines that bar. A result goes in only if **it teaches something most readers won't
> already know.** This document is not a §23 of the learner note. The note is the
> evidence, and this document selects from it. Anything the note holds that is not
> named here stays in the note.

## 0. How this was made

On 2026-09-28 a workflow ran (script `docs/paper1/audit-2026-09-28-workflow.js`). A
charter reader extracted the contribution, RQs, hypotheses, cut and prior art from the
proposal, both M1 parts, the status map and both literature notes. Six partition
readers extracted **90 findings** from the rest of `docs/`. Each finding was then given
to two agents. An adversarial skeptic tried to refute it against the notes, the raws and
any later corrections. A novelty judge applied the PI's test for an ML/interpretability
reader who knows Othello-GPT, Shai et al. and linear probing. A synthesizer drafted a
skeleton, and a simulated hostile reviewer and a completeness critic read it. In all,
190 agents ran with no errors. All outputs are committed unedited under `docs/paper1/`
(`audit-2026-09-28-*`). **What follows is my reading of them, not theirs.** Where I
adopt a numeric correction from them, I reproduced it first (§4).

## 1. What the audit says, plainly

- **Support.** 84 findings were supported after a correction, 5 were supported as
  stated, and 1 was not supported (`stipulated-prior-phantom-gap2`, a buggy-kernel
  residue). The corrections are mostly scope and wording, and they are listed per
  finding in the result JSON.
- **Novelty.** 42 findings were judged *expected*, 42 *project-internal*, and 6
  *novel as instrument demonstrations*. **None was novel in itself.** This matches both
  literature notes: the novelty is only the *conjunction* (interface as the variable
  over a fixed generator, exact per-interface ceilings, and a learner scored against
  the ceiling it actually faces, in a structured systems world).
- **The learner lesson as drafted does not survive review.** The draft's lesson was
  "the ceilings fall monotonically down the ladder but the learner's excess does not,
  and an exposed field shifts the ceiling by as much as the learner's whole shortfall."
  Three things are wrong with it:
  1. The ceilings the learner faces are **not** monotone. r4 is above r3 at every k
     (§4, C1), because each rung's ceiling is the entropy of a different target.
  2. The "field worth as much as the shortfall" comparison sets a per-lock sum on a
     subset against per-record excess (§4, C2).
  3. The reviewer's objection is the important one. **r1 ≈ r3 < r2 is what you would
     expect if excess tracks how much the ceiling needs hidden state inferred from
     history.** At r2 the lock owner can be inferred but is not printed: a third of
     the (window, lock) examples are uncertain, at 0.236 bits each (§17.2). At r3 and
     r4 it is printed, so that load is exactly 0. At r1 the locks are invisible, so
     nothing can be inferred.

## 2. Decisions (owner, 2026-09-28)

**D1. Paper 1 is an instrument paper whose learner half asks one question:** *what
predicts a small transformer's excess over the exact ceiling across observation
interfaces?* The candidates are ceiling entropy, target size (fields per record), and
**implicit information**: information about the next record that the trace carries only
through history, which the instrument can compute exactly (definition in D2). This is
the one learner-side question that **only an exact instrument can ask**, because the
regressor is itself an exact quantity. If implicit information predicts excess, the
lesson is that small transformers lose what the trace implies, not what it withholds or
states. That lesson is novel. If it does not, the paper is a pure instrument paper and
says so. Either outcome can be published; the only unpublishable version is one that
never tests it.

**D2. Implicit information: definition (v0.1, to be frozen before any learner number is
regressed on it).** For a prefix class c at position k, with the pattern observer's
exact next-record law P*(· | c), and with P*_m(· | c) the exact law given only the last
m records of c (the law-mass mixture of P* over classes sharing that suffix pattern):

> ι_m(c) = KL( P*(· | c) ‖ P*_m(· | c) )  — bits the history beyond the last m records
> contributes to the ceiling, per window.

ι_m is a function of the prefix only (the prefix-only rule holds by construction). Its
law-mass mean is H*_m − H*: the gap between the exact **order-m Markov ceiling** and
the full ceiling. The same tables therefore give the best any m-record-memory learner
could do, which is the n-gram baseline the reviewer asked for, exactly and for free.
Open design points: the naming re-key of the suffix (the pattern renaming depends on
earlier records); the choice of m (1 primary, 2 secondary); and whether ι is computed
on the canonical or the pattern observer (pattern: it is the one the learner faces).

**D3. Common target.** Cross-rung learner comparisons are reported on a common target
(the KIND field's exact KL, which the evaluator already splits, plus the r0 projection
where computable) next to the whole-record numbers. Whole-record ceilings across rungs
are entropies of different targets (C1).

**D4. Out of paper 1, recorded here so the omission is on the trace:**
- capacity/size claims (RQ5, H7): size enters only as a budget control, and the size
  runs now on the card choose the budget;
- synchronization markers and snapshots (TIME_CLASS is unbuilt), and the proposal's
  cross-L context axis: context in paper 1 is k within L = 8, stated as such;
- the D3 binding-split and lexical-split evaluation, deferred to M4;
- H1 (belief versus implementation state): the belief-geometry design excludes
  entity-coordinated targets (§16.1), and no coordinate-free implementation target
  exists. H1 is out unless one is designed. H2 (calibration on non-degenerate
  posteriors) is in;
- field-permutation and redundancy controls, workload-composition splits, and the
  §8.7 generalization tests. They are named in §6 as future work.

**D5. Naming.** r4 is "allocator-leaking lineage" in the paper (its lineage cargo is
the allocator, not matching; `lineage-rung-cargo-allocator-not-matching`).

## 3. Readiness for external review, in blocking order

1. **Order-m exact ceilings and ι** (D2). CPU, exact side, no GPU. This gives the n-gram
   baseline and the regressor at once. Design note first, then a gate: ι computed two
   ways (per-class KL mean against H*_m − H*) must agree exactly.
2. **Canonicalize-and-count learner baseline** (the reviewer's objection 1): a
   first-appearance name canonicalizer plus a smoothed count table over prefix classes,
   scored under the same contract. If it sits on the ceiling, gap 2 is a statement about
   transformers at this scale, and the paper says so.
3. **Per-window test of D1 on the existing raws, labelled exploratory**: excess against
   ι per window and per class, per cell and seed. The evaluator's `on_window` callback
   exists. This decides whether step 5 carries a confirmatory prediction.
4. **Budget choice** from the running size follow-up (`scripts/learner_gpu_2026-09-28.sh`,
   a981d72): the budget at which d = 128 has flattened, or the 45-epoch d = 256 point if
   it passes d = 128.
5. **Converged ladder re-run, confirmatory**: r0–r4 × ε ∈ {1, ½} at the chosen budget,
   ≥ 6 seeds per cell. Predictions (the rank of excess by ι versus by H*) are written
   and OTS-stamped before the first run starts. Per-seed strip plots; r4 is reported as
   basins.
6. **A load-separating control**: an r2 variant that reveals the owner intermittently at
   a controlled rate. If D1 holds, excess falls with the revealed fraction as ι does. Also
   the ctrl-irr decoy (P(field | kind) preserved), which tests "one more cheap field". The
   reviewer and critic are both right that the decoy alone cannot separate load from
   field count. Token budgets are matched across rungs, or the mismatch is reported.
7. **Belief-geometry completions**: an untrained-network probe control for every OIR;
   per-seed absolute extracted bits next to OIR; the λ grid widened past both edges; H2
   calibration; seeds 2–3 at k = 2..6; the §21 distance-geometry result (Spearman
   0.86–0.99) moved into the RQ3 status; the design-vs-execution deviations disclosed
   (λ grid, 1,000 against 2,000 geometry windows).
8. **Ceiling normalization**: recompute every cell's ceiling on the continuing-window
   base the excess uses (the k = 7 tables carry 0.85 of law mass).
9. **Estimator fixes**: the endpoint claim uses `end_total_bits`; per-kind attributions
   separate the outcome-selected KIND part; §17.3's post-hoc link is redone prefix-only
   or dropped.
10. **Exposure-gap note v0.2** before any model-versus-ceiling number leaves the
    repository: Wen et al. 2609.11132, the sign and nesting conditions, the
    condition-indexed "floor" from the 2026-09-04 addendum, and every KL_repr/KL_out pair
    labelled a Q_logit point.
11. **Corpus-track Clause 3** (lock/device/request naming), or every corpus-track number
    labelled a thread-naming lower bound. A gate record for the 2M-window corpora.
12. **Exact-side reruns**: exhaustive injectivity checks on worlds A/B/C with the
    corrected kernel; divergent classes at Δτ = 0.01 along δ_p; the Part II §3.2a
    erratum; a C0b truthsayer pass.
13. **Literature**: Mason & Anand 2603.20531 in §1 (the constructive-complement
    framing); Shai et al. and MetaOthello as contrasts; grid walkers 2603.16689;
    V-information (Xu et al. 2002.10689) as the grounding of gap 2; the disambiguation of
    "observability"; the eight papers the draft lists for full reading; a priority review
    immediately before submission.
14. **Appendices**: the full confirmatory scorecard (held-out Tier 1, W11, D8 C0b/C1, D10
    as corrected), and provenance (the kernel defect and relabelling, the Gate 6
    deviation, a51613a/94699fd, the endpoint-pooling erratum, the thirty (40,8,2)
    artifacts produced before enactment, and the support bound: frontier 1,964,919
    against 2×10⁶).

## 4. Corrections adopted, reproduced before adoption

- **C1** (critic A.2; reviewer, "claims I do not believe"). The r4 pattern ceiling
  minus the r3 pattern ceiling, from `pattern-ceilings-40-8-2-k{1..7}-2026-09-18.json`,
  at full precision:

  | ε | k=1 | k=2 | k=3 | k=4 | k=5 | k=6 | k=7 |
  |---|---|---|---|---|---|---|---|
  | 1 | +1.5e-5 | +9.1e-5 | +5.2e-5 | +2.1e-4 | +1.2e-4 | +3.9e-4 | +3.3e-4 |
  | ½ | +5.2e-6 | +9.0e-5 | +2.2e-5 | +2.0e-4 | +3.5e-5 | +3.3e-4 | +1.1e-4 |

  Positive everywhere. This is recorded at the top of the learner note.
- **C2** (critic A.4; reviewer objection 3). §17.2's 0.121 is a sum over visible locks,
  per window, on the 25,508 windows that have a visible lock ("Per window (summing the
  visible locks)", note §17.2 header). Reading 1's two comparisons are withdrawn. This
  is recorded at the top of the learner note.
- Adopted from the audit without a separate numeric check, because they are scope
  statements the notes already make: the corpus-track banner (the numbers are lower
  bounds until Clause 3); the r0→r1 decomposition is open at every law (exit-clause note
  §5, §11); the injectivity result is a proof sketch on the quotient.

## 5. Section outline (from the draft, with D1–D3 applied)

| § | Section | Teaches |
|---|---|---|
| 1 | Introduction | Text-only observation cannot verify epistemic states (Mason & Anand). In a world small enough to count, we can measure exactly what a trace carries, and where a learner loses it. The novelty is the conjunction. |
| 2 | The instrument | Exact ceilings are exact *for a stated observer*. The canonical and pattern tracks are different quantities, and the learner is scored against the pattern track. Two-path gate over 8,542,940 posteriors; what that gate does and does not validate. |
| 3 | Exact observability | Interface value exists only where the window hides history (injectivity from reset). At the frozen law, four distinct regimes with a thin top rung. Exact attribution of a gap to one coordinate (D8 C0b). Divergent classes. |
| 4 | Where the learner loses | D1: excess against ι, H* and target size, on a common target; the order-m ceilings as the n-gram baseline; count and GRU baselines; the converged confirmatory ladder; the load-separating control. |
| 5 | Belief geometry | The exact next-kind belief is linear after one record, and less accessible with context. The first block extracts a roughly fixed amount whatever the interface (with absolute bits and the untrained control). Distance geometry. The last layer equals the output (a Q_logit point, not gap 3). |
| 6 | Limits | Kernel-shared validation, lower-bound corpus track, the fragility of δ, basins, budget, the D4 omissions, future work. |
| A | Appendices | Confirmatory scorecard, provenance, thresholds, estimator errata. |

The cut list is the draft's `docs/paper1/audit-2026-09-28-skeleton-draft.md` §4, adopted
as is, with `r4-outlier-basin` added to §6 (critic A.1).

## 6. What would change this document

A result from §3 steps 1–3 that contradicts D1 changes §4's framing (not the
instrument). A converged re-run that flattens the learner ladder makes paper 1 a pure
instrument paper. Any change is a v0.2 of this file, with the reason stated here.
