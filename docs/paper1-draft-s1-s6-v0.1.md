# Paper 1, §1 and §6 drafts v0.2 (2026-10-13)

> **Status: DRAFT, owning instance. Not reviewed.** §1 follows skeleton v0.6, revised in place after the two-family
> review (v0.1 at commit e8e187d). Citations come from the literature passes of 2026-10-09 and 2026-10-13, and the Mason & Anand
> paragraph is the adopted text from `bridge-draft-2026-10-09.md` §0, verbatim.

## 1. Introduction

Systems are instrumented for the people who debug them. A trace records an event where it happens: the scheduler
logs a dispatch when it dispatches, the lock manager logs a release when it releases. Work on log placement asks
*which* events to record so that a failure can be reconstructed afterwards. Log20 (Zhao et al., SOSP 2017) makes
this information-theoretic: it places log statements to minimise the conditional entropy of the execution path
given the log output, under a budget on runtime overhead. The figure of merit is identifiability: how much
uncertainty about the hidden execution the record leaves. A learned reader faces a different quantity. It predicts
what happens next, so its best achievable loss also contains randomness that no record could remove. That predictive
ceiling, and not state identifiability, is what we hold learners against.

More and more traces are now read by learned models: anomaly detectors, root-cause agents, and language models
given logs as context. For such a reader, identifiability may not be the whole story. A human with a debugger can
scroll back. A bounded learner pays, in some way, for where in the stream the knowable information sits. Whether
and how it pays is an empirical question. It is also hard to measure in real systems, because there the
information a trace carries is not known exactly.

We build a world in which it is known. **Yupana** is a small stochastic operating-system kernel (threads, CPUs,
locks, an asynchronous device) whose state and transition law we own. It emits records through five interfaces,
each showing one more field than the last. Because the world is finite, we compute exactly, for every observable
window, the posterior over hidden state and the predictive law of the next event. From these we obtain two exact
quantities per interface:
- the **ceiling**, which is how much an ideal observer can know about the next event;
- the **lag profile**, which is how far back in the window that knowledge sits.

Small transformers trained from scratch on each interface's traces are scored against the ceiling class by class.

**Contributions.**
1. *Exact observability is a profile, not a number* (§3). Richer interfaces lower the ceiling monotonically, but
   their lag profiles cross: a field can add information and also relocate information that was already
   available. Interventions can hold the ceiling identical, class by class, and still change where information
   sits.
2. *Within each content interface, shortfall is higher where far information is* (§4a–§4b). The association
   holds for the next event's kind and for the identity of the entity that acts, on held-out models and at
   convergence, and training longer does not remove it. It is a correlation. The learners beat a count baseline by
   1.3–5.2× per seed (§4d).
3. *A near copy at a fixed ceiling, as a 2×2* (§4e). With the ceiling held identical, three relay models beat three
   controls. Pre-registered follow-ups separate the copy's presence from its supervision. On KIND, an unscored copy
   costs the learner, and supervising the slot without the copy helps a little. The copy's increment once
   supervised is not resolved, and none of this resolves on ACTOR. The simple placement hypothesis finds no support.
   Every comparison is three models a side.
4. *What output-level comparisons could not settle* (§5). These are four questions an exact world still left
   open, each with the design that would settle it, including whether the near copy helps by shortening distance
   or by supplying a binding fact.

**What is not ours.** Someya et al. (ACL 2025) showed, for natural language and random automata, that learned
models do worse when information is less local. They used transformations that preserve global and next-symbol
entropy, computed local entropies exactly on automata, and scored learners by KL against the inherent entropy.
Our ι_m is their m-local entropy less the full-window entropy. We claim neither exact ceilings nor
entropy-preserving relocation as new. What we add:
- a fixed hidden system whose *observation* is the controlled variable;
- predictive laws matched class by class under intervention;
- naming-aware binding targets measured alongside kind;
- within-interface analyses with the model as the unit.
We do not claim the direction of the effect, and our one intervention rejected its proportional form (§4e).

**Relation to the impossibility result.** Mason and Anand prove that, for a query answerable in one world and
unanswerable in another, no policy conditioning only on that query can satisfy both honesty requirements when
ε < ½. Their separate learnability result requires that the supervisor's observations stay identical throughout
training. Yupi is a related study of interface design: under a specified simulator law, it computes exact
posteriors over hidden state, and measures how much predictive information each trace interface carries and at
which lags. This is an analogy, not an instance or a test of their theorem. Yupi's learners are scored on full
predictive distributions, which lie outside the text-only observation class.

## 6. Limits and next studies

**Limits.**
- *The kernel is validated by tests, review and one proved property, not by an independent implementation.* The
  two-path gate validates the filter given the kernel (§2.3).
- *One world, one window law, one model size, three seeds per cell.* At 5 epochs, between-seed variance dominates.
  Every learner claim is per model, and the converged budget is the one we interpret.
- *Position 7 only.* The ceilings and lag profiles cover the 0.85 of window law mass whose windows run at least
  seven records.
- *One baseline.* The count table is a smoothed n-gram over pattern classes. A recurrent baseline might narrow
  the gap.
- *Correlation within cells.* The within-cell law controls entropy and frequency, and is not causal.
- *One intervention, three models a side.* Each 3 vs 3 separation gives p = 0.05 at best. Why an unscored copy
  hurts is not established.

**Next studies.**
1. *Interventions on fixed models.* Counterfactual windows and interchange interventions on trained models, with
   rival mechanisms (distance versus binding) constructed to be behaviourally indistinguishable and then separated
   internally. This is the study §5.3 calls for. Twelve pilot models (r1, r1R, r1D, r1S × three seeds) are trained
   and still unopened.
2. *A pre-specified full-profile locality test.* It needs a variable-but-uninformative control field and a test
   corpus frozen by its bytes.
3. *Acquisition dynamics.* When, during training, does a learner acquire far structure, class by class, against
   exact ceilings? This needs per-checkpoint censuses with at least eight seeds.
4. *The placement exchange rate* (design note `exchange-rate-design-v0.1.md`). What a near copy costs a producer
   in raw emitted bits, and what it buys a learner, per pairing.
5. *Exposure.* What is accessible in a learner's activations, against what its outputs show. Probes exist but lack
   controls, and the question belongs to a later paper.
