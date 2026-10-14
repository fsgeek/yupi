# Paper 1, §2 draft v0.3 (2026-10-13): The instrument

> **Status: DRAFT v0.3, owning instance.** Written from skeleton v0.6. It revises v0.2 (`paper1-draft-s2-v0.1.md`)
> after the whole-draft two-family review (`paper1-whole-review-2026-10-13.md`: W4–W8, W11–W13, W19, W26), which it
> supersedes. Every value was read from code or a named raw. Claim status is given in square brackets.

## 2. The instrument

### 2.1 The world

Yupana is a small stochastic operating-system kernel whose state and transition law we own.
- **Configuration:** four threads, two CPUs, two locks and one asynchronous device; a request pool of four, a device
  queue of depth two, and completion probability 1/3 per step.
- **Programs:** each thread runs a fixed looping program, giving four contention roles:
  - thread 0: acquire lock 0, release it, issue I/O;
  - thread 1: take lock 0 then lock 1, and release both in reverse order;
  - thread 2: compute, then take and release lock 0;
  - thread 3: issue I/O, then take and release lock 1.
- **Scheduler:** round-robin with probability 1 − ε, and uniform over runnable threads with probability ε. The base
  condition is ε = 1, and we also report ε = ½.

The kernel makes two kinds of random choice: which thread runs next, and whether the device completes on a step.
Each choice is labelled in the next record by its kind and actor. The *future* therefore stays random however much
is observed, and a predictive ceiling (§2.3) includes that irreducible part.

**The window law (40, 8, 2)**, frozen before any learner was trained:
- an episode runs 40 records from reset;
- an endpoint T is drawn uniformly from {2, 4, …, 40};
- the observer sees the last 8 records ending at T;
- a window that reaches back to the reset begins with a RESET token.

### 2.2 Interfaces

Every record has five fields: KIND, ACTOR, OBJECT, RELATED and LINEAGE. A rung shows some fields and renders the rest
as a placeholder token, so every record is exactly five tokens on every rung. A lag of m records is therefore a lag
of 5m tokens everywhere.

| rung | shows |
|---|---|
| r0 | KIND |
| r1 | + ACTOR |
| r2 | + OBJECT (which lock or device) |
| r3 | + RELATED (the thread woken, or the owner) |
| r4 | + LINEAGE (the request identifier) |

Before any learner existed, each added field was shown to change some posterior or some finite-horizon predictive
distribution. [EXACT; a design requirement of the milestone specification]

**Names carry no identity across episodes.** Entities are named per episode by a keyed injection from pools much
larger than the entity counts: 64 thread names for 4 threads, 32 lock names for 2 locks, 16 device names and 32
request names. Training corpora draw from 56, 28, 14 and 28 of these. The rest are reserved for held-out-binding
tests, which paper 1 does not use.

### 2.3 Exact quantities, for stated observers, and how each is validated

Two observers appear:
- **The structural observer** sees structural entity identities. It is used for state uncertainty and its
  decomposition (§3.1, Table 3.0).
- **The pattern observer** sees the window with every entity renamed by order of first appearance, so that only the
  pattern of who recurs remains. Names are re-drawn every episode, so this is the learner's comparison point. Every
  ceiling, lag profile and shortfall in §3–§4 (except Table 3.0) is for the pattern observer at window position k = 7: after seven
  records, predicting the eighth. Position k = 7 covers the windows that run at least seven records, which is 0.85
  of window law mass. Its averages are normalised over that mass.

The **ceiling** for a target is the law-mass-weighted entropy of the exact predictive law of that target, given the
pattern class: a Bayes predictive loss. Each computed quantity is validated in its own way:

| quantity | how it is validated | coverage |
|---|---|---|
| structural window posteriors | the filtering recursion agrees with an independent path summation, with zero mismatches | **exhaustive**, 8,542,940 windows, all ten (rung, ε) |
| pattern-class ceilings P\*(next \| pattern class) | they agree exactly with an independent pattern filter | **exhaustive class by class** at the small law (8, 4, 2); at the frozen law, **a random sample** of 82–91 test windows per (rung, ε), all exactly equal |
| the lag identity ι_m = H_m − H\* | the KL route and the entropy route agree | every row, within 3 × 10⁻¹⁴ (gate 10⁻⁹) |
| window-level rungs (r1R, r1D, r1S) | gate A: equal KIND marginal per class; gate B: equal multiset of whole-record probabilities per class; gate C: an independent construction, plus brute force on small worlds | **exhaustive** over classes |

**What none of this validates: the kernel.** Every route calls the same kernel functions: the enabled
transitions, the record a transition emits, and the rung projection. The gates validate computation *given* the
kernel. The kernel rests on its tests and reviews, and on one argued property, tested directly.
- **Structural-observer injectivity from reset.** Every random choice is labelled in the next record, so from a
  reset the r1 projection determines the state. [Proof sketch in `full-context-injectivity-note-v0.1.md`. The note
  predates the looping programs and was proposed for, not completed, cross-family review.]
- **Tested on the frozen world** by enumerating every transition path from reset up to 8 records: at r1 every
  prefix determines a single structural state, at both ε (up to 2,562 prefixes). At r0, prefixes leave up to 18
  states (ε = 1) and 36 (ε = ½). [EXACT, `reset-injectivity-r1-2026-10-13.jsonl`]
- The pattern observer does not inherit this, because it does not know which renamed entity is which (§3.1).

### 2.4 Rewrites that hold the ceiling

A **window-level rung** fills a slot its base rung masks, with a function of the window's records that precede the
slot in field order. (A function of the whole window could leak the target.) It adds nothing an observer of the
window lacked, so the ceiling is unchanged class by class (gates A–C above). The rewrite is applied to a window the
consumer already holds. It is not a field a producer emits. The three such rungs on r1 (relay, decoy, self-copy) are
defined in §3.3.

### 2.5 Learners

**Model:** a decoder-only transformer: 4 layers, d = 128, 4 heads, MLP width 512, 838,940 parameters, and up to 42
positions (BOS plus one window). Each model is trained from scratch on 2 M windows from the window law.

**Training:**
- **Optimizer and schedule:** AdamW (β 0.9, 0.95; weight decay 0.1), a 500-step linear warmup to lr 1e-3, cosine
  decay to 1e-4, batch 256, gradient clipping at 1.0.
- **Loss:** the mean cross-entropy over the scored target positions. Where a rung's targets are deterministic, a
  model can learn to predict them almost perfectly.
- **Budgets:** 5 and 15 epochs. At 15 epochs, validation loss is still falling slowly: the last two epochs account
  for a median of 7.5 % of the decline from epoch 5 (at most 17 %) across the 30 ladder runs. We therefore write
  "at 15 epochs", not "at convergence".

**Recipe variants.** In the original recipe every window position is a target, including any slot a window-level
rung fills. The §4e follow-ups vary only the OBJECT slot:
- *unscored* (r1m, r1Rm): OBJECT is left out of the loss, which also shrinks the loss denominator by about 24 %;
- *paired targets* (r1Rs): inputs from the r1 corpus and targets from the r1R corpus, accepted only if the two have
  identical masks and differ only at OBJECT.
Seed i shares initial weights and batch order across arms.

**Scoring at position k = 7.** Let the realised next record have KIND x and actor pattern value a. P\* is its exact
law given the pattern class, and q is the model's softmax.
- **KIND shortfall:** log₂ P\*(x | class) − log₂ q̃(x), where q̃ is the model's KIND distribution renormalised over
  non-end tokens. (Ending the window is scored separately and excluded.)
- **ACTOR shortfall:** log₂ P\*(a | x, class) − log₂ q̃(a | x). The model's probability is projected to the pattern
  value. A thread already bound in the window scores its own token. A fresh thread scores the summed probability of
  the drawable thread names not yet used in the window (reserved names never count).
- Means over a class estimate KL(P\* ‖ q̃). Single windows can be negative.
- Subsets are always chosen by functions of the prefix, never by another realised field, which would bias the
  estimator.
- A shortfall is measured above the model's own interface's ceiling. On the content rungs, 15-epoch shortfalls run at
  about 1–4 % of the KIND ceiling (0.009–0.041 bits against 0.78–1.00); on r0 about 0.4 %.

**The actor's far information.** ι_{A|K,m} is the KL from the actor's exact law given kind and the whole window, to
its law given kind and the last m records, read through the suffix's own naming. An entity bound only before the
suffix counts as fresh to the order-m observer. That coarsening discards identity that the earlier records fixed,
so ι_{A|K,m} is a **lower bound** on the far identity information.

**Unit of inference.** The model is the unit. Inference is per model or per matched seed pair, never a window-level
t statistic on a seed mean.

**Which models carry which claim:**

| experiment | cells | seeds per cell | budget | prior exposure | analysis |
|---|---|---|---|---|---|
| D1, KIND within-cell (held-out) | 5 of the 8 r1–r4 cells: r1 ε½, r2 ε1, r2 ε½, r3 ε½, r4 ε½ | 3; 6 for r2 ε½ and r4 ε½; seeds 4–6 for r2 ε1 | 5 ep | none (21 runs) | stamped before the census |
| A1, ACTOR within-cell | 8 cells | 36 runs: 21 held-out, 15 existing | 5 ep | 15 censused earlier for KIND | stamped before any actor ι |
| 15-epoch ladder (C1–C4, A4) | 8 r1–r4 cells, plus r0 at both ε | 3 | 15 ep | r1 ε1 seeds 1–3 evaluated before the prereg | stamped before evaluation |
| relay | r1 against r1R, ε = 1 | 3 per arm | 5 and 15 ep | — | stamped (Δι₄ pricing) |
| loss-masked arm | r1Rm | 3 | 15 ep | — | stamped (reading T) |
| relay 2×2 | r1m, r1Rs | 3 per arm | 15 ep | — | stamped (C1–C4) |
| count baseline | 10 cells | — | — | — | exploratory |
| GRU baseline | 8 r1–r4 cells | 1 | 15 ep | — | stamped (G1; quality floor) |
| d = 256 size check | r1 ε1 | 3 (15 ep), 1 (45 ep) | 15, 45 ep | trained in September | exploratory (not the planned pre-registered wave) |

Test windows come from episodes disjoint from training, as asserted by the corpus gates.

---

## Provenance

- World and law: `src/yupi/config.py` `WorldConfig.c1`; `src/yupi/programs.py` `c1_prime_loop_programs`;
  `src/yupi/window.py`. The freeze was enacted on 2026-09-13.
- Validation:
  - structural gate: `exit-clause-40-8-2-note-v0.1.md`, `tests/test_window_gate_full.py`;
  - pattern gate: `src/yupi/pattern_ceiling.py` docstring, `tests/test_pattern_ceiling.py`, and
    `pattern-ceilings-40-8-2-k*-2026-09-18.json` (`gate.n` ≈ 91, `all_exact`);
  - gates A–C: `pattern_ceiling.py` `relay_gates` and the exact-side logs;
  - reset injectivity: `scripts/reset_injectivity_r1.py`.
- Scoring: `src/yupi/learner/evaluate.py` docstring (continuation renormalisation, the fresh-entity projection, end
  scored separately). Actor ι: `implicit-information-design-v0.1.md` and the actor prereg.
- Convergence: training logs of the 30 ladder runs (`~/.cache/yupi-scratch/runs/ladder15`, `runs/gpu`), summarised
  2026-10-13.
- Recipe variants: `src/yupi/learner/data.py` (`unscore_fields`, `paired_targets`) and `train.py`.

**Not re-audited:** the D2 witnesses, and the disjointness of test episodes (asserted by the corpus gates).
