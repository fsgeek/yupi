# The bridge to Mason & Anand: draft paragraph (2026-10-09)

> **Status: DRAFT, for cross-family review (skeleton D3′, inventory §F item 5).** Source read:
> `../ai-honesty/arxiv/main.tex`, the abstract (ll. 99–120), Definition "Observation Model" and its remark
> (ll. 300–320), Theorem "Representational Impossibility" and "Connection to identifiability" (ll. 355–410). The
> inventory v0.1 called Yupi's negative results "the impossibility at small scale". That was a category error
> (text-only observation excludes token probabilities; Yupi scores full predictive distributions), and it is
> withdrawn.

## Draft (for paper 1 §1)

> Mason and Anand prove that when an observation model collapses a system's internal state to a response string,
> the map from world states to observations can be many-to-one. Epistemic honesty is then non-identifiable from
> that channel, and no bounded supervisor can verify it. They also note that what a system exports is a design
> choice, not a technological constraint. Yupana takes that choice as its independent variable, in a setting
> where identifiability can be computed rather than argued. Its trace interfaces are observation models of a
> small simulated operating system. For each one, the exact posterior over hidden state measures how far the
> observation is from identifying that state (the observation gap), and the lag profile of the information shows
> where in the trace the identifying information sits. This is a quantitative, exact instance of the
> observational-equivalence notion the theorem invokes. It concerns a simulated system's state, not a model's
> epistemic state, and it neither tests nor extends the theorem. Our learners are scored on full predictive
> distributions, which lie outside the text-only class. So the learner results bear on what a model can learn
> from a trace, not on what a supervisor can verify from text.

## What the paragraph deliberately does not claim

- That Yupi is a "constructive complement" in any sense stronger than the above. CLAUDE.md's founding phrase is
  aspiration. The paper states only the measured relation.
- That any Yupi result supports, illustrates or quantifies epistemic *honesty*.
- That the learner side has anything to say about text-only supervision.
