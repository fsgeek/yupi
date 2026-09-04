# Part II amendment proposal — v0.2.8 (looping programs: pc modulo the body)

> **Status (2026-09-03): PROPOSED — awaiting cross-family review, then PI
> enactment.** Written by the instance that built the window-process
> enumerator and priced C1′ on it, the same day. One clause plus a
> consequence for D4. No projection, threshold, query, or frozen decision
> changes; every committed number is unaffected because every committed
> configuration is straight-line and remains so.

## Why

The instrument now evaluates the window law at any horizon for fixed
context (`window-process-enumerator-v0.1.md`), and the first deep look
(`deep-truncation-census-v0.1.md`) says the ladder's collapse was a
from-reset artifact. The measurement that matters next is a *live* world
at depth — threads that keep contending. C1 dies by tick 24–40. The
pilot world C1′ keeps threads alive by **unrolling** short bodies
(`c1-prime-pilot-note-v0.1.md`), which leaves the kernel untouched but
multiplies the reachable state space by the number of unrollings for no
dynamical reason: two threads whose program counters differ by one body
length behave identically, yet the recursion carries them as distinct
states. Measured: C1′ has 5054 reachable states at tick 32 and 14370 at
tick 48 against C1's ≤ 456; the recursion's pair count at (48, 6, 2) is
1.65 × 10⁶ (15 min, 9.7 GB per rung per ε) and context 8 is out of reach.
Folding the counter collapses the state space by roughly ∏ (unrollings) —
about 5 × 4 × 5 × 5 = 500 for C1′ — and makes the episode horizon a free
parameter of the law rather than a property of the programs.

## Clause 1 — a program may be declared looping

§3 (thread instruction semantics) gains one sentence and one flag:

- A program is a finite instruction tuple as now, with a per-program flag
  `loop ∈ {false, true}` (default false; every committed configuration is
  false).
- For a looping program, the advance rule `pc ← pc + 1` becomes
  `pc ← (pc + 1) mod |program|`, applied wherever the kernel advances the
  counter (STEP, ACQUIRE, RELEASE, IO_ISSUE, the woken thread's advance on
  RELEASE, and the completion path). A looping thread never reaches
  `pc = |program|` and is never TERMINATED; I3 is vacuous for it.
- `validate_lock_order` (I6) applies to the body exactly as to a
  straight-line program: every acquisition released within the body, in
  increasing lock order. Because the body ends with an empty held set, the
  wrap carries no lock across iterations and the I6 argument for
  deadlock-freedom is unchanged.
- The record stream is unchanged in form: a looping thread emits the same
  DISPATCH-then-instruction records as now, indefinitely. No new
  EVENT_KIND, no new field. Projections, queries, τ, the window law and
  the endpoint prior are untouched.

**State tuple:** unchanged (pc is already a component; its range for a
looping thread is {0, …, |program| − 1}). The invariant check gains
`PC_RANGE` for looping threads.

**Implementation shape (for the reviewer's judgment, not enacted here):**
`Program` stays a tuple; the flag lives in a parallel tuple on
`WorldConfig` or as a wrapper type, so that `_program_len` and the eight
advance sites take a `loop` predicate; the enumerator, filter and
window-process recursion need no change beyond consuming the kernel. The
two-path gates (filter vs. paths at short horizons; recursion vs. paths;
filter vs. recursion at long horizons) cover it as they cover everything.

## Consequence for D4 (erratum, owed alongside)

B4′ is stated in paths per aggregation pass; the recursion's unit is
(state, window) pairs. The erratum proposed with this clause: **≤ 2 × 10⁶
pairs and ≤ 8 GB per (ε, rung) recursion** as the admitting rule for a
law, priced on the target world before any ceiling on it is called
statutory; ≤ 1.5 × 10⁶ paths remains the rule for the path-side gate
where it is run. Under that line, C1′-unrolled admits (48, 4, 2) and
(48, 6, 2) and refuses (48, 8, 2); a looping C1′ is expected to admit
(48–96, 8, 2) — to be priced, not assumed.

## Considered and declined

- **Keep unrolling and buy memory.** Declined: the state space grows with
  the horizon for no reason the world has; every ceiling would carry an
  artifact of the unrolling count.
- **A JUMP instruction.** Declined for M1: general control flow is what
  the founding hazard audit (D6) excludes; a body-level loop flag adds no
  data-dependent branching and no identity computation.
- **Nonterminating by restart** (a thread that TERMINATES is re-created at
  reset state). Declined: it re-emits a RESET-like discontinuity mid-
  episode and confounds the RESET-record question still open for
  deliverable 2.

## Review request

Cross-family review before enactment. Specific questions: (i) whether
`PC_RANGE` and the wrap should be witnessed by an executable exact-zero
control (a looping thread's posterior over `pc` never places mass on
|program|); (ii) whether Part I's exit clause ("three rungs distinct")
should be evaluated at deep truncation in a looping world, and if so at
what (T_ep, L) — a freeze decision, not this clause; (iii) whether the
v0.2.4 rule "the forward sum continues the kernel past T_ep" needs
restating for looping threads (it does not appear to: the kernel is
time-homogeneous either way).
