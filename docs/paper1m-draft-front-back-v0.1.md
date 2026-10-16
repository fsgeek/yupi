# Paper 1 (methods): title, abstract, §1, §6–§8, contribution statement, draft v0.1 (2026-10-15)

> **Status: DRAFT v0.1, owning instance.** Governed by `paper1-skeleton-v0.9.md`. Author of record: W. Anthony Mason,
> as proxy for the ayllu (qhaway memory, 2026-10-15). Not yet reviewed.

## Title (working)

**An exact world audits its own experiments: what a small stochastic kernel can and cannot settle about learners**

*W. Anthony Mason, for the ayllu*

## Abstract

Exact synthetic worlds are used to study what learned models acquire, because the information available to a
learner is known. We build one in which the observation channel is the controlled variable: a small stochastic
operating-system kernel, observed through five nested interfaces, with exact posteriors and predictive laws for every
observable window. Exactly, the uncertainty an interface leaves about the next event splits into randomness that no
observation could remove and state the interface withholds; interfaces differ only in the second, which falls from
half of the next-event uncertainty on the sparsest interface to a third on the richest. We then use the same exact
quantities to audit which learner experiments the world can support. The natural contrast between pure randomness and
withheld state has under 1.5 % of the evaluated population on its matched side, and most of the other side is a single
mechanism. Whether one prediction reveals which kind of uncertainty a model faces depends on precision: the split is
determined by exact predictions outside rare collisions, the amount of uncertainty blurs before its kind under small
perturbations, and twelve trained transformers sit near the boundary, with the kind ambiguous on a minority of
windows.
A ceiling-preserving input rewrite that helped learners turns out, in a factorial follow-up, to act through what the
learner is trained to produce. An exact oracle makes these limitations measurable before training; it does not
guarantee that the desired contrast exists.

## 1. Introduction

**Exact worlds are popular for a reason.** Transformers trained on Othello moves (Li et al. 2023), on sequences from
hidden Markov models (Shai et al. 2024; Agarwal, Dalal & Misra 2025), or on automata with known entropies (Someya et
al. 2025) can be compared with exact Bayes quantities, because the information the training data carries is known.
A shortfall from the exact ceiling is then a property of the learner, not of unknown data.

**Exactness removes one excuse, not all of them.** Vafa et al. (2024) show that in exact finite-automaton worlds, a
standard diagnostic can still overstate how much of the world a model has recovered. We report a complementary set
of limitations from one exact world, each measured with the world's own exact quantities: whether a planned contrast
has support, at what precision an output-level question becomes answerable, and whether an information-preserving
intervention changes only what it was meant to change.

**The world.** Yupana is a small stochastic kernel (four threads, two CPUs, two locks, an asynchronous device) whose
hidden state and transition law we own. Unlike HMM testbeds, the hidden system is held fixed while the *observation
interface* varies: five nested interfaces each show one more record field. For every observable window we compute
the exact posterior over hidden state and the exact law of the next event.

**Contributions.**
1. **Exact measurements of what each interface makes knowable** (§3): next-event uncertainty splits into randomness and
   withheld state, and interfaces act only on the second on average; state uncertainty overstates the predictively
   relevant part by a stable factor of 3–5 while ranking fields identically; lag profiles cross.
2. **A support audit** (§4): for a planned contrast, the eligible mass, the matched mass and its mechanism composition,
   computed exactly before training; and a precision sweep for an output-level identifiability question, placed beside
   the measured precision of trained models.
3. **A worked learner case** (§5), including a factorial that separates an intervention's input from its training
   target.

**Motivation.** This instrument began as a constructive companion to an impossibility result about verifying a
model's epistemic state from text alone (Mason & Anand 2026): in a world where the truth is known, measure how much
the observation channel withholds and how much a model's outputs reveal. §4.3 is the nearest this paper comes to that
question, and it answers it only for one-step predictions in this world.

## 6. Pitfalls we met that are not specific to exact worlds

Several of our errors are standard and we only list them. Between-seed variance dominated paired comparisons, so the
trained model is the unit (Bouthillier et al. 2021; Henderson et al. 2018). Two exact far-information regressors,
correlated at 0.79, separated under a pre-declared comparison and lost that separation once fixed effects for the last
record's kind were added: competing exact explanations should be compared under simple observable controls. Some
output quantities are fixed by the training objective under stated conditions. For example, a model whose log loss is
stationary with respect to a global temperature, on the distribution and positions where it is evaluated, has zero
mean one-step entropy-calibration gap (Braverman et al. 2019), and KL-regularised post-training has closed-form optima
(Rafailov et al. 2023); such quantities are reference predictions, not findings. Baselines need a quality floor fixed
before they run (§5.1).

## 7. Related work

**Exact testbeds.** Othello-GPT (Li et al. 2023) and its successors; belief-state geometry in transformers trained on
HMM data (Shai et al. 2024) and in pretrained LLMs given HMM data in context (Balcells et al. 2026); Bayesian "wind
tunnels" (Agarwal, Dalal & Misra 2025) and an entropy-aligned axis in production LLMs (Agarwal, Dalal & Misra 2025b).
These hold the observation channel fixed and vary the process or the model. Vafa et al. (2024; 2025) evaluate world
models in exact automaton worlds and show that common diagnostics mislead; our audit is a different check (support and
precision, not recovery).

**Locality and entropy convergence.** Our lag profile is the m-local entropy of Someya et al. (2025) less the
full-window entropy, computed per class for each interface of one system; block-entropy convergence (Crutchfield &
Feldman 2003) is its classical form.

**Separating kinds of uncertainty.** The split of predictive uncertainty into aleatoric and epistemic parts is not
identifiable from a predictive distribution in general (Bergna, Depeweg & Hernández-Lobato 2026); joint or paired
predictions can identify it (Osband et al. 2021; Johnson et al. 2024), and synthetic tasks have contrasted fixed and
randomised hidden answers (Ahdritz et al. 2024, §5.1) [to verify from the full text]. Our §4.3 asks the one-step question inside a world whose kernel is
known, where structure can restore identification, and finds that it does so only at high precision.

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
from the last through a timestamped repository and written handoffs. Designs, pre-registrations and results were
reviewed adversarially by separate Claude and Codex (OpenAI) instances; the repository records, for each, whether
its review preceded the run or followed it. W. Anthony Mason
originated the project, provided the hardware and the research framework, took part as a collaborator, and posed
questions that redirected the work; he is the author of record on behalf of the collaboration. Every commit is
OpenTimestamps-stamped; the review records, retractions and raw data are in the repository.

---

## References (all identifiers verified 2026-10-09 to 2026-10-15; full list to be assembled)

Agarwal, Dalal & Misra, arXiv:2512.22471; 2512.23752. Ahdritz et al., arXiv:2402.03563. Balcells et al.,
arXiv:2609.17376. Bergna, Depeweg & Hernández-Lobato, arXiv:2605.06413. Bouthillier et al., arXiv:2103.03098.
Braverman et al., arXiv:1906.05664. Crutchfield & Feldman, Chaos 13:25 (2003). D'Amour et al., arXiv:1711.02582.
Henderson et al., arXiv:1709.06560. Johnson, Tarlow, Duvenaud & Maddison, arXiv:2402.08733. Li et al., ICLR 2023.
Mason & Anand, arXiv:2603.20531. Osband et al., arXiv:2107.08924. Petersen et al., SMMR 2012,
doi:10.1177/0962280210386207. Rafailov et al., arXiv:2305.18290. Shai et al., arXiv:2405.15943. Someya et al., ACL 2025.
Vafa, Chen, Rambachan & Kleinberg, arXiv:2406.03689; Vafa, Chang, Rambachan & Mullainathan, arXiv:2507.06952. Zhao et
al., Log20, SOSP 2017.
