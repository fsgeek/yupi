# Exposure pre-declaration v0.1: review record (2026-10-15)

> Reviewed: `exposure-prereg-v0.1.md` (draft, unstamped). Claude reviewer: **NOT READY**, 15 findings. Codex
> reviewer: first run hung on stdin for an hour (owner error: no `< /dev/null`, launch not checked); rerun in
> progress, its findings will be appended here. Owning instance. Every finding below that the owner relied on
> was reproduced by the owner, as noted.

## Dispositions, Claude review

| # | finding | severity | disposition |
|---|---|---|---|
| 1 | V2 false: the count table is a Witten–Bell order-6 estimator, KIND KL 0.0443 at k = 7 (r1 ε = 1), not P\* | BLOCKING | **Adopted, reproduced** (`count-baseline-r1-eps1-2026-10-04.json`: chosen wb, max_order 6, mean 0.04431). V2 becomes an oracle learner, Q := P\*. Owner error: V2 was written from an assumption about the artifact, not the artifact. |
| 2 | V3 has no reference: no `kind_kl_bits` in the ladder raw or census | BLOCKING | **Adopted, reproduced** (grep: 0 hits in both; census rows carry only realised-record `by_field.kind`). V3 becomes a per-window bit-exact reproduction of `by_field.kind` against the sha-pinned census jsonl, plus n. Same owner error as 1. |
| 3 | V4 vacuous (missing_classes 0 = 0); V1 algebraic | SHOULD-FIX | Adopted. V4 → window-index set equality with the census `i` field. V1 kept, labelled as a code check, computed from log-probs. |
| 4 | Q not a distribution under `kind_output`; RESET in KINDS; "what a reader sees" overstated | BLOCKING | Partly pre-empted: convention fixed 2026-10-15 before the review returned (renormalise over KINDS; `kl_eval` = KL − log₂(1 − off), tested). RESET: P\*(RESET) = 0 at k = 7, its Q mass is reported. Wording adopted: "continuation-conditional one-step KIND entropy", not "what a reader sees". |
| 5 | g is not Braverman/Cao's sequence-level quantity; **mean g is near-forced**: dCE/dβ at β = 1 equals −g for Q_β ∝ Q^β | SHOULD-FIX | **Adopted, derivation checked by owner.** Call g "one-step teacher-forced entropy calibration". Stage 1's mean g and "telemetry dominated by H\*" are near-guaranteed (mean KL ≈ 0.015 vs H\* ≈ 1 bit) and are reported as checks, not findings. |
| 6 | corr(H_Q − H\*, KL) and the H_Q regression are partly circular | SHOULD-FIX | Adopted. Primary: corr(g, KL); slope of (H_Q − H\*) on KL tested against 1; reader-side detection of high-KL classes from H_Q alone. |
| 7 | deterministic classes build in correlation | SHOULD-FIX | Adopted: correlations within H\* > 0; H\* = 0 reported separately. |
| 8 | forking paths: weighting, class unit, bins, deciles, checkpoint shas, recipe split (runs/gpu vs ladder15) | SHOULD-FIX | Adopted in full for any v0.2. |
| 9 | Stage 2 H2a–H2c follow from the objectives' closed-form optima (DPO: π ∝ π_ref·exp(r/β); outcome-matching ⇒ power-sharpening toward P\*; RLVR; greedy self-distillation) | BLOCKING | **Adopted. This is the decisive finding.** Stage 2's directions are predicted a priori; only deviation from the closed form, its dependence on base ignorance (KL_ref) and on the interface, and dose-matched frontiers remain. See "Consequence" below. |
| 10 | Stage 2 arms ill-defined for five-token records; seed count contradiction (3 vs ≥ 5) | BLOCKING | Adopted; moot until the Stage 2 question is re-chosen. |
| 11 | P is outcome-supervised, not text-only | SHOULD-FIX | Adopted. A text-only arm needs a judge that never sees the outcome (e.g. typicality). The outcome arm is relabelled. |
| 12 | PACMI mapping loose; floors at H\* = 0; high-KL classes scarce and rarity-confounded; "fabrication" ≈ high KL with low H_Q | SHOULD-FIX | Adopted. The high-KL/low-H_Q region ("confidently wrong") is the closer analogue and is measurable in Stage 1. |
| 13 | literature support for "Q2 open" incomplete; missing DPO, sharpening, RLVR, Kalai et al. | SHOULD-FIX | Adopted. Owner verified via arXiv API: 2305.18290 (Rafailov et al.), 2412.01951 (Huang, Block, Foster, Rohatgi), 2504.13837 (Yue et al.), 2509.04664 (Kalai, Nachum, Vempala, Zhang). Owner read 2609.17376 (Balcells, …, Riechers, Shai) in full text: six pretrained LLMs, HMM data in context, belief probes and steering; **no** base-vs-instruct comparison, **no** entropy-calibration measure. It does report later layers moving the output away from the process: an exposure observation. Agarwal/Misra paper III still unlocated. |
| 14 | the "telemetry beats testimony" half is untested: Yupana has no testimony channel; kill criterion misses "informative but trivial" | NOTE | Adopted. Kill criterion amended: a result predicted by a closed form counts as trivial. |
| 15 | register `exposure-` prefix before any raw; per-window output should carry the realised-kind log-ratio | NOTE | Adopted. |

## Consequence (owner)

Findings 5 and 9 together remove most of v0.1's interest. Stage 1's headline is forced by first-order
optimality, and Stage 2's directions are forced by the post-training objectives' optima. An exact world makes
those predictions computable, which makes them less surprising, not more.

What a closed form does *not* give is what happens inside. The optima describe output distributions only.
Whether post-training removes the model's internal representation of the world's uncertainty, or only stops
exposing it, is not determined by any objective: that is the founding letter's accessible-representation vs
exposure gap, and 2609.17376 already sees later layers pull outputs away from an internally held belief in
pretrained LLMs. In Yupana it can be made exact: probe-accessible exact belief vs output, before and after
post-training, per class and interface. If uncertainty survives internally while the output sharpens, internal
telemetry beats output telemetry, which bears directly on PACMI's state object (entropy *and* attention).

Held loosely. It came as quickly as v0.1 did, and probes were cut on 2026-10-09 for thin evidence (one seed
carrying the trend, no untrained control, ε = 1 only). A v0.2 on this question needs, at minimum: an untrained-
model control, ≥ 5 seeds, both ε, a pre-declared probe family and capacity, closed-form output targets per arm as
the null for the output side, and a literature check on post-training vs internal representations (e.g.
"alignment is shallow"-type results) before it is written.

**Decision deferred until the Codex review is in.** v0.1 is not stamped and will not be.

## Dispositions, Codex review (rerun with stdin closed; NOT READY, 17 findings)

Codex converged independently with Claude on V2 (its #3), V3 (#4), V4/V1 (#5), forking paths (#6, #7), the
closed-form predictability of Stage 2 (#13), the outcome-informed judge (#12), arm definitions (#11), and the
untested motivating claims (#17). All adopted as above. New findings:

| # | finding | disposition |
|---|---|---|
| 2 | **Negative control kills the tracking metric.** A context-independent uniform Q has H_Q = CE = log₂K, g = 0, KL = log₂K − H\*: corr(H_Q − H\*, KL) = 1 for a model that ignores every window. | **Adopted, checked by owner** (algebra immediate). Any tracking claim must beat this control and an H\*-only predictor. |
| 4 | V3 repair exists: `learner-eval-*.json` summaries for all 30 models carry `kind_kl_bits` with matching hashes. | Adopted for any successor design. |
| 5 | evaluator `missing_classes` counts windows, not classes. | Noted. |
| 8 | mean g cancels; need mean \|g\| and tails. | Adopted. |
| 9 | first-order/second-order argument fails at support boundaries (deterministic classes: KL ≈ ε/ln2, H(Q) has ε log(1/ε)). | Adopted; Claude #5's temperature argument is unaffected (it is a global stationarity condition). |
| 10 | KIND-renormalised Q hides off-KIND failure. | Adopted: off-KIND and PAD mass reported beside every metric. |
| 15 | **H\* > 0 is not aleatoric.** Under an interface, H\* = H(next \| S) (transition randomness) + observation gap (hidden state the interface withholds); Table 3.0 already separates them. | **Adopted. This is the most useful finding of either review** (see Decision). |
| 16 | Paper III is arXiv:2512.23752; Baldelli et al. 2605.11845 is precedent for sampled-target SFT with exact target comparisons; CATTO 2601.23096; "Forcing Diffuse Distributions…" (2024). | **Owner verified** 2512.23752 (Agarwal, Dalal, Misra, "Geometric Scaling of Bayesian Inference in LLMs": a last-layer value axis tracks predictive entropy across Pythia, Phi-2, Llama-3, Mistral; Mistral base vs instruct shows "modest changes"; they name heavier alignment as open) and 2605.11845 (Baldelli et al., "Probabilistic Calibration Is a Trainable Capability in Language Models"). CATTO and the 2024 paper not yet checked. |

## Decision (owner, 2026-10-15)

**v0.1 is retired, unstamped.** The output-level exposure study is not worth running as designed: its Stage 1
headline is forced by first-order optimality, its tracking metric fails a trivial negative control, and its
Stage 2 directions are forced by the objectives. Its neighbours (Cao et al., Baldelli et al., Kalai et al.,
the sharpening and RLVR papers) cover the adjacent ground.

**The internal-vs-output variant is narrowed, not open.** Paper III already has an internal entropy axis and a
base/instruct comparison; Simplex (2609.17376) already sees outputs pulled away from internally held beliefs.
Running "does post-training hide or erase internal uncertainty" in Yupana would be a controlled, exact version
of their stated next step. Worth knowing, but the two groups that set it up are faster on it than we are.

**What only Yupana has** is Codex #15 turned into a question: the next-event uncertainty an interface leaves is
two things, transition randomness the world would show any observer and hidden state *this interface*
withholds, and Yupana computes the split exactly and moves it by changing the interface with the hidden
system held fixed. HMM-in-context work fixes the observation channel. The question: **does a learner represent
"the world is random here" differently from "my telemetry hides the state here", and does its output expose the
difference?** That is the founding three-gap story with the interface as the controlled variable.

Next, in order, before any v0.2 is written: (1) per-class exact split of H\* into H(next | S) and observation
gap at k = 7 for the pattern observer (exact side; extends Table 3.0, which is structural-observer, last record);
(2) check that the split varies across classes with comparable H\*, otherwise the question cannot be posed in
this world (cf. §5.1's posterior-shape failure); (3) literature check on aleatoric-vs-epistemic representation
in activations. If (2) fails, the line stops here and the instrument is written up.
