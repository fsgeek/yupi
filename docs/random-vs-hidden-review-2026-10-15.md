# Random-vs-hidden design v0.1: review record (2026-10-15)

> Reviewed: `random-vs-hidden-design-v0.1.md`. Claude reviewer: **UNSOUND as written**, 11 findings. Codex: in
> progress, to be appended. Owning instance; findings the owner relied on were reproduced by the owner.

## Dispositions, Claude review

| # | finding | disposition |
|---|---|---|
| 1 | **Position 8 does not exist.** WindowLaw(40, 8, 2): n_obs = min(T, L) ≤ 8 records (`window.py` offset = max(0, T − L)); SEQ = 42 = BOS + RESET + 8 × 5. k = 7 already predicts the last record. | **Adopted, reproduced.** The owner designed §2 without checking the window length: the same error as V2/V3 in the exposure prereg (a design written from an assumption about the instrument, not the instrument). Any successor runs at step 6 → 7 → 8 and loses the gate's k = 7 indexing. |
| 2 | **Υ = 0 at G = 0 is false for the full-record x₁.** Independence of KIND and S does not make the record independent of (S, β). Reviewer's kernel check at law (16, 8, 2), k = 5: about 14 % of r1's G = 0 (c, x₁) mass has Υ > 0, up to 0.205 bits at r3, ε = ½ (e.g. which thread is dispatched reveals the state). | Adopted (the owner had flagged it as review question 1, not fixed it). The zero condition is I(X₁; S, β \| c) = 0. |
| 3 | P̃ under-specified: the hidden variable is (S, β); zero-likelihood states force support pruning, so P̃ is not "non-updating"; the prior must be conditioned on continuation; the target is unstated. | Adopted. |
| 4 | **The primary contrast is one mechanism against a sliver.** Of the G = 0, H\* > 0 mass, ~91 % (r1) and 86 % (r3) at ε = 1 sit at H\* = h(1/3) = 0.918, the device-completion coin; ~95 % and 89 % at ε = ½. High-G classes in that bin are 0.4–0.8 % of mass. | **Adopted, reproduced** (0.917 / 0.860 / 0.946 / 0.892). **This also qualifies the feasibility gate:** the "random" side of the matched-H\* variation it found is mostly one mechanism, so the gate's pass shows the split varies, not that it varies across mechanisms. Recorded against the gate result. |
| 5 | φ mixes inherited and update error and rises mechanically with Υ; use U_Q = Υ − KL(P\* ‖ Q); real negative controls are order-m observers and the count table. | Adopted for any successor. |
| 6 | "Not predicted by any objective" is true but empty; the null must be quantitative (ι, mass, H(S \| c), mechanism). | Adopted. |
| 7 | Within an H\* bin R = H\* − G, so "separately" is not a probe target; G/H\* there is nearly a surface-predictable binary; decodability is predicted by Shai et al.; use needs intervention. | Adopted. |
| 8 | Query-class epistemic/aleatoric separation is established (Osband et al. epistemic NNs; Wen et al. joint predictives; Johnson, Tarlow, Duvenaud & Maddison, "Experts Don't Cheat", ICML 2024; Falck et al. 2406.00793). | Adopted; ids to verify before any citation. What stays new: the exact non-updating reference and the interface as the variable. |
| 9 | The operator claim (telling "fix the logging" from "the world is random") is not measured; no cross-rung prediction. | Adopted. |
| 10 | P̃ needs a two-step push with next states, which `ceiling_table` does not keep; re-keying needs an exhaustive gate. | Adopted. |
| 11 | R's interface invariance holds in the mean only. | Adopted; the design's line 75 drops "mean". |

## Owner's reading

The design is withdrawn. Two lessons repeat across today's two designs and paper 1's §5.1:
- **The owner keeps designing from assumptions about the instrument.** V2, V3 and now the window length were all
  checkable in a minute. Rule adopted: before a design note names a position, artifact, field or count, open the
  file that defines it.
- **The world is the binding constraint, not the analysis.** §5.1 could not test a step because classes with
  ι = 0 take three entropy values; today's "random" arm is one coin. A small owned world makes ceilings exact,
  but its mechanisms are few, so learner contrasts at matched exact quantities keep collapsing onto a single
  mechanism. A world variant built so that randomness and hidden state vary independently across several
  mechanisms is the fix both failures name; it is already on paper 1's next-studies list (§6, item 3).
