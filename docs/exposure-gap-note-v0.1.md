# The Exposure Gap, Relative to a Query Class

**Working note v0.1 — 2026-08-11. Exploratory; definitions proposed, not settled. Stamped to establish the formulation date, not to freeze the content.**

## 1. The problem this note repairs

Proposal v0.2 defines the exposure/use gap informally as "information present internally but absent from, or causally unused by, the immediate output distribution." CLAUDE.md flags the defect: measured against immediate logits alone the gap is trivially large by data processing, and measured against the model's full output law it threatens to be trivially small. The gap is only meaningful *relative to what an observer of the output is permitted to do*. This note makes that relativization explicit, and in doing so makes the whole three-gap decomposition uniform.

Two recent results bracket the problem and confirm it is real rather than pedantic:

- **Immediate logits are provably lossy.** Distinct posteriors can share identical predictive means, so no immediate next-token query distinguishes them (Aswadi, Ma & Wei, arXiv:2607.17060, Fig. 2; independently, Dalal et al.'s mixture inversion works only at hand-picked positions where the inversion is unambiguous, arXiv:2607.19379).
- **Unbounded continuation queries are complete — but only under idealizations.** Under exchangeability-type (c.i.d.) conditions, infinite autoregressive rollouts recover the entire implicit posterior (2607.17060); trained models empirically violate those conditions, and for Markov-exchangeable data no relaxed theory exists at all.

Between these bookends — a single lossy query and an idealized complete one — lies a lattice nobody has defined. The exposure gap lives on that lattice.

## 2. One schema, four observers

Fix the pipeline X_t → h_t → A_t → output, where X_t is Yupana's hidden state, h_t the visible trace under interface I and context L, A_t the model's activations, and the output interface is the model's conditional law over continuations. Fix a latent target Z_t = f(X_t) with prior uncertainty H(Z_t).

Every quantity below is an instance of one schema: **the information about Z_t recoverable by an observer with restricted access**, in the sense of predictive V-information (Xu et al., arXiv:2002.10689): I_V(S → Z) = H(Z) − inf over the allowed decoder/measurement family of achievable cross-entropy on Z given access S. Restricting the family is what keeps every term computable, finite-sample estimable, and immune to the "sufficiently powerful decoder learns the task" objection — the same repair, applied at every stage.

The four observers:

- **O₀ — the trace-Bayes observer.** Access: h_t. Family: unrestricted (exact Bayes; computable in Yupana). Recovers I₀ = H(Z_t) − H(Z_t | h_t).
- **O₁ — the probe observer.** Access: A_t. Family V: constrained probes (linear / MDL-bounded, per proposal §3.4.2). Recovers I₁ = I_V(A_t → Z_t).
- **O₂ — the query observer.** Access: the model's *output distributions* under a query class Q (defined in §3). Recovers I₂ = I_Q(Z_t).
- **O₃ — the sampling observer.** Access: only *sampled tokens* from those same output distributions, under the same continuation budget. Recovers I₃.

The decomposition is then a telescope of adjacent differences:

| Gap | Definition | Attribution |
|---|---|---|
| Observation gap | H(Z_t \| h_t) = H(Z_t) − I₀ | the interface designer (the teacher) |
| Accessible representation gap | I₀ − I₁ | the learner's internal organization |
| **Exposure gap (this note)** | **G(Q) = I₁ − I₂(Q)** | the learner's output interface, relative to observer power Q |
| Sampling gap | S(Q) = I₂(Q) − I₃(Q) | the logits→tokens channel |

Each term is nonnegative up to estimation error when the access sets are nested in the natural way; each is exactly computable in Yupana because H(Z_t | h_t) is exact and the restricted infima are over finite, enumerable measurement families. The symmetry worth stating plainly: **the query class Q does for the output side exactly what the probe family V does for the representation side.** Gap 2 and gap 3 are the same kind of object — restricted-observer information differences — at adjacent pipeline stages. The decomposition is a chain of students, each sitting the exam set by the stage before.

## 3. Query classes

A query q is a pair (c, g): a continuation protocol c (a family of prompt extensions and a rollout budget — depth N, number of rollouts R, adaptive or fixed) and a functional g mapping the resulting output distributions (O₂) or samples (O₃) to a prediction about Z_t. A query class Q is a set of such pairs; the observer may use the best decoder over Q.

Natural axes of the lattice:

- **Depth:** N = 0 (immediate logits only) → finite N → unbounded.
- **Breadth:** single continuation vs. families of counterfactual continuations (the "what would you say if…" axis — this is where interrogation-style probing lives).
- **Adaptivity:** fixed protocol vs. queries chosen as a function of earlier answers.
- **Channel:** distributions (logits) vs. samples, at matched budget — the O₂/O₃ split.
- **Functional family:** unrestricted vs. bounded-complexity g (mirroring MDL probes).

Partial order: Q ⊑ Q′ iff every measurement in Q is realizable in Q′. Immediate consequences: I₂ is monotone and G antitone along ⊑; the published bookends become the lattice's floor (Q_logit = {(N=0, id)}: G provably positive) and idealized ceiling (Q_∞ under c.i.d.: G → 0). The object of empirical interest is the **exposure profile** — G as a function on the lattice — and where trained models' profiles depart from the idealized ceiling. Existing methods are points on this lattice: predictive Monte Carlo (2607.17060) is deep-N, fixed-functional, distribution-channel; mixture inversion (2607.19379) is N=0 at selected positions; verbalized report (their CoT probe) is a sample-channel query — and their observed dissociation (logits 98.7% correct vs. verbalized answers near chance) is, in this vocabulary, a measured sampling gap S(Q) ≫ 0.

## 4. What this definition buys

1. **Non-triviality without arbitrariness.** The DPI objection dissolves: G is large or small *relative to a declared observer*, and claims are indexed by Q the way statistical claims are indexed by a test.
2. **Applicability where representation theorems fail.** Nothing here requires exchangeability. Z_t is defined by the world, not as a path functional of model rollouts; Yupana's non-stationary episodic processes are in scope — precisely the territory 2607.17060 concedes has no theory.
3. **Exact calibration.** In Yupana every term has a computable ground truth, so query-restricted recovery methods (PMC-style) can be calibrated against exact posteriors — a validity check unavailable in the wild, where such methods' sufficient conditions are admittedly untestable.
4. **The fourth gap becomes measurable.** S(Q) is defined at matched budget, turning the logits-vs-verbalization dissociation from an anecdote into a curve.
5. **The bridge to the impossibility result.** Epistemic Observability in Language Models (arXiv:2603.20531) can be restated in this vocabulary: for certain epistemic targets Z, under bounded supervision the infimum of G(Q) + S(Q) over *feasible* text-channel query classes remains bounded away from zero. The theorem asserts a floor on the exposure profile; Yupi measures the profile. Same object, two ends.

## 5. Distinctions deliberately preserved

- **Exposure ≠ causal use.** G(Q) is observational. The causal-use question — does the internally represented distinction *drive* downstream predictions — remains as defined in proposal §8.5 (patching between matched histories), unchanged by this note. A distinction can be exposed but epiphenomenal, or used but unexposed; the 2×2 is the interesting object for paper 3.
- **Relation to Dalla Riva (arXiv:2604.05469).** His Δ (behavioral-partition excess) + Γ (decoder-class gap) decompose what is here I₀ − I₂ territory, with an oracle-conditioned floor and no observation channel; his Def. 39 decoder-class move is the same repair as §3's functional-family axis, made on the decoding side. Where his framework and this one overlap they should agree; establishing that formally is open work below.

## 6. Open problems (v0.2 targets)

1. Canonical query lattices: which finite Q are *reportable standards* (the "linear probe" equivalents of the output side)?
2. Finite-sample estimators for I₂ with adaptive queries; budget accounting so R·N appears in the claim.
3. Conditions on the world/model under which G(Q) is monotone during training (does exposure lag representation?— H6 predicts yes).
4. Formal correspondence with Dalla Riva's (Δ, Γ) in the degenerate full-observability case.
5. Whether the impossibility result's assumptions map cleanly onto a feasibility predicate over the lattice (candidate: polynomially-bounded adaptive sample-channel queries).

## References

Aswadi, Ma & Wei, arXiv:2607.17060 · Dalal, Misra & Parekh, arXiv:2607.19379 · Agarwal, Dalal & Misra, arXiv:2512.22471 · Dalla Riva, arXiv:2604.05469 · Xu et al., arXiv:2002.10689 · Shai et al., arXiv:2405.15943 · Mason & Anand, arXiv:2603.20531 · "Abdullah X", arXiv:2605.20824.
