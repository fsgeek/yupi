# Yupana Milestone 1 — Part II: Formal Semantics (Draft v0.2)

**Status:** exploratory draft, 2026-08-12; updated same day for Part I v0.2.3 (predictive-state targets §5, witnesses 10–11, symmetric witness quality). This is the statute to Part I's constitution (`yupana-m1-spec-draft.md`, frozen at v0.2.3, commit `00ef2a7`). Every normative choice below carries rationale; contested choices carry a falsifier or revisit trigger. Attack freely.

**v0.2 (2026-08-13, truncation review round):** §2's truncated-window paragraph replaced by normative truncation, window-sampling, and shifted-reference semantics; the v0.1 offset-known default is **inverted** (offset-unanchored base), with the inversion recorded in place. §4's TIME_CLASS becomes a maskable absolute field. Provenance: derived-prior principle and two-reference decomposition proposed in-session (Claude instance); the IID/generalization boundary forced by Tony's question; support-containment admissibility rule and its two measure-theoretic amendments from cross-family review (ChatGPT), adopted after verification with two sharpenings (process-vs-empirical support; exactness boundary at transcendental diagnostics). Motivating measurement: commit `3e5a19f` — the C0 family is lossless at every rung at full context from reset, so all interface-rung grip at validation scale lives on the axes this section defines.

Contract: this document discharges the twelve Part II items enumerated at the end of Part I. The mapping is: §1→item 1, §2→item 2, §3→item 3, §4→item 4, §5→items 5+9, §6→items 6+10, §7→item 7, §8→item 8, §9→item 12, §10→item 11.

---

## §1 State tuple and invariants

An episode is parameterized by configuration $C = (n_T, n_C, n_L, n_D, d, R)$: thread, CPU, lock, device counts, device queue depth, and request-identifier pool size, with $R \ge 2d$.

$$S_t = (\mathbf{pc}, \mathbf{st}, \mathbf{run}, \rho, \mathbf{own}, \mathbf{wq}, \mathbf{dq}, \sigma)$$

- $\mathbf{pc}[i] \in \{0, \dots, |P_i|\}$ — program counter of thread $i$ into its fixed program $P_i$ (see §2); value $|P_i|$ means TERMINATED.
- $\mathbf{st}[i] \in \{\mathrm{RUNNABLE}, \mathrm{RUNNING}, \mathrm{LOCK\_BLOCKED}(l), \mathrm{IO\_BLOCKED}(r), \mathrm{QUEUE\_BLOCKED}(dev), \mathrm{TERMINATED}\}$ — thread status.
- $\mathbf{run} \subseteq \{1..n_T\}$, $|\mathbf{run}| \le n_C$ — the running set (threads currently holding a CPU slot). CPUs are anonymous slots; there is no per-CPU identity in the base state. *(Rationale: with symmetric CPUs, per-CPU assignment adds state distinctions no query in Q1–Q5 references; the D3 relational audit prefers the quotient. Falsifier: if a future condition makes CPU identity semantically relevant — e.g., per-CPU caches — the state gains $\rho$ as a map; the slot below is reserved.)*
- $\rho$ — reserved, unused in M1 (per-CPU identity map; present in the tuple so its later addition is a field change, not a schema change).
- $\mathbf{own}[l] \in \{1..n_T\} \cup \{\mathrm{FREE}\}$ — lock owner.
- $\mathbf{wq}[l]$ — ordered list of threads waiting on lock $l$ (FIFO discipline, §3.5).
- $\mathbf{dq}[dev]$ — ordered list of in-flight requests $(i, r)$: issuing thread, request id $r \in \{0..R-1\}$; $|\mathbf{dq}[dev]| \le d$.
- $\sigma$ — episode-local injection from entities to surface names (D3 pool); fixed for the episode at reset.

**Invariants.** (I1) $i \in \mathbf{run} \iff \mathbf{st}[i] = \mathrm{RUNNING}$. (I2) A thread appears in at most one of: $\mathbf{run}$, one $\mathbf{wq}[l]$, one in-flight/queue-blocked relation. (I3) $\mathbf{own}[l] = i$ only if $\mathbf{st}[i] \ne \mathrm{TERMINATED}$. (I4) request ids in $\mathbf{dq}[dev]$ are pairwise distinct (guaranteed by lowest-free allocation from a pool of size $R \ge 2d$; ids are recycled only after completion — the machine is finite). (I5) At most one request in flight per thread (synchronous I/O, §2). (I6) Base workloads acquire locks in global index order, so lock-cycle deadlock is unreachable (checked, not assumed: the witness suite includes a reachability check that no state with a blocked cycle occurs; violated only if a workload violates the ordering constraint, which the generator rejects).

## §2 Programs, initial state, episodes

**Instruction taxonomy** *(resolves Part I ambiguity 8):* lock and I/O operations are instruction subclasses. The instruction alphabet is $\{\mathrm{COMPUTE}, \mathrm{ACQUIRE}(l), \mathrm{RELEASE}(l), \mathrm{IO}(dev)\}$. A program $P_i$ is a finite sequence over this alphabet (shapes are implementation-time parameters per Part I, constrained by I6 and the D3/D6 audits). COMPUTE is single-tick. IO is synchronous: issue then $\mathrm{IO\_BLOCKED}$ until *own* request completes (I5).

**Initial state $\mu_0$:** deterministic modulo naming — all threads at $\mathbf{pc}=0$, RUNNABLE, $\mathbf{run} = \emptyset$, locks FREE, queues empty; $\sigma$ drawn uniformly from injections. So $\mu_0$ is uniform over the naming orbit of a single structural state. *(Rationale: a known reset state makes the full-episode condition the zero of the context-as-observability axis, per proposal §6.2.)*

**Episode boundary:** an explicit RESET record, visible at **every** rung *(rationale: episode-boundary observability is not an interface rung under study in M1; making it universal keeps the ladder about within-episode information)*. Episodes run to a fixed horizon $T_{ep}$ (parameter) or until all threads TERMINATED, whichever is first.

**Truncation, window sampling, and shifted-reference semantics** *(v0.2, 2026-08-13 review round; supersedes the v0.1 offset-known default — the inversion is recorded here, not silently applied).*

*(a) Training window protocol.* Episodes run from $\mu_0$ to $T_{ep}$; a window position $t \sim \mathrm{Uniform}\{1..T_{ep}\}$ is drawn; the observation is the last $\min(k, t)$ records, with $k$ the context-length condition parameter. **The truncation prior is derived, not stipulated:** the exact-filter prior is whatever marginal this sampling law induces. Rationale: a Bayes ceiling is a ceiling *for a learner* only under the learner's own generative process; any stipulated prior the training distribution does not induce converts prior mismatch into a phantom accessible-representation term and the decomposition stops decomposing.

*(b) Base condition: offset-unanchored.* The prior at window start is the $t_0$-mixture of exact marginals $P(S_{t_0})$ induced by (a). This inverts v0.1's default (offset known, "lost history, not lost clock"): review found the absolute offset is a covert information channel that partially undoes the truncation it rides on. The anchored condition remains defined and is priced under (e); v0.1's falsifier anticipated the offset-unknown variant — the round made it the base.

*(c) Anchoring is a maskable field, not a protocol fork.* TIME_CLASS carries the absolute bucket index; the base condition masks it (§4); the anchored condition is a rung-style unmasking of the same schema. Anchored evaluation of a *model* is admissible only by promotion, per (e).

*(d) Headline claims are exchangeable and in-distribution.* Every gap-decomposition claim is evaluated on held-out windows drawn by the exact training protocol (mirroring D3's exchangeability discipline). Shifts enter only as rows governed by (e).

*(e) Shifted-reference rule (normative).* For an evaluation process $Q \neq P$ (the training process), with $f_Q, f_P$ the exact Bayes predictors of the two processes and $f_M$ the model:

- A **model-generalization row** (shifted ceiling $f_Q$; transplanted reference $f_P$; model $f_M$) is admissible only under process-level absolute continuity, established on the joint episode-path/window measure and required at two marginals: $Q_H \ll P_H$ (the transplant is defined on $Q$'s observations) **and** $Q_{H,Z} \ll P_{H,Z}$ (log-score comparisons are finite; where this fails the row reports infinite transplant cost explicitly rather than being silently dropped). *Process* support is the criterion, not empirical-sample support: $f_P$ is defined on unsampled-but-possible windows — the same fact D3's exchangeable split relies on.
- Decomposition and names: $R_Q(f_M) - R_Q(f_Q) = \underbrace{[R_Q(f_P) - R_Q(f_Q)]}_{\text{transplant cost, } \ge 0} + \underbrace{[R_Q(f_M) - R_Q(f_P)]}_{\text{learner residual, signed}}$. The transplant cost prices the *unchanged $P$-optimal rule* under $Q$; it is not a floor for all learners, and a model may outperform the transplant (negative residual).
- Mandatory per-row diagnostics, separating admissibility, reweighting severity, and finite-sample coverage: the exact log-density-ratio range of $dQ_H/dP_H$ (rational ratios — exact); $D_{\mathrm{KL}}(Q_H \| P_H)$ or an equivalent expected-shift measure *(transcendental: reported at declared precision — the Fraction-exactness discipline covers measures and ratios, not logarithms)*; the $Q$-mass of windows absent from the empirical training sample; a $Q$-weighted summary of empirical training counts. **Artifact requirement:** the training-sample window census is a retained deliverable; the coverage diagnostics are computable only if it exists.
- **Information-expanding shifts** (observations outside $P$'s support by construction — e.g., unmasking TIME_CLASS): oracle rows only — the shifted ceiling plus a **declared-coarsening reference** (remask the expanded field), constituting a value-of-information analysis. Model rows for such shifts require either applying the declared coarsening to the model's inputs, or promotion of the shift to a *trained* interface condition (a ladder rung). Reserving vocabulary for never-trained values does not make an eval-only model claim admissible.

## §3 Transition kernel

One transition per tick (Part I D8). The kernel is a two-stage choice; all probabilities are exact rationals.

**Stage A — event class.** Let $n = |\mathbf{dq}[dev]|$ (single device in M1 configurations).
- With probability $p \cdot \mathbf{1}[n > 0]$: a **completion** fires (§3.4).
- Otherwise: an **execution/scheduling** step (§3.1–§3.3) if any is enabled; else an **IDLE** transition (§3.6).

This implements D10's queue-level hazard: $P(\text{completion} \mid n>0) = p$ in both disciplines, and same-tick completion conflicts are impossible by construction *(resolves ambiguity 2)*.

**Stage B — which step.**

### §3.1 Dispatch
If $|\mathbf{run}| < n_C$ and runnable threads exist, the step is a DISPATCH: a runnable thread is selected by the ε-policy *(resolves ambiguities 3–4: scheduling is over one shared runnable pool — CPUs are anonymous slots; round-robin is global, by thread index, via a cursor that is part of scheduler metadata when $\varepsilon < 1$; at the ε=1 base the cursor is absent from the effective state)*. Dispatch has priority over execution steps. *(Rationale: work-conserving; an idle slot never persists while work exists, which keeps $|\mathbf{run}|$ a deterministic function of the status vector and shrinks the reachable space.)*

*Cursor semantics (v0.2 — implementation-forced decision, 2026-08-12):* the round-robin cursor advances past the selected thread on **both** mixture components — $\mathrm{cursor}' = (\text{chosen}+1) \bmod n_T$ whether the choice came from the uniform or the round-robin branch — and the stored cursor is always canonical (mod $n_T$). Under the alternative (advance only on the RR branch), the two components picking the same thread yield states differing only in cursor, transitions fail to merge, and the ε<1 reachable space inflates 2.75× on C0a — pure support-bound poison with no informational content. Discovered as a Critical in Task-3 review; ruled here so the ambiguity dies in the document, not the code.

### §3.2 Interleaving choice
Otherwise the step is an execution step by one running thread, chosen by the ε-policy over $\mathbf{run}$: uniform with probability ε, round-robin with probability 1−ε. This is the interleaving entropy source — continuous through the episode, not only at scheduling boundaries.

### §3.2a CPU occupancy is transient (v0.2 — implementation-forced decision, 2026-08-12)
A thread **leaves $\mathbf{run}$ after executing each instruction** — one-tick slot occupancy, with re-dispatch (§3.1) preceding every instruction — rather than remaining RUNNING until it blocks ("sticky" occupancy). The original §3.3 specified departure from $\mathbf{run}$ only for blocking instructions, leaving the non-blocking case ambiguous. The choice is forced, not stylistic: under sticky occupancy with $n_C = 1$, C0a's own program pair can never exhibit lock contention (thread 0 releases its lock before its only blocking instruction, so thread 1 never runs while the lock is held) — proven by exhaustive reachability during Task-3 implementation (23 reachable states, zero BLOCK events; transient gives 72 states and reaches BLOCK with a live owner). Sticky would therefore falsify `c0a_programs`' purpose and make §9 witness 2 unsatisfiable. Transient also matches §3.2's stated rationale: interleaving entropy continuous through the episode. DISPATCH records consequently appear before every instruction — a deliberate property of the record stream, not an artifact.

### §3.3 Execution semantics
The chosen thread $i$ executes $P_i[\mathbf{pc}[i]]$:
- COMPUTE: $\mathbf{pc}{+}{=}1$. Record STEP.
- ACQUIRE($l$): if FREE → own it, $\mathbf{pc}{+}{=}1$, record ACQUIRE; else → append to $\mathbf{wq}[l]$, status LOCK_BLOCKED, leave $\mathbf{run}$, record BLOCK.
- RELEASE($l$): set FREE; if $\mathbf{wq}[l]$ nonempty, wake the **head** (§3.5): it acquires ownership immediately and becomes RUNNABLE; $\mathbf{pc}{+}{=}1$. Record RELEASE (the wake is carried in RELATED/LINEAGE fields, not a second record — one transition, one record).
- IO($dev$): if $|\mathbf{dq}| < d$ → allocate lowest-free request id, append, status IO_BLOCKED, leave $\mathbf{run}$, record IO_ISSUE. If full → status QUEUE_BLOCKED, leave $\mathbf{run}$, record BLOCK *(resolves ambiguity 6: issuing blocks. When a completion frees a slot, **all** QUEUE_BLOCKED threads on that device become RUNNABLE as part of the completion transition — carried in that transition's state change like wake-on-release, requiring no wait-order state; each re-executes its IO instruction when next chosen, and losers of the race re-block, generating fresh BLOCK records. Wake-all is chosen over wake-longest-waiting because the latter would add an ordered waiting structure to $S_t$ that no query references.)*

### §3.4 Completion
The departing request is FIFO-head or $J \sim \mathrm{Uniform}\{1..n\}$ per discipline (Part I D10). The issuing thread becomes RUNNABLE (from IO_BLOCKED) — or TERMINATED if the completed IO was its final instruction (edge case caught in implementation; the pc is already past program end). Record IO_COMPLETE with ACTOR = issuing thread, OBJECT = device, LINEAGE = request id. (The kernel-internal transition kind is COMPLETION; the record layer maps it to EVENT_KIND IO_COMPLETE — one name in the schema, per D5.) *Multi-device note (v0.2):* M1 configurations are all single-device; the implementation generalizes by splitting the queue-level hazard $p$ equally across nonempty devices so total completion mass stays exactly $p$. A per-device-hazard alternative exists and is NOT chosen; revisit explicitly before any multi-device configuration ships.

### §3.5 Lock wake discipline *(resolves ambiguity 5 — a posterior-changing choice, decided, attackable)*
FIFO wake, with **direct handoff** (the woken head owns the lock immediately, preventing barging and keeping ownership a deterministic function of the visible ACQUIRE/RELEASE/BLOCK history at rich rungs). *Rationale:* by the decision discipline — random wake shares the implementation, but no scheduled M1 measurement discriminates, and FIFO keeps the lock subsystem's uncertainty at zero so the device (D10) is the *only* order-uncertain subsystem: the 2×2's attribution stays clean. *Revisit trigger:* if the related-entity rung shows insufficient posterior movement on Q4 (wake-target queries too predictable), random-wake becomes a world condition — a new entropy source whose consequences the ladder differentially reveals, per D1's contingency ordering.

### §3.6 IDLE
If no completion fired and no thread can step: emit IDLE, all entity fields MASKED, probability $1-p$ when a device queue is nonempty and $1$ otherwise. *(Rationale: preserves one-record-per-tick (D5 emission discipline) so completion timing is observable as IDLE-gap length at every rung; the alternative — geometric time-skip — makes record index diverge from tick index and complicates every filter statement.)* *(Correction, v0.2:)* the all-TERMINATED empty-queue terminal state is reachable as normal episode end and is an absorbing IDLE self-loop with probability 1 — episode termination is the driver's job (§2), not the kernel's. What I6 makes unreachable is a *deadlock* state (blocked cycle with no pending completion), not the terminal state; the original sentence conflated them.

## §4 Record schema and observation models

Schema (fixed, D5): `EVENT_KIND ACTOR OBJECT RELATED LINEAGE TIME_CLASS`, with `EVENT_KIND` ∈ {RESET, STEP, DISPATCH, ACQUIRE, BLOCK, RELEASE, IO_ISSUE, IO_COMPLETE, IDLE}.

Field semantics per kind: ACTOR = the transitioning thread (or MASKED for IDLE/RESET); OBJECT = lock/device acted on; RELATED = current owner (on BLOCK), woken thread (on RELEASE), dispatching... (full table below); LINEAGE = request id (IO events) or MASKED; TIME_CLASS = absolute bucket index (D8), constant granularity within a condition, **maskable** *(v0.2)*: the base truncation condition masks it (offset-unanchored, §2b–c) and the anchored condition unmasks it — same schema, same vocabulary, model claims only by coarsening or promotion per §2e.

**Projection table (content rungs).** M = MASKED.

| Rung | EVENT_KIND | ACTOR | OBJECT | RELATED | LINEAGE |
|---|---|---|---|---|---|
| r1 actor-only | ✓ | ✓ | M | M | M |
| r2 +object | ✓ | ✓ | ✓ | M | M |
| r3 +related | ✓ | ✓ | ✓ | ✓ | M |
| r4 +lineage | ✓ | ✓ | ✓ | ✓ | ✓ |
| ctrl-irr | ✓ | ✓ | ✓ | ✓ | decoy per D2 refinement |
| ctrl-red | r4 under FIFO world (Part I D10) | | | | |

RELATED per kind — BLOCK: current owner. RELEASE: woken thread (or M if none). IO_COMPLETE: M (the completing request is LINEAGE's job — keeping the related-entity and lineage increments disjoint, per D2's one-kind-of-information-per-rung requirement). DISPATCH: M in M1 (no CPU identity). STEP/IO_ISSUE: M.

**Order modes (D8):** each content rung crosses with order mode ∈ {ordered, shuffled}, both bucketed at size $k$, delivered at bucket boundaries, queries scored at boundaries only. Ordered: identity serialization, deterministic projection $\pi_r$. Shuffled: uniform within-bucket permutation — a stochastic kernel $\Pi_r(O_b \mid E_{bk+1:bk+k})$ whose likelihood of a visible sequence is $m/k!$ where $m$ is the number of permutations of the latent bucket producing it (duplicate records make $m > 1$). The filter multiplies world-path probability by this channel likelihood; it never assumes uniformity over causally possible latent orders.

## §5 Queries: signatures, evaluation times, computation

Evaluated at bucket boundaries $t$ (§4). All are exact posteriors under the observation model of the condition.

- **Q1$(l)$:** $\mathbf{own}[l] \in \{1..n_T\} \cup \{\mathrm{FREE}\}$. State predicate.
- **Q2$(i)$:** $\mathbf{st}[i]$, full six-value enum (TERMINATED included). State predicate.
- **Q3$(dev)$:** the ordered in-flight list $\in \mathrm{Req}^{\le d}$. State predicate.
- **Q4:** the thread *directly* woken by the first wake-causing transition in $(t, t + W]$ — for a completion, the issuer of the departing request; for a release-with-waiter, the woken head. Secondary wakes (QUEUE_BLOCKED threads freed by the same completion, §3.3) are excluded, keeping the value single-valued. Value in $\{1..n_T\} \cup \{\mathrm{NONE\_WITHIN\_W}\}$, horizon $W$ a fixed parameter. **Computation** *(Part II item 9)*: finite-horizon forward sum over the belief-state–conditioned kernel — for each support state, a $W$-step absorbing computation where absorption = first wake event, tagged by woken thread; cost $O(W \cdot |\mathrm{supp}| \cdot b)$ ($b$ = branching), budgeted separately from the forward filter and reported in the M1 report. *(Q4 is the query whose entropy has an irreducible term under exact state knowledge — Part I D1 correction; both terms reported.)*
- **Q5$(i_b, i_r)$:** predicate — $\exists l:\; i_b \in \mathbf{wq}[l] \wedge \mathbf{own}[l] = i_r \wedge i_r \in \mathbf{run}$. Evaluated over ordered pairs; C1 can satisfy it for several pairs simultaneously (the Part I singular phrasing is a simplification, per review round one).

**Predictive-state targets (added with Part I v0.2.3, restoring proposal §3.2/§5.4).** Alongside the fact posteriors, the exact-inference component computes, per condition:
- **P-next:** the Bayes-optimal next-record distribution $P(O_{t+1} \mid h_t)$ under the condition's observation model.
- **P-horizon:** a preregistered finite test set $\mathcal{T}$ of future-observation functionals — for M1: the distribution of the next $m$ EVENT_KINDs; the identity of the next IO_COMPLETE's LINEAGE (where exposed); and the time-to-next-wake distribution truncated at $W$ — each computed exactly by finite-horizon forward sum over the belief-conditioned kernel ($m$, and $\mathcal{T}$ itself, frozen with the budgets in §7).
- **Divergent-history search:** enumeration (C0 family) and guided search (C1) for history pairs with equal P-next but unequal P-horizon on some $\tau \in \mathcal{T}$ — the immediate-agree/later-diverge classes that the exposure experiments require. Their existence, prevalence, and the interfaces under which they arise are an M1 exit deliverable (Part I deliverable 5); predictive equivalence ("histories inducing the same distribution over all futures") is the quotient these tests probe from the finite side.

## §6 Operational definitions

- **Arithmetic:** exact rationals end-to-end (Python `fractions.Fraction` or equivalent). No floats in the filter, enumerator, or any ceiling.
- **Bit-for-bit:** exact rational equality of every posterior entry. *(Part II item 10:)* numerator/denominator bit length is recorded per step alongside support size, peak memory, and wall clock — a filter can grow expensive at constant support.
- **Enumerator independence:** the validation enumerator is a separate implementation building the explicit trajectory tree (depth-first over all stochastic choices to horizon $H$), sharing no filtering code with the recursive filter; shared code is limited to the state tuple and kernel definitions themselves, which both must consume from one machine-readable specification.
- **Exhaustive (C0 family):** all histories to fixed horizon $H$ (parameter, frozen with budgets), plus sampled spot-checks beyond $H$. Belief-closure enumeration is used instead where a closure proof is cheap; otherwise horizon semantics apply.
- **Entropy:** Shannon, bits, computed exactly from rational posteriors (log₂ evaluated at report time in floats — presentation only, never inside the filter).
- **Incremental information of a rung:** ceiling difference on a named query between adjacent rungs at matched context, per D2.
- **Rung collapse (numerical criterion):** adjacent rungs r, r′ collapse at context $L$ if $\max_{q \in Q}\, [H_r(q \mid L) - H_{r'}(q \mid L)] < \delta$ bits, with $\delta$ frozen alongside budgets before any curve is computed.
- **Synchronization horizon:** smallest $L$ at which a rung's posterior entropy on a query falls below $\delta_{sync}$ (frozen likewise).

## §7 Budgets (placeholders to be frozen from benchmarks, before curves)

Per the D4/D9 precedence rule: benchmark the filter on C1-scale states first, then freeze — max support count $N_{supp}$, peak memory $M_{max}$, wall-clock per filtering step $\tau_{max}$, rational bit-length alarm threshold, enumeration horizon $H$, and $(\delta, \delta_{sync})$. The freeze is a stamped commit *preceding* the first observability curve. This document deliberately does not guess the numbers.

## §8 Dependency pinning

- Part I: `docs/yupana-m1-spec-draft.md` @ v0.2.3, commit `00ef2a7`.
- Exposure-gap note: `docs/exposure-gap-note-v0.1.md` @ commit `60cd340` (stamped b2ccffe).
- Proposal: `docs/what-the-trace-surrenders-proposal-v0.2.md` (v0.2, 2026-08-11).
- CLAUDE.md as of commit `0e50bc2`.
- arXiv: 2405.15943, 2602.02385, 2602.14814, 2602.23164, 2603.20531, 2607.17060, 2607.19379, 2512.22471, 2604.05469, 2002.10689.
- Episode external-validity claim: Chutani et al., "The Episode File System," USENIX Winter 1992; production-lineage claim (Episode as the basis of the z/OS POSIX file system) per Tony Mason, co-author, 2026-08-12 — *implementation-time task: replace with a citable IBM zFS heritage reference.*

## §9 Interface-witness test suite (Part II item 12)

Machine-checkable witness histories, each an executable test asserting an exact-posterior property:

Symmetric witness quality is required (Part I v0.2.3): witnesses 1–3 must each be a **history class surviving beyond a single handcrafted transition** — established by enumeration over C0-family histories, reporting the fraction of histories at horizon $H$ where the field moves the posterior — so that no single rung (lineage included) becomes the protagonist by construction.

1. r2 > r1: a history class where OBJECT changes Q1's posterior.
2. r3 > r2: a history class where RELATED (owner on BLOCK) changes Q1/Q5's posterior.
3. r4 > r3: a stochastic-world history class where LINEAGE changes Q3's posterior.
4. ctrl-irr: the decoy field changes **no** query ceiling (exact zero, not approximately).
5. ctrl-red: FIFO-world lineage changes no ceiling at full context.
6. Crossover: the same FIFO-world history under truncation — lineage changes a ceiling.
7. Shuffled channel: a bucket with two noncommuting events where order mode changes a posterior; filter validated against hand-computed channel likelihood, including a duplicate-record bucket ($m > 1$).
8. Reachability: no lock-cycle state reachable under I6-conforming workloads (C0 family, exhaustive).
9. Q4 decomposition: a history exhibiting $H(Z) = H(Z \mid S_t) > 0$ at full observability (the irreducible term isolated).
10. Divergent histories: a pair with equal exact next-record distributions and unequal P-horizon on some $\tau \in \mathcal{T}$ (§5) — the exposure experiments' raw material, witnessed before any training.
11. Predictive rung discrimination: an adjacent interface pair distinguished by a P-horizon test while all Q1–Q5 posteriors are unchanged — the D2 disjunctive clause (b) exercised, proving the query suite alone does not define interface value.

## §10 Hazard-audit scope (Part II item 11)

The D6 audit covers, per scheduler condition and order mode: absence of group-word-problem/permutation-composition subproblems in the belief update; posterior-support size; probability aggregation/normalization depth; numerical precision demanded by query outputs; within-bucket permutation marginalization cost (grows as $k!/\prod(\text{dup multiplicities})$ — $k$ must stay small, which is also an interface-design fact worth reporting); Q4's hitting-time computation; and working memory as a function of context horizon.

---

## Decisions made here that most deserve attack

1. **Anonymous CPU slots** (§1) — quotients away per-CPU identity. Cheap now; wrong if CPU identity ever becomes semantic.
2. **Dispatch priority over execution** (§3.1) — work-conserving, shrinks reachable space, but means dispatch order and execution order never compete stochastically.
3. **FIFO wake with direct handoff** (§3.5) — zero lock-subsystem entropy by design; the argued trade is attribution cleanliness for D10.
4. **Blocking on full queue re-executes the issue** (§3.3) — simplest semantics; creates a BLOCK record whose OBJECT is a device.
5. **IDLE records** (§3.6) — makes completion timing visible at all rungs as gap length; an alternative world would coarsen that too.
6. **Known-offset truncation windows** (§2) — models lost history, not lost clock.
