# Yupana Milestone 1 — Specification Draft

**Status:** exploratory draft, founding day (2026-08-11). Design decisions below are *proposed*, each with rationale and falsifier. Nothing is confirmatory. Attack freely.

**v0.2 (2026-08-12):** all four founding-day open questions are now resolved — three by D8–D10 below, the fourth (gap-3's home) by `exposure-gap-note-v0.1.md` on founding evening. D7 adds a new constraint from Yupi's second purpose (training-intervention testbed). Decision rules pre-stated before any measurement; resolved in dialogue with Tony. The decision-discipline note below records the principle that did the deciding.

**Milestone 1 goal (per proposal §11):** specify the finite state machine and transition process; implement simulator + event interfaces; validate exact filtering against exhaustive enumeration; characterize observability and synchronization per interface — all *before* training any transformer.

## Governing design principle: interface-first

The observation interface is the specimen; the world is the apparatus. Design order is therefore inverted from the naive one:

1. Fix the **query set** — the latent facts an observer cares about.
2. Design the **interface ladder** so adjacent rungs differ by exactly one identifiable kind of information.
3. Choose **world dynamics** so that (a) each rung's added field provably changes the posterior over the query set, and (b) the sparsest rung stays inside the exact-filtering support bound.

Realism is not a design criterion. Yupana does not need to resemble Linux; it needs to be the world in which interface differences cast the sharpest shadows.

## Decision discipline: collapse vs. generality (added 2026-08-12)

Premature collapse (resolving before the evidence arrives) has a dual failure mode: premature generality (keeping options open when optionality is not free). The discriminator is two tests: **(a) do the alternatives share an implementation, and (b) is the evidence that would decide between them cheap and already scheduled?** Both pass → parameterize and defer to measurement (D9). Either fails → commit outright and document a *revisit trigger* instead of engineering optionality (D8). This principle decided D8–D10 and applies to every implementation decision that follows.

## Query set (draft)

For each time t, posteriors over:

- **Q1 (ownership):** which thread owns lock L? (incl. "free")
- **Q2 (runnability):** is thread T runnable / running / lock-blocked / IO-blocked?
- **Q3 (in-flight):** which requests are outstanding at device D, in what order?
- **Q4 (next-wake):** which thread does the next completion/release wake?
- **Q5 (relational):** is the blocked thread waiting on the resource owned by the running thread? (name-free binding query)

Q5 is the held-out-binding target; Q1–Q4 are the observability targets.

## Proposed design decisions

### D1 — Deterministic workloads; stochasticity confined to scheduler and device

Every thread runs a fixed finite program (compute / acquire / IO / release loop). The only random elements: scheduler tie-breaking among runnable threads, and device completion timing (per-tick completion probability).

*Rationale:* all world entropy then arises from interleaving and asynchrony — exactly the things telemetry fields describe — so every bit of posterior uncertainty is attributable to what the interface masked. Private coin flips inside workloads would inject entropy no interface could surrender, flattening rung differences.

*Falsifier / known risk:* over-synchronization. Deterministic workloads may make the world too inferable — long contexts could collapse every interface to certainty, erasing rung differences. **M1 must measure posterior entropy vs. context length per interface.** Contingency: add back the minimal workload randomness needed to keep rungs separated; the amount required is itself a synchronization measurement, reported not hidden.

### D2 — Interface ladder as controlled information increments

Rungs (from proposal §6.1): actor-only → +object → +related-entity → +lineage. Requirement added here: for each adjacent pair, exhibit (analytically or by enumeration) a history class where the added field changes the posterior on a named query in Q1–Q5. A rung that changes no posterior is redesigned before implementation. Controls: entropy-matched irrelevant field; redundant (derivable) field.

### D3 — Entity pool ≫ entity count (promoted from CLAUDE.md constraint (a))

Thread names drawn per-episode from a pool of ≥50 tokens for ≤4 threads; locks and devices proportionally. No token ever has a stable semantic role. Held-out evaluation reserves a subset of names never seen in training. This constraint is arithmetic, not preference: without pool ≫ count, held-out-binding evaluation is impossible.

*Warning added 2026-08-11 (from full-text read of arXiv:2607.19379):* per-episode symbol relabeling is empirically **scale-invariantly fatal** (2.8M→316M params, immune to extended training) when the discriminative statistic requires *computing over* symbol identities (e.g., composing per-episode bindings with arithmetic), but harmless when the required structure is purely *relational* (attention key-matching). Audit requirement: every headline Yupana condition must depend only on relational structure over per-episode names (who owns, who waits, who wakes). Any condition that would require arithmetic keyed to episode-random tokens (counters, timers over fresh names) must be either redesigned or explicitly designated a learnability-boundary condition — never left as an accident.

### D4 — Support-bound co-design (promoted from CLAUDE.md constraint (b))

The sparsest interface produces the fastest posterior-support growth and is the binding computational constraint. Requirement: before any transformer exists, measure reachable-support growth of the exact filter under the actor-only interface on the base configuration. If support growth under the sparsest rung exceeds the enumeration budget, the world shrinks — not the ladder.

### D5 — Fixed record schema with MASKED symbols (from proposal §5.3)

One schema across all interfaces; masked fields carry a distinguished MASKED token. Vocabulary size and record length constant across conditions, so observability gains cannot masquerade as tokenization gains.

### D6 — Belief update must be in the transformer-learnable regime (added 2026-08-11, from full-text read of arXiv:2602.14814)

Siems et al. show 265M from-scratch transformers fail S₅ permutation-composition state tracking outright even under dense observation — an *expressivity* failure, not an information failure. If Yupana's hidden dynamics embed group-word-problem-hard structure (e.g., scheduling rules that compose like permutations), the accessible-representation gap silently absorbs an architecture-expressivity term and the three-gap decomposition's interpretation corrupts.

*Requirement:* M1's characterization must include an argument (or measurement) that Yupana's exact belief update lies within the transformer-learnable regime — e.g., bounded-depth filtering without hard group-composition subproblems. If any condition intentionally crosses that boundary, architecture becomes an explicit experimental factor for that condition, and it is labeled as such.

### D7 — Reward–truth divergence hook (added 2026-08-12)

Yupi's second purpose (stated by Tony, 2026-08-12) is testing alternative training regimes — post-training and fine-tuning interventions measured against exact ceilings. Requirement on the world/query design, cheap now and expensive to retrofit: **the query and output design must admit query classes where a rewarded report and the posterior-truthful report can differ.** Without reward–truth divergence, the phase-2 masking experiment (does compliance-style post-training widen the exposure gap G(Q)?) has nothing to grip. Consistency check against the restricted-observer hierarchy in `exposure-gap-note-v0.1.md` is an implementation-time deliverable.

*Positioning note:* adjacent literatures test sycophancy and reward hacking behaviorally — against raters, preference models, or other LLMs. The contribution here is the conjunction: divergence measured against exact posteriors, i.e., against ground truth rather than against another opinion. Nobody else can currently run that experiment, because nobody else has the ceilings.

### D8 — Tick semantics: strict interleaving, committed (resolved 2026-08-12)

Exactly one enabled transition fires per tick (scheduler step, instruction, lock op, I/O issue, or completion); exactly one record is emitted. Two-CPU parallelism in C1 is modeled as tick-alternation — standard interleaving semantics, named honestly. **No composite-tick abstraction in the transition API.** By the decision discipline: composite ticks fail both tests (different state space, filter update, and record schema; no scheduled measurement discriminates), so holding the option open is a standing generality tax on the exact filter for an option the serialization argument says we would likely never exercise — the trace is a token sequence regardless, so simultaneous dynamics would need a serialization order that reintroduces interleaving at the token level.

Ordering-loss as an interface phenomenon is carried instead by coarsening the TIME_CLASS field on the ladder. *Revisit trigger:* if TIME_CLASS coarsening proves insufficient to study ordering-uncertainty, composite ticks earn a world v2 — a bounded, honest rewrite, not an option held open.

### D9 — Scheduler: ε-parameterized, decision rule pre-stated (resolved 2026-08-12)

Policy: round-robin with probability 1−ε, uniform-random among runnable with probability ε. Both endpoints share one implementation and one state space, and M1's exact-filter characterization sweeps ε on CPU at negligible cost — the deferral tests pass, so the base value is decided by measurement.

**Decision rule, stated before data:** the base condition defaults to ε=1 — the maximum-entropy null, under which the choice-among-runnable carries no learnable pattern and attribution is sharpest (note: enabled-*set* dynamics remain learnable structure at any ε; ε=1 purifies attribution, it does not perfect it). If the sweep shows a D4 support-budget violation or rung collapse at ε=1, take the largest ε satisfying both. The M1 report documents rule and outcome.

*The tension this resolves is constitutive, not accidental:* masked entropy and posterior support are the same quantity seen from the observer's side and the filter's side — rung separation **is** support growth. D1's placement of entropy in scheduler and device is defended on relational grounds (that is where queries Q1–Q5 live; private workload coins would add entropy no query posterior cares about), and D4's budget is a hardware fact — binding, not wrong. Structured scheduling enters later as the §6.4 priority-interaction manipulation, not baked into the base.

### D10 — Device completion discipline: the lineage 2×2 (resolved 2026-08-12)

Completion discipline is a two-valued world parameter sharing one state space (an ordered queue either way; only the enabled completion-transitions differ):

- **Stochastic-order (base world):** any in-flight request completes with per-tick probability. Q3 (in-flight set and order) is substantive, and the provenance rung has its D2 grip — lineage on a completion record resolves *which* request finished, moving the Q3/Q4 posteriors.
- **FIFO (control world):** completion order equals issue order; only timing is stochastic. Lineage becomes *derivable* — the k-th completion is the k-th issue — making it exactly D2's redundant-telemetry control, in the same schema, same field, same vocabulary. Cleaner than a synthetic derivable field.

**The experimental unit is the 2×2:** {FIFO, stochastic} × {lineage exposed, MASKED}. One diagonal isolates information gain, the other isolates token-volume effect, and the cross-world comparison at fixed interface measures how the same field changes what a model learns when the world decides whether the field carries information.

*Pre-registered crossover prediction (doubles as instrument validation):* FIFO-lineage is redundant only relative to full context — truncation before the issue events makes the "redundant" field informative again. The redundancy control should therefore show no effect at full context and a growing effect under truncation (an H5 × D2 interaction, exactly computable in advance). If the measured posteriors do not show this crossover, the filter or the reasoning is wrong.

*External validity (Tony, from the builder's chair):* disk controllers have reordered operations since at least 1990 — Episode's asynchronous old/new-value log (STEAL/NO-FORCE semantics) was deliberately designed to exploit controller reordering, and Episode remains in production today as the POSIX file system for IBM z/OS. Stochastic-order is the ecologically honest base; FIFO is correctly framed as the idealized control.

## Configurations

- **C0 (validation):** 2 threads, 1 CPU, 1 lock, 1 device, queue depth 1. Small enough for exhaustive enumeration of the full belief-state dynamics. Every filtering result must match enumeration exactly here before C1 is touched. Both completion disciplines (D10) are enumerated on C0.
- **C1 (base experimental):** 4 threads, 2 CPUs, 2 locks, 1 device, queue depth 2 (pending D4 measurement). Scheduler ε per D9's decision rule; completion discipline stochastic-order per D10. Exact filtering along sampled histories; support bound per D4.

## Deliverables and exit criteria

1. State-space and transition specification document (machine-checkable form).
2. Simulator + interface emitters (all rungs, D5 schema).
3. Exact filter, validated bit-for-bit against enumeration on C0.
4. **Observability characterization report:** per-interface posterior entropy over the query set vs. context length; support-growth curves; synchronization horizons; D1 falsifier verdict; the D9 ε-sweep and base-ε decision under the pre-stated rule; the D10 crossover computation (FIFO-lineage redundancy vs. context horizon) as instrument validation; the D7 consistency check against the exposure-gap note's observer hierarchy.

M1 succeeds if the report shows measurably distinct observability regimes across rungs within tractable support bounds — that is, if the world can carry the experiment. M1 fails informatively if the rungs collapse (over-synchronization) or the support explodes (D4 violation); either outcome redesigns the world before any GPU-hour is spent.

## Founding-day open questions — all resolved

- ~~Scheduler policy for C1~~ → D9 (ε-parameterized, decision rule pre-stated, measured in M1).
- ~~Device queue: FIFO certain or completion-order uncertainty~~ → D10 (world parameter; the lineage 2×2).
- ~~Tick semantics~~ → D8 (strict interleaving, committed; revisit trigger documented).
- ~~Where does the gap-3 formalization live~~ → separate stamped note, `exposure-gap-note-v0.1.md` (2026-08-11).

## Remaining open parameters (implementation-time)

Numeric parameters — per-tick completion probability, identifier pool sizes (≥50 per D3), the ε sweep grid, workload program shapes — are set at implementation time and recorded in the M1 report, not frozen here. Each must respect the D3 relational-structure audit and the D6 learnable-regime argument.
