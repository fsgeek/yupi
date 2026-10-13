# Paper 1: skeleton v0.6 (2026-10-13)

> **Status: GOVERNING for paper 1's shape. Supersedes v0.5.** Written after the two-family adversarial review of
> the §2–§4 drafts (dispositions in `paper1-review-2026-10-13.md`). Both reviewers, working independently, said
> the earned result is the exact side, and that the learner half is a measured case with one exploratory
> intervention. This skeleton adopts that. Owning instance.

## The centre

**In one hidden system small enough to count, we vary only how it is observed. We measure exactly two things for
each interface: how much it lets an observer know about what happens next (the ceiling, a Bayes predictive loss),
and where in the window that knowledge sits (the lag profile).** The two come apart:
- interfaces ranked by ceiling are not ranked the same way at a given lag;
- the lag profiles of richer and poorer interfaces cross;
- the presentation can be changed with the ceiling held identical class by class.

This is the paper's result, and it is exact (§3).

**Small transformers are a measured case** (§4):
- Within each content interface, a converged learner's shortfall from the ceiling is higher in classes with more
  far information. This holds for event kind and for entity identity, on held-out models. It is correlational and
  confirmatory, and it survives class-clustered errors.
- Training longer does not remove that association (confirmatory).
- The learners beat a count table over the ceiling's own classes by 1.3–5.2× per seed (exploratory).
- No cross-interface ordering is claimed, since a seed-resolved counterexample exists.

**One intervention, exploratory.** With the ceiling held identical, three relay models beat three controls,
which is complete separation (exact p = 0.05). The design leaves three mechanisms unseparated: distance, binding
content, and auxiliary supervision (the relay value is itself a training target). A pre-registered loss-masked arm
tests the third, and §4e is written to its reading.

**What is ours and what is not.** Someya et al. (ACL 2025) used entropy-preserving transformations, exact PFSA
local entropies, and learner KL against the inherent entropy. Our ι_m is their m-local entropy less the
full-window entropy. So we do not claim exact ceilings or entropy-preserving relocation as new. We claim:
- one *fixed* hidden system observed through several interfaces, as a controlled variable;
- predictive laws matched class by class under intervention;
- naming-aware entity targets (binding), measured alongside kind;
- within-interface analyses with the model as the unit;
- the systems framing: Log20's identifiability objective (SOSP '17) priced against a learned consumer.

**Producer and consumer locality: motivation only.** Traces are written where activity happens, and learned
consumers may pay for where information sits. That is the hypothesis the instrument is built to test, and paper 1
does not establish it. The relay is a consumer-side transformation of a window. Back-reference fields are a
familiar log-design pattern, for example:
- per-transaction previous-record links (ARIES prevLSN);
- the scheduler's previous-task state on a context switch (Linux `sched_switch`);
- parent and related activity identifiers in tracing (OpenTelemetry, ETW).
These are candidate citations, to be verified before use. §1 frames the relay as pricing that familiar
denormalization for a learned reader, not as a new principle.

## Sections

| § | content | status |
|---|---|---|
| 1 | Telemetry for debuggers vs learned readers; Log20; Someya; the adopted Mason & Anand analogy paragraph | as reviewed |
| 2 | Instrument: world, window law, rungs, naming, pattern observer, shared-kernel gate limit, structural-observer injectivity (scoped), window-level rungs, learners, estimator, model as unit | exact / method |
| 3 | Ceiling as Bayes predictive loss; ladder; lag profile = m-local entropy minus ceiling; crossing; ceiling-holding rungs; one cross-interface pair and its counterexample | **exact: the result** |
| 4a | Within-cell association, KIND and actor, r1–r4 | confirmatory (correlational) |
| 4b | Convergence does not remove it; the "no more than" clause failed and is reported | confirmatory / failure reported |
| 4c | No cross-interface claim (see §3.4) | — |
| 4d | Count baseline | exploratory |
| 4e | Relay: 3 vs 3 separation, the Δι_4 pricing rejected, three rival mechanisms, the loss-masked arm | exploratory, plus pre-registered arm |
| 5 | What output-level comparisons could not settle, and the designs that would | negative, as method |
| 6 | Limits; next studies (fixed-model interventions, full-profile locality test, acquisition dynamics, exchange rate, exposure) | — |

## Owed before external review

1. The loss-masked relay arm, scored to its pre-registration.
2. ~~The fixed-effects and coarse-cluster robustness check across all cells.~~ Done 2026-10-13: 45/45 keep t ≥ 3.
3. ~~The raw per-model bins.~~ Done 2026-10-13: monotone above 0.001 in 45/45. Figure: `figures/b1-raw-bins-2026-10-13.png`.
4. The back-reference citations verified, and Log20's measure read from its full text.
5. A whole-draft second review by both families.

## Cut (unchanged)

Belief geometry; the three-arm test; any mechanism claim; any claim about epistemic honesty or text-only
supervision; "the learner builds its own index".
