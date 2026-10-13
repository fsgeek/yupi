# Paper 1, §2 draft v0.1 (2026-10-13): The instrument

> **Status: DRAFT, owning instance. Not reviewed.** Written from skeleton v0.5. Every configuration value was read
> from code or from a raw named in the provenance list, and none from memory. Claim status is given in square
> brackets for review, to be removed in the paper.

## 2. The instrument

### 2.1 The world

Yupana is a small stochastic operating-system kernel whose entire state and transition law we own. The working
configuration has four threads, two CPUs, two locks and one asynchronous device, with a request pool of four, a
device queue of depth two, and completion probability 1/3 per step. Each thread runs a fixed looping program, and
the four programs give four contention roles:
- thread 0: acquire lock 0, release it, issue I/O;
- thread 1: take lock 0 then lock 1, and release both in reverse order;
- thread 2: compute, then take and release lock 0;
- thread 3: issue I/O, then take and release lock 1.

The scheduler is round-robin with probability 1 − ε and uniform over runnable threads with probability ε. The base
condition is ε = 1, and we also report ε = ½.

The kernel makes only two kinds of random choice: which thread runs next, and whether the device completes a
request on a given step. Every such choice is labelled in the very next record by its kind and actor. From a known
start, then, a record stream that shows KIND and ACTOR determines the state exactly (§2.3, injectivity). Every
uncertainty in what follows therefore comes from the observation, not from hidden coins: the window cuts history
off, and the interface hides fields.

An episode runs 40 records from reset. The **window law** (40, 8, 2) draws an endpoint T uniformly from
{2, 4, …, 40} and shows the observer the last 8 records ending at T. A window whose start reaches back to the
reset begins with a RESET token, so the observer knows it is seeing the episode's beginning. This law was frozen
before any learner was trained.

### 2.2 Interfaces

Every record has five fields: KIND, ACTOR, OBJECT, RELATED and LINEAGE. An interface (*rung*) shows some of them
and masks the rest. Masked fields render as a placeholder token, so every record on every rung is exactly five
tokens long and a lag of m records is a lag of 5m tokens on every interface.

| rung | shows |
|---|---|
| r0 | KIND |
| r1 | + ACTOR |
| r2 | + OBJECT (which lock or device) |
| r3 | + RELATED (the thread woken, or the owner) |
| r4 | + LINEAGE (the request identifier) |

Adjacent rungs differ by exactly one field, and each added field was shown, before any learner existed, to change
some posterior or some finite-horizon predictive distribution. [EXACT; Part I D2]

**Entity names carry no identity across episodes.** In each episode, threads, locks, devices and requests are
named by a keyed injection from pools much larger than the entity counts: 64 thread names for 4 threads, 32 lock
names for 2 locks, 16 device names, 32 request names. A name tells the observer which entity *within this
episode* it is, and nothing else.

### 2.3 Exact ceilings for a stated observer

A ceiling is defined for an observer, so we state the observer. Because names are re-drawn every episode, the
learner's comparison point is the **pattern observer**. It sees the window with every entity renamed by order of
first appearance, so that only the pattern of who recurs remains. For each pattern class of windows, the exact
predictive law of the next record is a finite mixture computed in exact rational arithmetic. It comes from a
recursion over the window process, weighted by the window law. The ceiling for a target (here, the next KIND) is
the law-mass-weighted conditional entropy of that target given the class.

**What the gate validates, and what it does not.** Two computational routes agree on every window's posterior:
the filtering recursion and an independent path summation. They agree on 8,542,940 windows across all ten
(rung, ε) pairs, with zero mismatches. Both routes call the same kernel functions, though: the enabled-transition
set, the record a transition emits, and the rung projection. So the gate validates the filter *given the kernel*.
It does not validate the kernel. [EXACT for that statement only; A1] The kernel's correctness rests on its tests
and review, and on one proved property. **Full-context injectivity:** from a reset, the map from transition
sequences to their r1 projections is one-to-one, for every configuration the kernel can express, because each
random choice is labelled in the next record. It follows that every content rung r1–r4 has a point-mass
posterior from reset, and the frozen world's ceiling tests confirm zero state entropy on windows anchored at
reset. r0 masks ACTOR and is not injective from reset. [Theorem with proof sketch; computational falsification
attempt survived; pinned in `tests/test_c1prime_loop_ceilings.py`]

**Position.** The ceilings and lag profiles in §3 are taken at window position k = 7: after seven records, predicting
the eighth. They cover only windows that run at least seven records, which is 0.85 of window law mass (endpoints
T ≥ 8).

### 2.4 Interventions that hold the ceiling

A *window-level* rung may fill a slot that its base rung masks, using any function of the window itself. Such a
field adds nothing that an observer of the whole window lacked, so the ceiling is unchanged class by class. Where
the information sits can still change. We use three such rungs on r1, each writing into the OBJECT slot (§3.3):
the relay r1R, the decoy r1D and the self-copy r1S. Three gates check each one:
- the ceiling is identical class by class, computed by two independent routes (the rung's window map applied before
  pattern keying, and a derivation from the base rung's table);
- the corpus pairs each window with its base-rung counterpart;
- the evaluator shows no regression.
[EXACT; gates A–C]

### 2.5 Learners

The learners are decoder-only transformers with 4 layers, d = 128, 4 heads and an MLP width of 512, about 0.84 M
parameters. Each takes a BOS token plus one window, with up to 42 positions. Each is trained from scratch on a
corpus of 2 M windows drawn from the window law, with AdamW, lr 1e-3 cosine-decayed to 1e-4 and batch 256. We
report two budgets:
- 5 epochs, which is under-converged;
- 15 epochs, the converged budget.

There are three seeds per (rung, ε) cell. Test windows come from episodes disjoint from training.

**Scoring.** On each test window at position k = 7, the learner's **shortfall** for the next KIND is the
realized-record estimate log P\*(x | class) − log q(x | window), where x is the KIND that actually occurred. Its
mean over a class estimates KL(P\* ‖ q) for that class, and it may be negative on single windows. A shortfall is
always measured above the learner's own interface's ceiling, so cells with different ceilings are comparable.
Subsets are chosen only by functions of the prefix, never by another realized field. A subset selected on a
realized field biases this estimator. [method; feedback memory of 2026-09-24]

**Unit of inference.** The model is the unit. Between-seed variance dominates window-level sampling error at
5 epochs, so every learner claim is stated per model, or per seed pairing, and never as a window-level t
statistic on a seed mean. [ROBUST, B6; C4]

---

## Provenance

- World configuration: `src/yupi/config.py` `WorldConfig.c1`, used by `scripts/pattern_ceiling.py:124`. Programs:
  `src/yupi/programs.py` `c1_prime_loop_programs`. Scheduler policy: Part I D9.
- Window law: `src/yupi/window.py` `WindowLaw`; the raws record `{'T_ep': 40, 'L': 8, 'B': 2}`. Enacted as frozen
  on 2026-09-13 (memory of that date).
- Records and rungs: `src/yupi/corpus/rendering.py` `render`; Part I D5 and D2. Name pools:
  `src/yupi/corpus/vocab.py` `POOL_SIZES`.
- Gate count: `exit-clause-40-8-2-note-v0.1.md` (8,542,940 windows, `tests/test_window_gate_full.py`). The
  shared-kernel limit is the methods-robustness audit §5.
- Injectivity: `full-context-injectivity-note-v0.1.md`, and the frozen-world test run 2026-10-13 (7 passed).
- Coverage 0.85: `src/yupi/window_process.py` `prefix_law_aggregate` (T − U ≥ k), re-derived 2026-10-11.
- Learner: `src/yupi/learner/model.py` defaults (parameter count 838,940, computed 2026-10-13), `train.py`
  `TrainConfig`, `converged-ladder-prereg-v0.1.md`.
- Estimator: `src/yupi/learner/census.py` docstring.

**Not re-audited this session:** the D2 witnesses for each adjacent rung pair; gates B and C on the r1D and r1S
corpora; the disjointness of test episodes (asserted by corpus gates, not re-run here).
