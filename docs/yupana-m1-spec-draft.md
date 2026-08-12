# Yupana Milestone 1 — Specification Draft

**Status:** exploratory draft, founding day (2026-08-11). Design decisions below are *proposed*, each with rationale and falsifier. Nothing is confirmatory. Attack freely.

**Milestone 1 goal (per proposal §11):** specify the finite state machine and transition process; implement simulator + event interfaces; validate exact filtering against exhaustive enumeration; characterize observability and synchronization per interface — all *before* training any transformer.

## Governing design principle: interface-first

The observation interface is the specimen; the world is the apparatus. Design order is therefore inverted from the naive one:

1. Fix the **query set** — the latent facts an observer cares about.
2. Design the **interface ladder** so adjacent rungs differ by exactly one identifiable kind of information.
3. Choose **world dynamics** so that (a) each rung's added field provably changes the posterior over the query set, and (b) the sparsest rung stays inside the exact-filtering support bound.

Realism is not a design criterion. Yupana does not need to resemble Linux; it needs to be the world in which interface differences cast the sharpest shadows.

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

## Configurations

- **C0 (validation):** 2 threads, 1 CPU, 1 lock, 1 device, queue depth 1. Small enough for exhaustive enumeration of the full belief-state dynamics. Every filtering result must match enumeration exactly here before C1 is touched.
- **C1 (base experimental):** 4 threads, 2 CPUs, 2 locks, 1 device, bounded queue. Exact filtering along sampled histories; support bound per D4.

## Deliverables and exit criteria

1. State-space and transition specification document (machine-checkable form).
2. Simulator + interface emitters (all rungs, D5 schema).
3. Exact filter, validated bit-for-bit against enumeration on C0.
4. **Observability characterization report:** per-interface posterior entropy over the query set vs. context length; support-growth curves; synchronization horizons; D1 falsifier verdict.

M1 succeeds if the report shows measurably distinct observability regimes across rungs within tractable support bounds — that is, if the world can carry the experiment. M1 fails informatively if the rungs collapse (over-synchronization) or the support explodes (D4 violation); either outcome redesigns the world before any GPU-hour is spent.

## Open questions (for Tony / future instances)

- Scheduler policy for C1: pure random among runnable, or round-robin with random tie-break? (Affects both entropy budget and realism of the priority-interaction condition later.)
- Device queue: FIFO certain, or is completion-order uncertainty (Q3) wanted as a separate rung-discriminator?
- Tick semantics: one event per tick vs. simultaneous events — affects lineage-field design and the exposure analysis later.
- Where does the gap-3 query-class formalization live — separate stamped note (recommended, time-critical) or appendix here?
