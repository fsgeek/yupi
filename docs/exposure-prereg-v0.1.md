# Exposure study: pre-declaration v0.1 (2026-10-15)

> **Status: DRAFT v0.1, owning instance (took over 2026-10-14).** Not stamped. It goes to a two-family
> review (Claude, Codex) before any checkpoint is evaluated under it. Stage 1 is a **measurement, not a bet**:
> it fixes a baseline, and its only floor is a validity floor. Stage 2's hypotheses are sketched here and get
> their own pre-registration after Stage 1 has been read, so Stage 1 cannot be tuned to them.
>
> Why this study exists: at the 2026-10-14 handover Tony said Yupi's original intent was to be a world small
> enough to know the distribution, as ground truth for the telemetry claim of Mason & Anand, "Epistemic
> Observability in Language Models" (PACMI '26; arXiv:2603.20531). That paper reads a model's next-token entropy
> (telemetry) as more trustworthy than its self-report (testimony), and reports that post-training lowers entropy
> far more on knowable answers than on fabrications (OLMo-3, base → SFT → DPO → RLVR). Neither claim can be
> checked against a true distribution on natural text. Here it can. This breaks the founding cut, which put
> exposure in paper 3; the reason is recorded in qhaway (2026-10-14 handover memory).
>
> Literature: `literature-exposure-2026-10-15.md` (owner-verified ids: 2605.20824, 2609.17376, 2512.22471,
> 2511.11966, 1906.05664).

## 1. Quantities (exact, per window, KIND at position k)

For a test window w at position k, with exact next-KIND law P\* = P\*(· | class(w)) and the model's
next-KIND distribution Q = Q(· | w) (renormalised over non-PAD, as `evaluate.kind_output`):

- **H\*** = H(P\*): the world's share, what no learner of this interface can remove.
- **H_Q** = H(Q): the telemetry, what a reader of the model's output sees.
- **KL** = KL(P\* ‖ Q): the model's shortfall, its ignorance (`window_excess.kind_kl_bits`, exact given the class).
- **CE** = H\* + KL: the model's exact expected log loss on the next KIND (an identity, used as a gate).
- *Convention (fixed 2026-10-15, before any read):* Q is renormalised over the KINDS. The evaluator's
  `kind_kl_bits` renormalises over non-PAD only and may leave off-KIND mass; it equals KL − log₂(1 − off),
  exactly, and V3 checks it in that form. Off-KIND mass is reported per model.
- **g** = H_Q − CE: the *entropy-calibration gap* (Braverman et al. 2019; Cao, Valiant & Liang 2025).
  g < 0: the model reports less uncertainty than its own expected loss (overconfident). g > 0: more.

So the telemetry splits exactly: **H_Q = H\* + KL + g.** The PACMI reading of entropy is sound for a model to the
extent that H_Q moves with H\* + KL, and it can separate world from ignorance only if H_Q − H\* carries KL.

Why this is not trivial (from the literature pass): near the optimum, H_Q − H\* is first-order in the error of Q,
while KL is second-order, so the two can diverge in sign and size class by class. Agarwal, Dalal & Misra
(arXiv:2512.22471) report |H_Q − H\*| and KL as accuracy scores; they do not study their relation, sign, or
dependence on the observation interface.

## 2. Stage 1: the log-loss baseline (measurement, not a bet)

**Models.** The 30 models of the 15-epoch ladder (`converged-ladder-c3c4-2026-10-02.json`): r0–r4 × ε ∈ {1, ½} ×
seeds 1–3, 2M windows, d = 128, step 117195. No new training. The count-table learner on the same cells
(`count-baseline-*`) is the reference learner whose Q equals P\* on every seen class.

**Windows.** The test split at k = 7 (pattern observer), as in §4 of paper 1. KIND only.

**Reported per model (the model is the unit), law-mass weighted over test windows:**
1. Means of H\*, H_Q, KL, g.
2. Across classes within a model: the weighted correlation of (H_Q − H\*) with KL, and the weighted regression of
   H_Q on H\* and KL jointly (coefficients, with class-clustered intervals for description only).
3. g by H\* bin (deterministic classes H\* = 0; three further bins fixed at the tertiles of H\* over r1 ε = 1
   test classes, computed once and frozen before any model is read) and by KL decile.
4. Per cell: seed range of each of the above. Cells are compared descriptively only.

**Validity floor (stamped now; if it fails, Stage 1 is void, not negative):**
- V1 identity: |H\* + KL − CE_direct| < 10⁻⁹ on every window, where CE_direct = −Σ P\* log₂ Q is computed
  independently.
- V2 reference learner: on the count table, mean KL < 10⁻⁹ and mean |g| < 10⁻⁹ on seen classes (its Q is P\*).
- V3 reproduction: each model's mean of KL − log₂(1 − off) equals the ladder raw's `kind_kl_bits` mean to 10⁻⁹
  (same windows).
- V4 coverage: missing-class count equal to the ladder raw's.

**What Stage 1 is for.** It fixes the log-loss learner's telemetry profile, against which Stage 2 is read. The
owner's prior, written before any read: mean g is small and slightly negative; H_Q − H\* correlates weakly and
positively with KL; telemetry is dominated by H\*. None of this is a test. Stage 1 also answers whether
the 15-epoch models are entropy-calibrated *by interface*, which no prior work has measured exactly.

## 3. Stage 2: post-training in a known world (sketch; its own prereg follows Stage 1)

Start from the Stage 1 checkpoints of r1, r2, r3 at ε = 1 (the cells with entities and distinct lag
profiles), three seeds each. Arms, each run for the same number of optimizer steps:
- **C (control):** continued pretraining with log loss. Separates "more training" from the objective.
- **S (SFT):** cross-entropy on the model's own greedy continuations of training windows (self-distillation to
  argmax; mimics SFT's sharpening).
- **P (preference):** DPO on pairs of sampled next records, where a text-only supervisor prefers the sample
  that matches the realised next record. The supervisor sees sampled text and the realised outcome, never P\*:
  the bounded-supervision setting of Mason & Anand.
- **R (verifiable reward):** policy gradient with reward 1 when the sampled next KIND equals the realised one
  (RLVR-style).

**The question Stage 2 asks.** PACMI observed entropy falling more on knowable answers than on fabrications. In
Yupana, "knowable" splits exactly into two kinds of low-shortfall class: deterministic (H\* = 0) and
aleatoric (H\* > 0, small KL); "unknown to the model" is high KL. The candidate hypotheses to pre-register:
- H2a: S, P and R reduce H_Q on aleatoric classes (destroying honest world-uncertainty telemetry) by more than C.
- H2b: after S, P and R, the correlation of H_Q − H\* with KL is lower than after C (telemetry loses ignorance).
- H2c: P and R raise mean KL (calibrated uncertainty is spent for accuracy on the argmax), measurable exactly.
Floors, seed counts (≥ 5 per arm, given the 2026-10-05 seed-variance lesson) and the decision rule are set in
the Stage 2 prereg.

**Kill criterion for the line of work.** If Stage 1 passes validity and Stage 2's pre-registered contrasts are
uninformative by their own floors, the result is written up as a short report on the instrument and the line
stops. Tony has said that is an acceptable outcome; the owner holds it as a real one.

## 4. Known limits, declared now

- **Log-loss learners are pushed toward calibration by construction.** Stage 1 alone says nothing about
  post-trained LLMs; that is Stage 2's job, and Stage 2's arms are small analogues, not replicas, of
  OLMo-3's pipeline.
- KIND only, position 7 only, one world, d = 128 (the size axis is one cell at d = 256).
- KL is exact given the class; H_Q is the model's at the realised window. Within a class, windows differ only in
  entity names and the model may treat them differently; the class mean is reported, never a single window.

## 5. Code

New, additive, not touching `window_excess` (whose per-window rows earlier verdicts reproduce bit-exactly): a
function computing (H\*, H_Q, KL, CE_direct, g) from `kind_belief` and `kind_output`, tested first, and a script
that runs it over a checkpoint's test windows and writes one raw per model. Registered as a non-measurement
prefix (`exposure-`) in `predictions.py`.
