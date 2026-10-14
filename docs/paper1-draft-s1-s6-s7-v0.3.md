# Paper 1: title, abstract, §1, §6 and §7, draft v0.3 (2026-10-13)

> **Status: DRAFT v0.3, owning instance.** It revises the §1/§6 v0.2 text (`paper1-draft-s1-s6-v0.1.md`) after the
> whole-draft review (`paper1-whole-review-2026-10-13.md`: W1, W2, W3, W11, W23, W24, W26), adds §7, and supersedes
> the earlier file. Citations were checked against their sources on 2026-10-09 and 2026-10-13. Two neighbours
> (2512.22471, 2605.20824) were checked from their abstracts only.

## Title (working)

**What the trace makes knowable, and where: exact observability profiles for a small stochastic kernel, with
learners as a measured case**

## Abstract

We build a small stochastic operating-system kernel whose state and transition law we own. We observe it through
five nested interfaces, each showing one more record field. Because the world is finite, we compute, for every
observable window, exact posteriors over hidden state and exact predictive laws for the next event.

**Two results hold exactly:**
- *Most state uncertainty is irrelevant to the next event.* For an observer with structural identities, the
  state uncertainty a window leaves is 3–5 times the part of it that bears on the next record. The ratio is nearly
  constant, so identifiability and prediction rank the fields the same way, and the first overstates the second by
  a stable factor.
- *The lag profile of predictive information differs across interfaces, and can cross.* That is, where in the
  window the knowable information sits, and window-level rewrites can change it with the ceiling held identical
  class by class.

**Small transformers, as a single-configuration case study:**
- Within each content interface, their shortfall from the exact ceiling is higher in classes with more far
  information. This is robust for event kind, and for entity identity only under weaker controls.
- One pre-registered intervention, a near copy of earlier information, factored into its presence and its
  supervision, gives no support to the simple hypothesis that a near copy helps a learned reader.

We also report what output-level comparisons in an exact world could not settle, and why.

## 1. Introduction

**Telemetry is designed for people who debug.** A trace records an event where it happens. Work on log placement
asks which events to record so that a failure can be reconstructed. Log20 (Zhao et al., SOSP 2017) places log
statements to minimise the conditional entropy of the execution path given the log, under an overhead budget. The
figure of merit is identifiability.

**Traces are now also read by learned models**: anomaly detectors, root-cause agents, language models given logs as
context. Such a reader predicts what comes next. Its best achievable loss is a predictive ceiling. That ceiling
includes randomness no record could remove, and it may depend on *where* in the trace the knowable information
sits, not only on how much there is. Whether identifiability is the right figure of merit for such a reader, and
whether placement matters to it, are empirical questions. They are hard to answer on real systems, because there
the information a trace carries is not known exactly.

**We build a world where it is known.** Yupana is a small stochastic kernel: threads, CPUs, locks and an
asynchronous device. It is observed through five nested interfaces. For every window we compute, exactly:
- the posterior over hidden state;
- the predictive law of the next event;
- from these, per interface: state entropy, the predictive ceiling and its irreducible part, and the **lag
  profile**, the predictive information that lies more than m records back.

**What holds by construction, and what we find.** Two properties hold by construction:
- the ceiling falls monotonically as fields are added;
- window-level rewrites leave it unchanged.

What we find:
1. **Most state uncertainty is irrelevant to the next event** (§3.0, structural observer). On the first content
   interface, 0.60 bits of state uncertainty correspond to 0.15 bits of reducible next-event uncertainty. Each
   added field removes 3–5 times more of the first than of the second. That factor is nearly constant, so the two
   measures rank the fields the same way. (The predictive gap is a mutual information with the state, so it can
   never exceed the state entropy.)
2. **Lag profiles cross** (§3.2). A richer field can add information and also relocate information that was already
   available. Interfaces rank differently by ceiling and by distance, and the ranking by distance depends on which
   lags are counted. This is one world, and the crossing is about 0.02 bits.
3. **Learners, as a single-configuration case study** (§4):
   - within each content interface, KIND shortfall is higher where far information is (robust to fixed effects and
     coarse clustering in 45 of 45 models), and training to 15 epochs does not remove the association;
   - the identity association passes its pre-registered test but is not robust to the stronger controls;
   - the transformers beat a count table over the ceiling's own classes on every content interface, and an untuned,
     parameter-matched GRU did not, so it is uninformative by its pre-registered floor.
4. **A near copy, factored** (§4e). With the ceiling held identical, the relay recipe helps: the actor's previous
   event is placed at the point of use *and* is a training target. In no resolved contrast did the copy itself
   help. A pre-registered 2×2 separates the copy's presence from its supervision. On KIND, an
   unscored copy hurts, and supervising the slot without the copy helps a little. Whether the copy helps once
   supervised is not resolved with three seeds. On identity none of these three contrasts resolves. The simple placement hypothesis
   finds no support.
5. **What output-level comparisons could not settle** (§5), with the cause of each failure and candidate designs.

Paper 1's claim is the instrument and what it measures exactly. The learner results are reported at their status,
and none is a general claim about learners or about telemetry design.

## 6. Limits and next studies

**Limits:**
- *Validation scope.* The structural posteriors are validated exhaustively. The frozen-law pattern ceilings are
  validated on a sample of about 91 windows per cell, and class by class only at a smaller law. Nothing validates
  the kernel itself beyond its tests, reviews and one argued property tested at r1.
- *One world and one window law.* The crossing is one example.
- *One architecture, one corpus size, position k = 7 only.* The size axis is thin: d = 256 was checked in one
  cell (r1 ε = 1), where the KIND association holds, and the larger model is under-trained at this recipe.
- *Seeds.* Three per cell; six in two held-out cells. Every relay or 2×2 comparison is three models a side, with a
  paired p floor of 1/8. The 2×2 also carries post-hoc multiplicity: four contrasts × two fields, plus a sum.
- *Budget.* 15 epochs, with validation loss still falling slowly.
- *Baselines.* A smoothed count table. A parameter-matched GRU on the untuned transformer recipe did worse than the
  table in every cell, so it is uninformative by its pre-registered floor. A tuned recurrent baseline is owed.
- *Correlation within cells.* The KIND association controls entropy, frequency and coarse observable classes, and
  remains a correlation.
- *Consumer side only.* The relay rewrites windows a consumer holds. Producer-emitted fields, their overhead, and any
  deployment rule are unmeasured.

**Next studies:**
1. Interventions on fixed trained models: counterfactual windows and interchange interventions.
2. A variable-but-uninformative control field, and a nontrivial auxiliary target that is not the lookup, with more
   paired seeds.
3. A world variant built so that posterior shapes overlap across ι = 0 (§5.1), and a second world for the crossing.
4. Acquisition dynamics: per-checkpoint censuses with at least 8 seeds.
5. Producer-side telemetry: back-reference fields emitted by the kernel, with their emission cost.
6. Exposure: what is accessible in activations against what outputs show (paper 3).

## 7. Related work

**Entropy convergence and locality.**
- The lag profile is a per-class, exact version of a familiar curve. Crutchfield and Feldman (Chaos 13:25, 2003)
  study how block entropies converge to the entropy rate, and what an observer misses when it reads structure as
  randomness. Our ι_m is a per-class KL divergence whose law-mass mean equals the gap between the order-m and
  the full-window predictive entropy, computed for each interface of one system. (Per class, the KL and the entropy
  difference generally differ; only their means agree. Our order m counts *records*. Someya et al.'s m-local
  entropy conditions on m − 1 symbols.)
- In language, the memory–surprisal trade-off (Hahn, Degen and Futrell, Psychological Review 128(4), 2021) and
  information locality (Futrell, "Information-theoretic locality properties of natural language", 2019,
  Quasy/SyntaxFest workshop, ACL Anthology W19-7902; Someya et al., ACL 2025) treat how far back predictive information sits as a
  property that shapes processing and learning. Someya et al. used entropy-preserving transformations, exact
  local entropies on automata, and learner KL against the inherent entropy. We do not claim these methods. We
  differ in the setting: one fixed hidden system whose *observation* is varied, with predictive laws matched class
  by class under intervention, and entity-binding targets.

**Transformers and exact posteriors.**
- Transformers trained on sequences from known generative processes learn hidden state (Li et al., ICLR 2023,
  Othello) and represent belief-state geometry (Shai et al., arXiv:2405.15943; factored representations,
  arXiv:2602.02385).
- Exact posteriors serve as wind tunnels in the Bayesian-geometry series (arXiv:2512.22471). Excess loss over Bayes
  across HMM families appears in arXiv:2605.20824. MetaOthello varies the generator (arXiv:2602.23164).
- As far as their abstracts show, none holds a hidden system fixed and varies the observation interface, which is
  our controlled variable. Our learner half measures outputs only. Belief geometry is left to later work.

**Auxiliary supervision.** Intermediate supervision of sub-tasks can make sequence tasks learnable (Wies, Levine and
Shashua, ICLR 2023). Educated scratchpads help when they break globality (Abbe et al., NeurIPS 2024). The relay 2×2
(§4e) touches this. Supervising the lookup slot helped a little on KIND without the copy, and it cannot be told
apart from other nontrivial auxiliary targets.

**Systems.**
- Log20 (Zhao et al., SOSP 2017) is the identifiability precedent, and Table 3.0 computes its kind of quantity next
  to the predictive one.
- Back-reference fields are a familiar log-design pattern. ARIES records carry the previous log record of the same
  transaction (Mohan et al., TODS 17(1), 1992). The relay is a consumer-side analogue of such a link, copying a value
  rather than holding a pointer.
- Learned log readers (DeepLog, Du et al., CCS 2017; LogBERT, Guo, Yuan and Wu, IJCNN 2021; LLM-based detectors) treat long-range
  dependence as a modelling problem, not as a format choice.
- Interventional and causal-abstraction methods (Geiger, Lu, Icard and Potts, "Causal Abstractions of Neural
  Networks", NeurIPS 2021) are the route §6 names for fixed-model
  studies.

**Text-only supervision.** Mason and Anand prove that for a query answerable in one world and unanswerable in
another, no policy conditioning only on that query can meet both honesty requirements below a tolerance of ½. Their
learnability result requires the supervisor's observations to stay identical throughout training. Yupi is a related
study of interface design, and an analogy, not an instance or a test of their theorem: its learners are scored on
full predictive distributions, which lie outside the text-only observation class. (Their tolerance is unrelated to
our scheduler's ε.)

---

## Citations still to verify before submission

- ~~Futrell, LogBERT, Geiger et al.~~ Checked 2026-10-13. Futrell 2019 is cited by its Anthology id; the venue is
  not confirmed beyond that.
- ARIES PrevLSN: the wording in the paper itself (checked so far only against course material).
- 2512.22471 and 2605.20824: read beyond their abstracts.
- The Linux `sched_switch`, OpenTelemetry and ETW examples are cut from the text until checked against primary
  documentation.
