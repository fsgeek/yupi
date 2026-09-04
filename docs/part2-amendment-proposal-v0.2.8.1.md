# Part II amendment proposal — v0.2.8.1 (looping programs: pc modulo the body; revised after cross-family review, with the clause built and priced)

> **Status (2026-09-04): PROPOSED — revised from v0.2.8 after the Codex
> review of 2026-09-04 (`part2-v0.2.7-v0.2.8-codex-review-2026-09-04.md`,
> verdict AMEND BEFORE ENACTMENT); awaiting a second review, then PI
> enactment.** Written by the instance of 2026-09-04, which built the clause
> behind a wrapper type the same morning (TDD-first, 15 executable controls
> written before the kernel changed; suite green) and priced the looping
> C1′ on the producer as it actually runs. v0.2.8 is retained with a
> pointer to this file. Every review finding is adopted or answered by a
> named check; none was declined. Every committed configuration is
> straight-line and every committed number is unchanged (suite: 354 passed
> after the kernel edit, before today's new tests were added).

## Why *(as v0.2.8, corrected per [10], [11])*

The window-process recursion's cost is reachable states × windows, and an
unrolled nonterminating world multiplies its reachable state space by the
unrolling count for no dynamical reason. Measured (exact replay, now
retained in the pass-pricing raws' `states_per_tick`): C1′-unrolled has
5,054 reachable states at tick 32 and 14,370 at tick 48; C1 has 317 and
185 at those ticks and peaks at 482 (tick 21) — the earlier "C1 ≤ 456" was
the table's entries, not a global bound. Folding the counter is expected to
shrink the state space by *at most* the product of unrolling counts
(5 × 4 × 5 × 5 = 500 for C1′); the measured factor is smaller and is
reported below, not assumed. "Keeps threads alive" is overwhelmingly but
not exactly true of the unrolled pilot (ε = 1: P(any thread terminated by
tick 48) ≈ 7.6 × 10⁻⁶); of the looping world it is exact.

## Clause 1 — a program may be declared looping *(restated per [1], [2], [3])*

§2 (programs): a program is a finite nonempty instruction tuple, optionally
**looping**. Define, per thread $i$ with program $P_i$:

- $\mathrm{advance}_i(pc) = (pc + 1) \bmod |P_i|$ if $P_i$ is looping, else
  $pc + 1$;
- $\mathrm{done}_i(pc) \Leftrightarrow \neg\,\mathrm{loop}_i \wedge pc = |P_i|$.

§3: the kernel writes $pc_i \leftarrow \mathrm{advance}_i(pc_i)$ at exactly
**five** sites — STEP (COMPUTE), successful ACQUIRE, the releasing thread on
RELEASE, the directly handed-off waiter on RELEASE, successful IO_ISSUE —
and tests $\mathrm{done}_i$ wherever it decides RUNNABLE versus TERMINATED,
including §3.4 completion, **which inspects and does not advance**. (v0.2.8
listed a "completion path" among the advance sites and an implementation
note said eight; both were wrong.) A looping thread is never TERMINATED;
$\mathrm{done}_i$ is identically false for it.

§1 erratum surfaced by the review: §1 says "$pc = |P|$ means TERMINATED",
but after a final IO_ISSUE the thread sits at $pc = |P|$ IO_BLOCKED until
completion (§3.4 already acknowledges this). Restate §1 as: $pc = |P|$
means the program is exhausted; the status becomes TERMINATED at the first
transition that would otherwise make the thread RUNNABLE. No number
changes; this is the kernel's existing behaviour named correctly.

**Invariants** (`PC_RANGE`, checked when the invariant checker is given the
programs, since the state carries no lengths — the checker's signature
gained an optional `programs` argument): a looping body is nonempty;
looping: $0 \le pc < |P|$ and status ≠ TERMINATED; straight-line:
$0 \le pc \le |P|$; mixed looping / straight-line configurations are
permitted, and I3 (no TERMINATED lock owner) stays active for the
straight-line threads.

**I6 (per [4]):** `validate_lock_order` applies to the body as to any
program (increasing order while held, LIFO release, empty held set at body
end), enforced at the kernel boundary. Hence no lock crosses a wrap and the
global-order argument gives lock-cycle freedom exactly as before. It does
**not** give termination or starvation freedom, and the clause does not
claim either.

**Nothing operational assumes eventual termination (per [6]):** dispatch
and idle depend on enabled work and device queues; simulator and enumerator
run to fixed horizons; the endpoint prior is uniform on a fixed grid; Q4
and every τ use finite W with NONE_WITHIN_W. **The continuation rule
(v0.2.4) needs no restatement (per [7]):** the loop flag is part of the
fixed kernel configuration, so the kernel is time-homogeneous either way;
this sentence is the cross-reference.

**Implementation (built 2026-09-04, exploratory until enactment):**
`yupi.programs.Loop(body)` — indexes, lengths and iterates as the body;
equality and hash include the flag so a Loop and its body never collide in
a cache keyed by programs; `is_looping()`; `kernel._advance` / `_done`
replace the five sites and every done-check; `state.check_invariants(...,
programs=None)`; `c1_prime_loop_programs()` (the pilot's four bodies
folded) registered as `YUPI_PROGRAMS=c1prime-loop`. No enumerator, filter
or recursion code changed.

**Executable controls (per [5]; `tests/test_looping_programs.py`, 15
tests, all written before the kernel edit and watched to fail):** wrap at
COMPUTE, at RELEASE, at IO_ISSUE with completion waking RUNNABLE where the
straight-line body would TERMINATE; the direct-handoff waiter advancing
past its ACQUIRE without terminating; a mixed configuration in which only
the straight-line thread terminates; PC_RANGE positive and negative cases;
an exhaustive reachable-set assertion that no looping thread ever has
$pc = |P|$ or TERMINATED, plus the same by mass over every path at horizon
8 (total mass exactly 1); the two-path gate (exact filter vs. path
aggregation) on a looping two-thread world at every rung; Loop ≠ body;
`c1prime-loop` is `c1prime` folded, and its entire reachable set is smaller
than the unrolled world's tick-48 slice.

## Consequence for D4 — erratum restated on the producer's unit *(per [8], [9])*

B4′ is stated in paths per aggregation pass and 2 GB RSS per process
(E2: 4 GB for D8 builds), and those rules stand unchanged for the path
side. The recursion's producer is `window_law_aggregates()`: **one r4
recursion per (law, ε), every coarser rung materialized by projection**;
there is no per-rung recursion for a per-rung rule to bind. The erratum
therefore binds **a pass**:

> A window law is admitted on the recursion iff one
> `window_law_aggregates()` pass per ε — the r4 recursion plus all
> requested projections — has maximum live (state, window) pair count
> ≤ 2 × 10⁶ and whole-process peak RSS ≤ 8 GB, priced on the target world
> with `scripts/window_process_pass_pricing.py` before any ceiling on that
> law is called statutory. A single-rung `window_law_aggregate()` pass is
> admitted under the same two numbers, stated as such. Path-side gates keep
> B4′ (≤ 1.5 × 10⁶ paths, ≤ 2 GB; E2 ≤ 4 GB for D8) where they are run.

**Corrected verdicts (per [9]):** v0.2.8 said the rule admits C1′-unrolled
(48, 6, 2). It does not: the raw has 1,650,623 pairs (under the line) and
9,703,432 KB peak RSS (over it), and the committed test
`tests/test_c1_prime_live.py::test_pricing_says_context_4_is_the_ceiling_unrolled`
asserts exactly that. Unrolled: (48, 4, 2) r1 single-rung admitted
(332,119 pairs, 2.03 GB); (48, 6, 2) **refused** on RSS; (48, 8, 2) refused.

**Looping C1′, priced 2026-09-04 on the pass unit** (raws
`window-process-pass-pricing-c1prime-loop-48-4-2-2026-09-04.json` and the
single-rung r1 raw beside it; ε = 1 and ½ each one pass):

| world | law | unit | ε | max live pairs | reachable states (max / tick 48) | wall | peak RSS |
|---|---|---|---|---|---|---|---|
| C1′-unrolled | (48,4,2) | r1 single-rung | 1 | 332,119 | 14,370 (tick 48) | 199 s | 2.03 GB |
| C1′-loop | (48,4,2) | r1 single-rung | 1 | 53,951 | — | 65 s | 0.17 GB |
| C1′-loop | (48,4,2) | r1 single-rung | ½ | 53,951 | — | 82 s | 0.21 GB |
| C1′-loop | (48,4,2) | **pass (r4 → r0–r4)** | 1 | 68,733 | 1,973 / 1,973 | 79 s | 0.22 GB |
| C1′-loop | (48,4,2) | **pass (r4 → r0–r4)** | ½ | 68,733 | 4,231 / 4,231 | 100 s | 0.33 GB |

The fold factor at (48, 4, 2), ε = 1, is **6.2× on r1 pairs and 7.3× on
tick-48 states** — not 500×. The bound was a product of phases; the world
does not visit every phase combination. What the fold removes is also
visible in the ceilings: mean state entropy at r1 falls from 4.24 bits
(unrolled) to 2.46 (looping) and the largest r1 support from 7,337 states
to 165, because the unrolled number counted uncertainty about the
unrolling count, which no observer of the folded world is asked to resolve.
The two worlds' r1 window counts are close (7,289 vs 7,041). The looping
(48, 4, 2) pass is admitted with a factor of ~30 to spare on both lines.
**(48, 8, 2) is being priced at the time of writing and its row is
appended below when it lands, not assumed.**

## Considered and declined *(as v0.2.8, with the D6 attribution narrowed per [12])*

- Keep unrolling and buy memory — declined (state space grows with the
  horizon for no reason the world has; every ceiling would carry an
  artifact of the unrolling count, now measured: 1.8 bits of it at r1).
- A JUMP instruction — declined for M1 scope. D6 does not categorically
  exclude control flow; it excludes named hard belief-update structures
  (group composition, permutation tracking). The loop flag is declined-JUMP's
  smallest useful subset: no data-dependent branching, no identity
  computation.
- Nonterminating by restart — declined (RESET-like discontinuity
  mid-episode; confounds the open RESET-record question).

## Freeze decision owed separately *(per [13])*

Part I's exit clause does not say "three rungs distinct"; that is the D1
verdict's gloss. Whether the exit clause is evaluated at deep truncation
in a looping world, and at which (T_ep, L), is a **freeze decision the
researcher will make after the (48, 8, 2) pricing and the filter-side gate
on the looping world**, in its own stamped note — not in this clause. The
reviewer's candidate (64, 8, 2), both statutory ε, is noted: 12.5 % of
endpoints reset-visible, first context unreachable unrolled, and an
existing C1 (64, 8, 2) pricing to compare against. r0, if enacted, does not
substitute for separation within r1–r4 (v0.2.7.1 Clause 4).

## Review request (second round)

(i) whether the §1 erratum's restatement ("exhausted; TERMINATED at the
first transition that would otherwise make it RUNNABLE") matches every
path in `_execute_one` and `_completion_transitions`; (ii) whether the
pass rule should also cap the *materialized* aggregate size (windows ×
support) separately from live pairs, since RSS at the end of a pass is
dominated by the aggregates rather than the recursion dictionary; (iii)
whether `Loop` should be a `WorldConfig` field instead of a program wrapper
(the wrapper was chosen so that no producer signature changes and no cache
key can conflate the two forms).
