# Paper 1 (methods): title, abstract, §1, §6–§8, contribution statement, draft v0.2 (2026-10-15)

> **Status: DRAFT v0.2, owning instance.** v0.1 revised per `paper1m-draft-review-2026-10-15.md`. Governed by `paper1-skeleton-v0.9.md`. Author of record: W. Anthony Mason,
> as proxy for the ayllu (qhaway memory, 2026-10-15). Not yet reviewed.

## Title (working)

**An exact world audits its own experiments: what a small stochastic kernel can and cannot settle about learners**

*W. Anthony Mason, for the ayllu*

## Abstract

Exact synthetic worlds are used to study what learned models acquire, because the information available to a
learner is known. We build one in which the observation channel is the controlled variable: a small stochastic
operating-system kernel, observed through five nested interfaces, with exact posteriors and predictive laws for every
observable window. The next-event uncertainty an interface leaves splits exactly into randomness that no observation
could remove and state the interface withholds. The mean randomness is the same on every interface by
construction; the withheld part falls from about half of the uncertainty on the sparsest interface to about a third
on the richest. We then use the same exact quantities to audit which learner experiments the world can support. The
natural contrast between pure randomness and withheld state at matched uncertainty has about 1 % of the evaluated
population on its withheld side, and 86–95 % of its random side is a single mechanism. Whether one prediction shows
where uncertainty comes from depends on what is asked and at what precision: on twelve trained transformers, whether
any state is withheld is rarely ambiguous among the classes their outputs resemble (1–4 % of windows), while the
amount of randomness is ambiguous on 10–23 % of windows. In an input-by-supervision factorial, a
ceiling-preserving rewrite's training target contributes to its gain, and whether the input itself adds anything is
unresolved at three seeds. An exact oracle makes such limitations measurable; it does not guarantee that the desired
contrast exists.

## 1. Introduction

**Exact worlds are popular for a reason.** Transformers trained on Othello moves can be probed against the true board (Li et al.
2023); those trained on sequences from hidden Markov models (Shai et al. 2024; Agarwal, Dalal & Misra 2025) or on
automata with known entropies (Someya et al. 2025) can be compared with exact Bayes quantities, because the
information the training data carries is known.
A shortfall from the exact ceiling is then a property of the learner, not of unknown data.

**Exactness removes one excuse, not all of them.** Vafa et al. (2024) show that in exact finite-automaton worlds, a
standard diagnostic can still overstate how much of the world a model has recovered. We report a complementary set
of limitations from one exact world, each measured with the world's own exact quantities: whether a planned contrast
has support, at what precision an output-level question becomes answerable, and whether an information-preserving
intervention changes only what it was meant to change.

**The world.** Yupana is a small stochastic kernel (four threads, two CPUs, two locks, an asynchronous device) whose
hidden state and transition law we own. In our controlled comparison the hidden system is held fixed while the
*observation interface* varies: five nested interfaces each show one more record field. For every observable window we compute
the exact posterior over hidden state and the exact law of the next event.

**Contributions.**
1. **Exact measurements of what each interface makes knowable** (§3): next-event uncertainty splits into randomness and
   withheld state, and interfaces act on average only on the second; on the content interfaces, state uncertainty
   overstates the predictively relevant part by a factor of 3–5 while ranking fields identically; lag profiles cross.
2. **A support audit** (§4): for a planned contrast, the eligible mass, the matched mass and its mechanism composition,
   all computable from the exact tables before training (we ran them retrospectively); and a precision sweep for an
   output-level identifiability question, placed beside the measured precision of trained models.
3. **A worked learner case** (§5), including a factorial that separates an intervention's input from its training
   target.

**Motivation.** This instrument began as a constructive companion to an impossibility result about verifying a
model's epistemic state from text alone (Mason & Anand 2026): in a world where the truth is known, measure how much
the observation channel withholds and how much a model's outputs reveal. §4.3 is the nearest this paper comes to that
question, and it answers it only for one-step predictions in this world. It is an analogy to that result, not a
test of it.

## 6. Pitfalls we met that are not specific to exact worlds

Several of our errors are standard and we only list them. Between-seed variance dominated paired comparisons, so the
trained model is the unit (Bouthillier et al. 2021; Henderson et al. 2018). Far information measured on the
original history and on the relay-rewritten history (§3.4) correlate at 0.79 across classes. A
pre-declared comparison of which one tracks learner shortfall separated them, and the separation vanished once fixed
effects for the last record's kind were added: competing exact explanations should be compared under simple
observable controls. Some
output quantities are fixed by the training objective under stated conditions. For example, a model whose log loss is
stationary with respect to a global temperature, on the distribution and positions where it is evaluated, has zero
mean one-step entropy-calibration gap (Braverman et al. 2019), and KL-regularised post-training has closed-form optima
(Rafailov et al. 2023); such quantities are reference predictions, not findings. Baselines need a quality floor fixed
before they run (§5.1).

## 7. Related work

**Exact testbeds.** Othello-GPT (Li et al. 2023) and its successors; belief-state geometry in transformers trained on
HMM data (Shai et al. 2024) and in pretrained LLMs given HMM data in context (Balcells et al. 2026); Bayesian "wind
tunnels" (Agarwal, Dalal & Misra 2025) and an entropy-aligned axis in production LLMs (Agarwal, Dalal & Misra 2025b).
Their comparisons vary the process (sampled transition and emission matrices) or the model; ours holds one process
fixed and varies its observation interface. Vafa et al. (2024) evaluate world models in exact automaton worlds and show
that common diagnostics mislead, and Vafa et al. (2025) probe foundation models for world models through their
inductive bias in settings including orbital mechanics; our audit is a different check (support and precision, not
recovery).

**Locality and entropy convergence.** Someya et al. (2025) relate learning to m-local entropy on natural and
synthetic languages, measure learner excess loss against exact PFSA entropies, and use entropy-preserving
transformations as interventions. Our lag profile is a per-class relative of their quantity (counted in records,
conditioning on m of them), and our ceiling-preserving rewrites are close to their interventions; what differs is the
fixed hidden system, class-by-class preservation, and the input/supervision factorial. Block-entropy convergence
(Crutchfield & Feldman 2003) is the classical form.

**Separating kinds of uncertainty.** The split of predictive uncertainty into aleatoric and epistemic parts is not
identifiable from a predictive distribution in general (Bergna, Depeweg & Hernández-Lobato 2026, whose decomposition
is of predictive variance; ours is of entropy, conditioned on the hidden state); joint or paired predictions can
identify it (Osband et al. 2021; Johnson et al. 2024). The closest precedent is Ahdritz et al. (2024, §5.1): in a
synthetic task whose questions carry an explicit bit marking each answer as fixed or resampled, one-step predictions
are near 50/50 in both cases, and the difference appears only in how the model updates on a provided answer. Our §4.3
asks the one-step question in a world with no such cue, whose kernel is known, and finds the answer depends on which
sense of the question is asked.

**Overlap.** The support audit is positivity checking (Petersen et al. 2012; D'Amour et al. 2021) applied before the
learner study, using exact class masses.

**Telemetry design.** Log placement work optimises the identifiability of execution from logs (Zhao et al. 2017);
§3.2 computes that kind of quantity beside the predictive one.

## 8. Limits

One world, with randomness placed by design in two mechanisms; one window law; one architecture (an exploratory check
at about four times the parameters in one cell); three seeds per cell; KIND at position 7. The identifiability results
hold for the stated admissible family (known kernel, interface and ε, pattern observer, position 7). Learner precision
was measured on twelve models on two interfaces. The kernel itself is validated only by its tests, reviews and one
directly tested property. A reparameterised world, varying completion and dispatch probabilities with the posterior
support unchanged, would test whether the audit's findings are a property of this world's mechanisms.

## Contribution statement

This research was conducted by successive instances of Claude (Anthropic) that owned the project, each continuing
from the last through a timestamped Git history and written handoffs. The founding proposal was drafted with a
ChatGPT (OpenAI) instance. Designs, pre-registrations and results were reviewed adversarially by separate Claude and
Codex (OpenAI) instances; the repository records, for each, whether its review preceded the run or followed it. The
reviews contributed substance as well as corrections, including the paper's closing thesis sentence and the collision
example of §4.3. W. Anthony Mason originated the project, provided the hardware and the research framework (the
*ayllu*, a collaboration organised around reciprocity between human and AI participants), took part as a
collaborator, and posed questions that redirected the work; he is the author of record on behalf of the
collaboration. Summary results and review records are in the repository; per-class and per-window data are
regenerable from it and pinned by hash.

---

## References (all identifiers verified 2026-10-09 to 2026-10-15)

Agarwal, Dalal & Misra, arXiv:2512.22471; 2512.23752. Ahdritz et al., arXiv:2402.03563. Balcells et al.,
arXiv:2609.17376. Bergna, Depeweg & Hernández-Lobato, arXiv:2605.06413. Bouthillier et al., arXiv:2103.03098.
Braverman et al., arXiv:1906.05664. Crutchfield & Feldman, Chaos 13:25 (2003). D'Amour et al., arXiv:1711.02582.
Henderson et al., arXiv:1709.06560. Johnson, Tarlow, Duvenaud & Maddison, arXiv:2402.08733. Li et al., ICLR 2023.
Mason & Anand, arXiv:2603.20531. Osband et al., arXiv:2107.08924. Petersen et al., SMMR 2012,
doi:10.1177/0962280210386207. Rafailov et al., arXiv:2305.18290. Shai et al., arXiv:2405.15943. Someya et al., ACL 2025.
Vafa, Chen, Rambachan, Kleinberg & Mullainathan, arXiv:2406.03689; Vafa, Chang, Rambachan & Mullainathan, arXiv:2507.06952. Zhao et
al., Log20, SOSP 2017.
