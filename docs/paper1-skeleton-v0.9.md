# Paper 1: skeleton v0.9 (2026-10-15)

> **Status: GOVERNING for paper 1's shape, owning instance. Supersedes v0.8**, applying both families' DRAFT AFTER
> FIXES findings (`paper1-skeleton-v0.8-review-2026-10-15.md`) and the measured learner-precision result
> (`learner-precision-monitor-check-2026-10-15.md`). Ready to draft.

## Thesis

**An exact oracle makes experimental limitations measurable, but it does not guarantee that the desired contrast
exists.** We build one fixed stochastic kernel observed through five nested interfaces, compute exactly what each
interface lets an observer know and where that knowledge comes from, and then audit, with exact numbers, which
learner questions the world can and cannot support.

**Audience:** builders and users of exact synthetic testbeds for learned models (Vafa et al. 2406.03689 is the
closest: exact worlds where a standard diagnostic still misleads). **Not claimed:** general facts about learners,
telemetry design, or exact testbeds as a class.

## Sections

| § | content | status |
|---|---|---|
| 1 | Exact testbeds; the instrument with the observation channel as the variable; the thesis; position against Vafa et al., Someya et al., Agarwal–Misra, Simplex | to draft |
| 2 | Instrument (compressed s2 v0.3 + Appendix A): world, interfaces, pattern observer, exact quantities and gates, learners | compress |
| 3 | **What each interface lets an observer know, exactly.** (a) H\* = R + G: R's mean is interface-invariant by construction; G falls 0.567 → 0.302 bits (ε = 1), 0.560 → 0.240 (ε = ½): a third of r3's next-KIND uncertainty is withheld state. (b) State vs predictive (Table 3.0): same field ranking, 3–5× scale. (c) Ceiling ladder; lag profiles with the crossing as an illustration; ceiling-holding rewrites | EXACT (s3 v0.4) |
| 4 | **A support audit: which contrasts this world can carry, and at what precision.** (a) *Motivating error:* the withdrawn "plateau" reading (s4 v0.3 §4a) came from an entropy control extrapolating off the support of ι = 0 classes, which take three next-KIND entropy values; an audit run first would have shown it. (b) *Randomness vs withheld state:* the pure-randomness contrast (G = 0, H\* > 0: 15.6 % / 17.2 % of the position-7 population pooled over r1–r3 at ε = 1 / ½, three H\* values, the device coin 89–92 %) against G/H\* ≥ 0.5 in shared floor(H\*/0.05) bins has 0.8–1.4 % support; a graded contrast (within-bin q10–q90 spread of G/H\* ≥ 0.30) has 17–22 % / 36–43 % (exploratory bin statistics; mechanism composition not audited). (c) *Precision:* exact predictions determine the split outside rare collision groups (< 0.05 % of mass; a reachable example on r3, ε = 1: 24 classes with P\* = ⅓ ACQUIRE/IO_COMPLETE/RELEASE and (R, G) of (0.918, 0.667) or (1.585, 0)). Within a TV ball the *amount* of uncertainty blurs first (|ΔG| ≥ 0.1 on 49–69 % at δ = 0.02) while the *kind* holds (|ΔR| ≥ 0.1 on 1.8–2.4 % at ε = 1); by δ = 0.05 the kind blurs too (43–44 %; swaps 18–21 %). (d) *Measured on 12 trained models:* median TV 0.015–0.027; mean prior-weighted ambiguity about R 5–11 %, with 10–23 % of windows ≥ 10 % (BETWEEN by the declared rule in every cell). (e) The audit as a procedure: estimand, matching variables, eligible mass, mechanism composition, admissible posterior family (stated: known kernel, rung, ε, pattern observer, k = 7), precision sweep; inputs and CPU cost (minutes) | EXACT + EMPIRICAL (d) |
| 5 | **The learner case.** Within-interface KIND association (robust to FE and clustering in 45/45 evaluations, not seeds; ACTOR not robust); count baseline; the relay as an input-by-supervision factorial: an unscored copy hurt on KIND; changing the OBJECT-slot target moved KIND shortfall by about as much as other recipe changes (C2 margin 0.0005 bits, not separable from any nontrivial slot target); the copy's increment unresolved at three seeds; ACTOR resolves nothing; the GRU floor | EMPIRICAL (s4 v0.3) |
| 6 | Standard pitfalls we met, one paragraph with citations: seeds and the unit (Bouthillier et al.; Henderson et al.), declared floors, competing exact regressors under observable controls, objective-implied nulls with their conditions (temperature stationarity holds only for the training distribution, positions and normalisation; Braverman et al.; Rafailov et al.) | compress |
| 7 | Related work | revise |
| 8 | Limits: one world; one architecture (an exploratory d = 256 check in one cell); three seeds; KIND at k = 7; identifiability results scoped to the stated admissible family; learner TV measured on 12 models (r1, r3) only | revise |

## Owed
1. Do not let `literature-methods-2026-10-15.md`'s positioning ("cuts both ways") govern §1/§7; it is withdrawn.
2. Reproduce Claude's mass-weighted U variants before citing any of them (the R/G-swap numbers at ε = 1 are reproduced).
3. Carried: ARIES wording, [check] author lists, status brackets out of body text.

## Cut
"Mechanism sparsity cuts both ways"; "not determined at learner precision" (unmeasured premise, superseded by 4(d)); the observation-design note; post-training; belief geometry; [PRE-RUN] as a
category; the design chronology (provenance only).
