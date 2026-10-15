# Paper 1: skeleton v0.7 (2026-10-15), the methods paper

> **Status: GOVERNING DRAFT for paper 1's shape, owning instance (from 2026-10-14). Supersedes v0.6** (kept, with its
> 2026-10-15 addendum). Not yet reviewed. The re-aim and its reasons: the Oct 15 HANDOFF memory;
> `exposure-prereg-review-2026-10-15.md`; `random-vs-hidden-review-2026-10-15.md`;
> `one-step-identifiability-check-2026-10-15.md`.

## Audience and claim

**Audience:** people who build exact synthetic worlds to make claims about learners (Othello-GPT and MetaOthello;
HMM "wind tunnels" (Agarwal, Dalal & Misra); belief-state geometry (Shai et al.; Balcells et al.); PCFG and automaton
locality studies (Someya et al.)). Such worlds are usually justified by exactness: the information available is
known, so a learner's shortfall can be read cleanly.

**Claim:** exactness removes one excuse, unknown information, and leaves the others. We built an exact world whose
*observation channel* is the controlled variable and report:
1. what it settles exactly;
2. what it could not settle, each with its cause, demonstrated with numbers from the same world;
3. one property that runs through several of the failures: **mechanism sparsity cuts both ways.** A world small
   enough for exact posteriors has few stochastic mechanisms. That makes the *source* of uncertainty readable from
   one prediction, so a general impossibility result does not bind inside it. It also leaves learner contrasts
   between sources with almost no overlapping support;
4. checks a builder can run before designing a learner contrast.

**Not claimed:** anything general about learners, telemetry design, or epistemic honesty. Mason & Anand
(arXiv:2603.20531) is motivation, not a result tested here.

## Evidence status, kept visible in the text

- [EXACT]: computed on the full world and validated (§2.3 gates).
- [EMPIRICAL]: trained models, at stated seeds and status (confirmatory or exploratory).
- [PRE-RUN]: a design that two-family review stopped before it ran, with the reason. These are arguments made
  concrete with this world's numbers, not experiments, and are labelled as such everywhere.

## Sections

| § | content | source | status |
|---|---|---|---|
| 1 | Exact testbeds and what they are assumed to buy; our instrument; the four contributions | new | to draft |
| 2 | The instrument, compressed: world, five nested interfaces, pattern observer, exact quantities and gates, learners | s2 v0.3, Appendix A | compress |
| 3 | **What exactness settles.** Ceiling ladder; state vs predictive (Table 3.0); H\* = R + G with R's mean interface-invariant and interfaces acting only through G; lag profiles (one figure, the crossing as illustration); ceiling-holding rewrites | s3 v0.4 | EXACT; trim lag detail |
| 4 | **What it could not settle, by cause** (the centre) | s5 v0.4 + review records | see below |
| 5 | The learner case as a worked example: KIND association (robust), ACTOR (not), count baseline, the relay 2×2, the GRU floor | s4 v0.3, shrunk to ~1 page | EMPIRICAL |
| 6 | A checklist for builders | new | to draft |
| 7 | Related work | s1-s6-s7 v0.3 §7, re-aimed | revise |
| 8 | Limits | s1-s6-s7 v0.3 §6 | revise |

### §4, by cause

- **4.1 Forced by construction** [PRE-RUN, derivations EXACT]:
  - a log-loss learner's mean one-step entropy-calibration gap is ≈ 0 by first-order optimality (dCE/dβ at β = 1 is
    −g for Q_β ∝ Q^β);
  - post-training directions (SFT on greedy outputs, outcome-matching DPO, RLVR) follow from the objectives'
    closed-form optima;
  - a context-free uniform Q makes the "entropy tracks ignorance" correlation exactly 1.
  Lesson: derive what the objective forces before measuring outputs.
- **4.2 Mechanism sparsity, the learner edge** [EXACT]:
  - classes with no far information take three next-KIND entropy values (§5.1 v0.3);
  - classes with no hidden-state uncertainty take three H\* values per ε, the device coin holding ~90 % of their
    mass; matched random-vs-hidden contrasts cover ~1 % of mass.
  Lesson: count the mechanisms on both sides of a contrast (overlap, in causal-inference terms) before designing it.
- **4.3 Mechanism sparsity, the monitor edge** [EXACT]: with the kernel known, the one-step predictive determines the
  random/hidden split on all but < 0.05 % of mass, although the split is not identifiable in general (Bergna et al.,
  arXiv:2605.06413). Lesson: a general impossibility result has to be checked inside the world before it is
  cited as holding there; and a world's structure can make such questions too easy.
- **4.4 Collinear exact regressors** [EMPIRICAL]: two exact far-information measures correlate 0.79; a pre-declared
  comparison separated them until last-kind fixed effects were added (§5.2 v0.3).
- **4.5 The unit** [EMPIRICAL]: between-seed variance dominates paired learner comparisons; window-level errors on
  seed means overstated every effect (§5.4 v0.3).
- **4.6 Interventions change input and target together** [EMPIRICAL]: the relay helped only as a training target;
  the 2×2 separates presence from supervision (§4e v0.3, §5.3 v0.3).
- **4.7 Floors declared in advance** [EMPIRICAL]: the GRU produced large positive statistics from models worse than a
  count table; only the stamped floor kept them from being read as support.

### §6, the checklist (draft items)

1. Derive what the training objective forces on the quantity you will measure.
2. Count mechanisms on both sides of every contrast; report the overlapping mass.
3. Check any general theorem you cite inside your world.
4. Make the trained model the unit; size seeds from a pilot's between-seed variance.
5. Declare what result is uninformative, for each baseline and test, before running.
6. In an intervention, separate what the learner sees from what it is trained to produce.
7. Verify instrument facts (window length, stored fields, estimators) from their definitions before a design names
   them.

## Owed before drafting

1. **Literature: is this lesson set known for synthetic testbeds?** Search methods critiques of toy-model and
   synthetic-benchmark studies; seed variance (e.g. Bouthillier et al., "Accounting for Variance in ML
   Benchmarks"; Henderson et al., "Deep RL That Matters"); positivity/overlap. Verify every id. The individual
   lessons are known in other fields; the claim is that they bite in exact worlds, where exactness is taken to
   remove them. If a paper already makes that claim, the paper narrows.
2. Verify reviewer-cited ids not yet checked: Johnson et al. "Experts Don't Cheat" (ICML 2024); Falck et al.
   2406.00793; Chung et al. 2606.19353; CATTO 2601.23096; Osband et al. epistemic neural networks.
3. A two-family review of this skeleton, asking specifically whether the audience would find the contribution
   new and useful, and whether [PRE-RUN] items belong in a paper.
4. Carried from v0.6: ARIES wording, [check] author lists, status brackets out of body text.

## Cut

The observation-design note (its central claim is false in this world); post-training experiments; belief geometry;
any telemetry-design recommendation.
