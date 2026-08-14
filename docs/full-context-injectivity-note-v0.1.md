# Full-Context Injectivity of r1 — a theorem of the kernel, not a fact about C0 scale

**v0.1 — 2026-08-13.** Drafted by the day-four instance following C0c validation
(commit 30e2568), same-day computational check in scratchpad
`injectivity_check.py`. Status: **proposed for cross-family review**; if it
survives, Part I's grip language and Part II §9's witness scoping should cite
it rather than the C0-scale measurement. Nothing in the frozen specs is edited
by this note.

## Claim

**Theorem (full-context injectivity).** For every `WorldConfig` and every
program tuple, the map from length-n transition sequences out of
`initial_state` to their r1 projections (EVENT_KIND + ACTOR per tick) is
injective. Equivalently: every full-context posterior from reset is a point
mass, at every rung, for every configuration expressible in the current
kernel.

The August 13 C0-family losslessness measurement (C0a H=12, C0b H=10, C0c
asserted as `test_full_context_point_mass_expected`) is a corollary, not a
scale accident.

## Proof sketch

By induction on the trace. Base: the initial state is known (reset). Step:
suppose the state s before tick t is known. It suffices that (kind, actor)
identifies at most one transition in `enabled(s)`:

- **DISPATCH(i)** — puts i into `running`; cursor update is a deterministic
  function of the chosen thread (`(i+1) mod n_threads` when ε<1; never
  written at ε=1). Unique.
- **STEP / ACQUIRE / RELEASE / IO_ISSUE / BLOCK (i)** — the instruction
  executed is `programs[i][pc[i]]`, fixed by the known state; its effect is
  deterministic. BLOCK's two readings (lock-block vs queue-block) are
  disambiguated by that instruction, not by the masked OBJECT field.
  RELEASE's woken thread is the head of a FIFO wait queue whose contents are
  a deterministic function of the known state — RELATED is masked below r3
  but carries no information the history did not already fix. IO_ISSUE's
  request id is lowest-free, deterministic given visible issue order.
- **IO_COMPLETE(i)** — I5 (one in-flight request per thread) makes ACTOR
  identify the completed request under either completion discipline;
  LINEAGE is masked below r4 but determined.
- **IDLE** — unique self-loop.

The kernel's only stochastic choices are (which thread) and (completion vs
stage B), and both are emitted in the very next record's (kind, actor).
There is no unlabeled branch anywhere in the transition system. ∎

Three load-bearing dependencies, named so a future kernel change knows what
it is breaking:

1. **The D9 cursor canonicalization.** Under the pre-review cursor semantics
   (uniform picks not advancing the cursor), a uniform pick and a
   round-robin pick of the *same* thread produced identical (kind, actor)
   labels but different `rr_cursor` values — support 2 from one tick. The
   review fix that collapsed the cursor space is exactly what makes (kind,
   actor) a sufficient label at ε<1. The theorem is true *because of* that
   fix.
2. **I5 + lowest-free request allocation.** Relax either (multiple in-flight
   per thread, or randomized ids) and IO_COMPLETE's actor no longer names
   the request.
3. **Deterministic direct-handoff wake.** A stochastic wake policy (wake a
   uniformly chosen waiter) would be an unlabeled branch — RELATED masked
   below r3 would then carry real information. The current kernel has no
   such branch.

## Computational check (falsification attempt, survived)

Scratchpad `injectivity_check.py`, designed to kill the claim at its most
plausible failure point — multi-waiter wake ambiguity:

| world | shape | H | tree nodes | max support (r1–r4) |
|---|---|---|---|---|
| A | 3 threads / 1 CPU / 1 lock, both waiter orders reachable | 14 | 367 | 1 |
| B | 3 threads / 2 CPUs / 1 lock / 1 device | 14 | 2,758 | 1 |
| C | world A at ε = 1/2 (cursor dynamics live) | 12 | 287 | 1 |

## Consequences

1. **The August 13 memory's grip triage needs one correction.** It located
   future grip in "truncation axis, D8 shuffled channel, or C1 multi-waiter
   lock wake (transient ambiguity)". The third location is empty at full
   context: the wake is a deterministic function of history, so masking
   RELATED loses nothing to a full-context observer. C1's wake grips only
   through a *windowed/truncated* observer — which is what Part II v0.2.2
   already prescribes (witnesses 1–2 run over C1 *windows*), now with the
   reason made explicit: windows are not merely where those witnesses are
   convenient, they are the only place the witnesses can exist.
2. **C1 at full context is a predicted fourth zero.** Do not build C1
   expecting full-context rung separation; assert the point-mass expectation
   as a test there too (C0c precedent).
3. **The interface axis is degenerate at full context, everywhere.** All
   rung differences are exactly zero for every config — the interface
   ladder separates only under truncation, windowing, or the D8 shuffled
   channel (which breaks the induction by hiding within-bucket order — the
   one interface manipulation that attacks the induction step rather than
   the base). This sharpens proposal §6.2: full context is the zero of the
   context axis *and*, provably, of the interface axis.
4. **Part II §2's truncation machinery is now formally the critical
   path.** Every informational witness in the program waits on it.
   *(Correction, v0.1.1 — same-day review: the original wording called
   this an "open item," which was drift from a stale memory. Part II §2
   v0.2 already rules the truncation prior derived-not-stipulated and the
   base observer offset-unanchored over joint (U, S_U); what is critical
   is implementing that statute, not deciding it. See
   window-prior-experiment-note v0.3.)*
5. **The nondegeneracy gate (consequence 4 of the losslessness memory)
   cannot be discharged by any full-context configuration.** The bit-for-bit
   filter gate will carry its first support>1 belief only when window/
   truncation machinery exists. Until then the filter's fat-belief paths
   remain green-but-unexercised — the same genus, one level up.

## What would falsify this note

A kernel-expressible configuration and observation prefix with full-context
support > 1 at any rung; or a review finding a hole in the induction (the
BLOCK disambiguation and the ε<1 cursor argument are the two joints a
reviewer should attack first).
