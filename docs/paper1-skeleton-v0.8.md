# Paper 1: skeleton v0.8 (2026-10-15)

> **Status: GOVERNING for paper 1's shape, owning instance. Supersedes v0.7** after both families returned RESHAPE
> (`paper1-skeleton-v0.7-review-2026-10-15.md`). Not yet reviewed itself.

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
| 4 | **A support audit: which contrasts this world can carry.** (a) Far vs no far information: ι = 0 classes take three next-KIND entropy values. (b) Pure randomness vs withheld state at matched H\*: G = 0 classes (15–17 % of mass) take three H\* values, the device coin ~90 % of them; the pure-random vs high-gap contrast covers ~1 % of mass (contrast, bins and pooling stated). Graded split variation at matched H\* is wider (22–54 % of covered mass) but within few mechanisms. (c) One-step identifiability of the split, for the stated admissible family (known kernel, rung, ε, pattern observer, k = 7): determined at exact precision, not at a learner's precision (tolerance table; a declared ball-based check owed). Codex's real-kernel counterexample as a box: identifiability is a property of the reachable posterior family. (d) The audit as a procedure others can run | EXACT |
| 5 | **The learner case.** Within-interface KIND association (robust to FE and clustering, 45/45; ACTOR not robust); count baseline; the relay as an input-by-supervision factorial: unscored copy hurt on KIND, supervision alone helped a little, the copy's increment unresolved at three seeds; the GRU floor | EMPIRICAL (s4 v0.3) |
| 6 | Standard pitfalls we met, one paragraph with citations: seeds and the unit (Bouthillier et al.; Henderson et al.), declared floors, collinear exact regressors and observable controls, objective-implied nulls (Braverman et al.; Rafailov et al.) | compress |
| 7 | Related work | revise |
| 8 | Limits: one world; one architecture and size; three seeds; KIND at k = 7; exact identifiability only at exact precision | revise |

## Owed
1. Declared ball-based tolerance check for 4(c) (replace grid rounding); its threshold fixed before the run.
2. Verify Braverman et al. 2019 (1906.05664, verified earlier), and the home-field ids in `literature-methods-2026-10-15.md`.
3. Two-family review of v0.8 before drafting.
4. Carried: ARIES wording, [check] author lists, status brackets out of body text.

## Cut
"Mechanism sparsity cuts both ways"; the observation-design note; post-training; belief geometry; [PRE-RUN] as a
category; the design chronology (provenance only).
