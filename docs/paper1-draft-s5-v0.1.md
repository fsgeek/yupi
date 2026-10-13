# Paper 1, §5 draft v0.1 (2026-10-13): What output-level comparisons could not settle

> **Status: DRAFT, owning instance. Not reviewed.** Sources are the inventory's section C (reviewed by two
> families on 2026-10-09) and the documents it cites. Overlap and attribution figures were re-read from those
> documents on 2026-10-13. The raws were not recomputed.

## 5. What output-level comparisons could not settle, and the design that would

An exact world removes one excuse for an inconclusive result: the information is known. Four questions still
went unsettled. Each failure was in a design or an estimator, not in the learners, and each one names the study
that would settle it. We report them because the same traps await anyone who measures learners against exact
quantities.

**5.1 Is the cost a step or a slope?** Binned fits suggested that a class costs about the same whatever its far
information, once that information is non-zero. Testing this needs classes with similar posterior shape on both
sides of ι_4 = 0. The world does not supply them. Classes with ι_4 = 0 take only three next-KIND entropy values,
and exact matching on type, mass and entropy bin covers only 26–64 % of the windows with far information. Almost
all of the matched windows are in deterministic classes. *Not identified.* Settling it needs a simulator variant designed so
that posterior shapes overlap across ι_4 = 0.

**5.2 Which far-information measure does the learner track?** Two exact long-range regressors (with and without
an accounting term) correlate at 0.79. A pre-declared horse race between them was passed, and then reversed once
trivial fixed effects for observable classes (the last record's kind) were added. *Not identified.* Settling it
needs regressors that are not collinear by construction, or an intervention that moves one and holds the other.

**5.3 Does the relay help by moving information or by binding it?** We trained three ceiling-holding arms: relay,
decoy and self-copy. The self-copy carries zero entropy, so it cannot absorb any effect that comes simply from a
slot carrying *a variable field*. Under planted rival mechanisms, the pre-registered design attributed the
mechanism wrongly 14–33 % of the time. Three rounds of two-family review blocked it, and the test was not run.
*Not identified by those arms.* Settling it needs a field that varies but carries no information about the
target. Better still, it needs interventions on a *fixed* trained model at evaluation time, such as
counterfactual windows or interchange interventions (Geiger et al. 2021), rather than comparisons between models
trained on different corpora.

**5.4 What is the unit?** Every paired analysis from 30 September to 5 October computed window-level errors on
seed-mean differences. Between-seed variance dominates at 5 epochs: two r1 seeds differ by more than the relay
effect. Re-analysed with the model as the unit, the qualitative findings survived and their stated strengths did
not. This is an analyst error, corrected throughout §4.

**What these have in common.** Every identification attempt compared models trained on different corpora. That
asks what makes a corpus learnable. It does not ask what a fixed model *uses*. Whether outputs under-determine
what a model uses was never tested here. The successor study intervenes on fixed models (§6).

---

## Provenance

- 5.1: `plateau-stratified-results-v0.1.md` (stamped fc05734; "exact matching on type × mass × H bin covers only
  26–64 % of treated windows"); inventory A5 and C1.
- 5.2: inventory C2; `relay-free-difficulty-results-v0.1.md` CORRECTIONS; feedback memory of 2026-10-04 22:52.
- 5.3: inventory C3; `three-arm-prereg-review-2026-10-05.md` (wrong attributions 14–33 % under planted rivals).
- 5.4: inventory C4 and B6; the prereg review §1 and addendum.
