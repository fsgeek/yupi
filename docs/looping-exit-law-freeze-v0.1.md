# Looping exit-law freeze — v0.1 (2026-09-04)

> **Status: researcher's freeze decision, PROPOSED as the law on which the
> Part I exit clause is evaluated in the looping world.** Written by the
> instance of 2026-09-04 under the PI/researcher split (the researcher
> freezes laws and grid rules; the PI enacts statute and decides the shape
> of the question). It takes effect for measurement only after Part II
> v0.2.8.1 (looping programs, per-pass D4 erratum) is enacted, and no
> ceiling under it is statutory until the two-path gate named in §5 has
> run. Every number below is priced on the instrument as it runs today;
> nothing is assumed from a bound. Raws are cited per row.

## 1. The question

Part I's exit clause asks for "measurably distinct observability regimes
across rungs." Every committed evaluation of it is a from-reset statement
on C1 at horizon 14, where the ladder collapses by eight to ten visible
records because the world is dead by then (`deep-truncation-census-v0.1.md`;
`c1-prime-live-census-v0.1.md`). The looping world C1′ keeps the four
contention roles alive indefinitely. This note chooses the (T_ep, L, B)
law on which the clause is evaluated there, under the admitting rule of
v0.2.8.1's D4 erratum:

> one `window_law_aggregates()` pass per ε in a fresh process, frontier
> $\max_t |\mathrm{frontier}_t| \le 2 \times 10^6$ and peak RSS ≤ 8 GB
> (`ru_maxrss` / 10⁶).

Context 8 is the target because it is the first context the unrolled
world could not reach and the context at which the deep-truncation census
found every adjacent C1 pair above δ mid-episode. B = 2 throughout (the
committed bucket).

## 2. The priced ledger (looping C1′, `YUPI_PROGRAMS=c1prime-loop`, 2026-09-04)

| law | unit | ε | frontier | reachable states (max) | wall | peak RSS | verdict | raw |
|---|---|---|---|---|---|---|---|---|
| (32,8,2) | pass r4 → r0–r4 | 1 | 1,335,771 | 1,733 | 623 s | 6.77 GB | admitted | `window-process-pass-pricing-c1prime-loop-32-8-2-2026-09-04.json` |
| (32,8,2) | pass | ½ | 1,335,771 | 3,645 | 762 s | 6.81 GB | admitted | same |
| **(40,8,2)** | **pass** | **1** | **1,964,919** | 1,953 | 1,313 s | **7.21 GB** | **admitted** (frontier margin 1.8 %) | `…-40-8-2-2026-09-04.json` |
| **(40,8,2)** | **pass** | **½** | **1,964,919** | 4,173 | 1,637 s | **7.23 GB** | **admitted** | same |
| (48,6,2) | pass | 1 | 397,007 | 1,973 | 429 s | 1.30 GB | admitted | `…-48-6-2-2026-09-04.json` |
| (48,6,2) | pass | ½ | 397,007 | 4,231 | 533 s | 1.29 GB | admitted | same |
| (48,8,2) | pass | 1 | 2,223,674 | 1,973 | 2,302 s | 7.40 GB | refused (frontier +11 %) | `…-48-8-2-2026-09-04.json`, `…-eps1.json` |
| (48,8,2) | pass | ½ | 2,223,674 | 4,231 | 2,820 s | 14.35 GB (cumulative process) | refused | same |
| (48,8,2) | r1 single-rung | 1 | 1,623,016 | — | 1,761 s | 5.15 GB | admitted, r1 only | `window-process-pricing-c1prime-loop-48-8-2-r1-2026-09-04.json` |
| (48,8,2) | r2 single-rung | 1 | 1,623,016 | — | 1,753 s | 5.37 GB | admitted, r2 only | `…-r2-…` |
| (48,8,2) | r3 single-rung | 1 | 1,623,016 | — | 1,755 s | 5.41 GB | admitted, r3 only | `…-r3-…` |
| (48,4,2) | pass | 1 / ½ | 68,733 | 1,973 / 4,231 | 79 / 100 s | 0.22 / 0.33 GB | admitted | `…-48-4-2-2026-09-04.json` |

Three facts the ledger establishes, none assumed before it was run:

1. **The frontier is bound by windows, not states, and does not depend on
   ε.** The frontier is identical at ε = 1 and ε = ½ for every law although
   ε = ½ reaches about twice the states. The actor-only window set
   *saturates by T_ep = 32* (794,808 windows at 32; 819,073 at 40 and at
   48); the frontier still grows with T_ep because more (state, window)
   pairs are reached, not more windows.
2. **OBJECT and RELATED never split a (state, window) pair; LINEAGE does.**
   The r1, r2 and r3 single-rung passes at (48,8,2) have the same frontier
   (1,623,016) with different window counts (819,073 / 923,461 / 991,585);
   the r4 recursion is 2,223,674. This is why the pass unit binds at r4.
3. **Folding the counter bought 6–7×, not 500×** (`part2-amendment-
   proposal-v0.2.8.1.md`), and it is the reason context 8 is reachable at
   all: the unrolled world refused (40,8,2) at 21.6 GB after 30 min.

## 3. Decision

**Primary law: (T_ep, L, B) = (40, 8, 2), both statutory ε ∈ {1, ½}, full
ladder r0–r4 from one pass per ε.**

Reasons, in order of weight:

- It is the **deepest horizon at which the full ladder at context 8 is
  admitted** under the rule, at both ε. (48,8,2) is refused on the r4
  frontier at either ε; the single-rung passes admit r1–r3 there but not
  r4, and a ladder without its top rung cannot evaluate the r3 → r4
  adjacency the D1 verdict named.
- It is **live**. Define recurrence as "some thread has ACQUIRED the same
  lock twice" (thread i's pc past the index of its second ACQUIRE of one
  lock: 3 / 4 / 4 / 4 in the unrolled bodies). Computed 2026-09-04 by exact
  forward marginal on the unrolled C1′ (whose dynamics coincide with the
  looping world's through tick 48 up to a terminated mass of 7.6 × 10⁻⁶;
  pinned in `tests/test_c1_prime_recurrence.py`): ε = 1 — 0.0085 / 0.118 /
  0.675 / 1.000 / 1.000 at ticks 16 / 24 / 32 / 40 / 48; ε = ½ — 0.0004 /
  0.026 / 0.583 / 1.000 / 1.000. **By tick 40 recurrence is certain to
  four decimals; by tick 32 it is two thirds.** (A differently defined
  table, 0.07 / 0.38 / 0.85 / 0.98 at 24 / 32 / 40 / 48, appears only in
  the commit message of `a73ece8` and is not cited.) Under the uniform
  endpoint prior most windows sit early in the episode whatever T_ep is;
  horizon 40 puts the later fifth of the endpoint grid entirely past the
  first same-lock re-acquisition, horizon 32 does not.
- The **state-entropy ladder is present at every step** at (40,8,2)
  (exploratory, recursion side, from the pricing raw): ε = 1 — r0 3.947,
  r1 0.601, r2 0.528, r3 0.405, r4 0.390 bits (steps 0.073 / 0.123 /
  0.016); ε = ½ — 3.371 / 0.296 / 0.240 / 0.177 / 0.166 (steps 0.056 /
  0.063 / 0.012). These are H(S), not the statutory query gaps; they say
  the ladder has something to measure, not what the clause will find.
- The **margin is thin and is stated as such**: 1.8 % on the frontier, 10 %
  on RSS. The rule admits the law; the margin means any change to the
  recursion's instrumentation (a memo, a different key encoding) requires
  a re-price before the law is called statutory. The freeze is of the law,
  not of the pricing.

**Secondary laws (reported beside the primary, never substituted for it):**

- **(48,6,2), both ε** — the deeper-horizon control at context 6, admitted
  with a factor of five to spare; distinguishes "horizon" from "context" if
  the primary's clause verdict is contested.
- **(48,8,2), r1–r3 single-rung, ε = 1** — the deepest context-8 object the
  rule admits; reported as three rungs, with the r3 → r4 adjacency
  explicitly *not measured* there.

**Exit-clause evaluation** under this freeze is on the content ladder
r1–r4, with r0 → r1 reported beside it as an added D2 adjacency; whether r0
counts toward the clause is the PI's decision at enactment of v0.2.7.1
(its Clause 4), and this note does not pre-empt it.

## 4. Considered and declined

- **(32,8,2) as primary.** Admitted with more margin (1.34 × 10⁶), but the
  window set is already saturated at 32, so the margin buys nothing on
  windows, and recurrence is two thirds by 32 against certain by 40.
  Declined; it remains a
  natural ε-sweep or held-out law because it is cheap.
- **(44,8,2).** Not priced. Interpolating the frontier between 40
  (1.96 × 10⁶) and 48 (2.22 × 10⁶) puts it over the line; that is an
  expectation, not a measurement, and it is recorded as such. If a deeper
  full-ladder law is ever wanted, price it rather than trust this line.
- **Moving the frontier line to admit (48,8,2).** Declined: nothing
  measured argues for a different line. The rule was proposed this morning
  from the instrument's actual cost; a law that fits it exists; moving the
  line to admit a preferred law is the argument from appearance the house
  rules exclude.
- **Freezing on the single-rung unit at (48,8,2).** Declined as primary
  because it cannot carry the r3 → r4 adjacency; kept as a secondary.

## 5. Owed before any ceiling under this law is statutory

1. **Enactment** of Part II v0.2.8.1 (the loop flag and the per-pass D4
   erratum) and v0.2.7.1 (r0 on the ladder) by the PI.
2. **The two-path gate at (40,8,2), both ε**: every window's posterior from
   `filter_window` compared with the recursion's aggregate, Fraction for
   Fraction. Policy: every window through the filter (819,073 at r1; more
   at r2–r4), cost dominated by support size (max 118 at r1–r4, 578 at r0
   at ε = ½). Price the gate on the 40 largest-support windows first, then
   run it in full under B2 (≤ 8 GB per filtering process). Any mismatch
   voids the law.
3. **Statutory producers on the recursion**: `c1_query_ceilings`,
   `c1_q4_ceilings`, `c1_predictive_targets` switched to the window-process
   aggregate with the gate above as their exactness check, extended to r0
   (v0.2.7.1's scope decision). Until then every number at this law is
   exploratory.
4. **A re-price** if any producer or instrumentation change touches the
   recursion (the 1.8 % margin).

## 6. Not claimed

That the exit clause is satisfied at (40,8,2); any statutory query gap;
that the H(S) steps above survive the query set; that (44,8,2) is refused;
that the 14.35 GB ε = ½ figure at (48,8,2) is an isolated-process peak
(it is a cumulative high-water mark, and is over the line either way).

---

## Addendum 2026-09-04 17:50 PDT — the gate priced, and scheduled

§5 item 2 said "every window through the filter; price it on the 40
largest supports first." Done, in three steps, each on the trace:

1. **Top-40 by support, filter as it stood** (raws
   `window-gate-c1prime-loop-40-8-2-{r4,r0}-2026-09-04.json`): 160/160
   exact, at 4.2–11.8 s per window. With 1,524,612 r4 windows that is
   hundreds of hours per ε — the policy was infeasible as written.
2. **Profile, then two exact memos** in the filter (commit `1451418`): the
   forward marginal μ_u was recomputed per offset per window (14.7 of 17 s),
   and after caching it the first Bayes step over all of μ_u dominated; both
   are pure functions of exact inputs and are now cached, with bit-identity
   and kernel-call-count tests. Nothing approximate entered the filter.
3. **A 1-in-100 stride sample at (40,8,2) r4 ε = 1 with the memos** (raw
   `…-r4-2026-09-04-stride100.json`): **15,247 / 15,247 exact, 84.3 ms per
   window**, 6.76 GB. Full r4 gate at this rate: 35.7 h per ε in one
   process.

**Schedule (researcher's decision):** the full gate runs sharded, 8
interleaved shards per (rung, ε) (`--shard i/8`, each shard rebuilding the
recursion — 22 min — and gating windows i, i+8, …), in the order r4 ε = 1,
r4 ε = ½, then r1, r2, r3, r0 at both ε; 8 × 6.8 GB fits the box with
headroom. Expected wall: r4 ≈ 5 h per ε; the whole ladder ≈ 2 days. Each
shard writes its own raw; a (rung, ε) is gated iff every shard reports zero
mismatches and the shard window counts sum to the recursion's total. No
ceiling under this law is called statutory until the (rung, ε) it needs is
gated. PIDs are recorded and killed by PID only; every shard runs under
`ulimit -v 20 GB`.
