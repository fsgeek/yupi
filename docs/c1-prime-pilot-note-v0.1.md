# C1′ pilot — recurring-contention workloads are unreachable at the instrument's horizon; the blocker is the enumerator, not the workload

**v0.1 — 2026-09-03.** Exploratory. Instance following the map-v4 author;
the second step of the Part C order chosen this afternoon (r0 first,
`r0-ladder-census-v0.1.md`; then this pilot). `yupi.programs` gains
`c1_prime_programs()` and `programs_for()` (env `YUPI_PROGRAMS`), both
exploratory; C1 and every statutory producer are untouched. Pins
`tests/test_c1_prime_pilot.py`. Corrected kernel, ε = 1 unless stated.
Numbers from the enumeration in-session.

## 1. What the pilot was meant to test

`c1-residual-ambiguity-census-v0.1.md` found the only rung-reachable
residual in C1 to be lock ownership, decaying with a half-life of one hold,
and recommended "structured nonterminating workloads with recurring lock
contention" as the intervention that acts on that mechanism. The pilot:
keep C1's world and its four contention roles, shorten and unroll the
bodies so every lock is re-acquired several times within the horizon, and
census the ladder along L.

C1′ programs (unrolled, straight-line; kernel and Part II §3 untouched;
I6 checked by `validate_lock_order`):

| thread | body × repeats | length |
|---|---|---|
| 0 | (acquire 0, release 0, io 0) × 5 | 15 |
| 1 | (acquire 0, acquire 1, release 1, release 0) × 4 | 16 |
| 2 | (COMPUTE, acquire 0, release 0) × 5 | 15 |
| 3 | (io 0, acquire 1, release 1) × 5 | 15 |

## 2. What the enumeration says (ε = 1)

| world | T | paths | E[Σ pc] (instructions executed, all threads) | max pc | E[#DISPATCH] | E[#ACQUIRE] | E[#BLOCK] | P(any thread re-acquires lock 0) |
|---|---|---|---|---|---|---|---|---|
| C1 | 8 | 2540 | 2.58 | 3 | 4.58 | 1.16 | 0.42 | 0 |
| C1 | 12 | 69210 | 3.99 | 4 | 6.24 | 1.57 | 1.13 | 0 |
| C1 | 14 | 308690 | 4.85 | 4 | 7.13 | 1.76 | 1.44 | 0 |
| C1′ | 8 | 2562 | 2.61 | 3 | 4.58 | 1.17 | 0.41 | 0 |
| C1′ | 12 | 76618 | 4.21 | 5 | 6.23 | 1.69 | 1.04 | 0.001 |
| C1′ | 14 | 396978 | 4.99 | 6 | 7.14 | 1.90 | 1.33 | 0.003 |
| C1′ | 16 | 2123762 | 5.86 | 7 | 8.06 | 2.07 | 1.60 | 0.005 |

Pricing at T = 14: 397 K paths, 11 s (ε = 1) / 19 s (ε = ½), 0.77 GB — the
same as C1. E[#TERMINATED] = 0 at T = 14 in C1′ (as intended).

**Reading.** In fourteen records the whole four-thread world executes
about five instructions, half the records are DISPATCH, and the chance that
any thread has acquired lock 0 twice is three in a thousand. At sixteen
records it is five in a thousand. The world's instruction throughput is
about 0.35 per record; for each of four threads to complete a
three-instruction body twice takes roughly seventy records. Recurring
contention does not exist at T_ep ≤ 16 in any C1-shaped world, whatever the
programs say. **The pilot is blocked by the horizon, not by the workload.**

## 3. What this means

1. **The ladder's collapse along L was measured in a world that has barely
   started.** Every (14, L, 2) window either begins at reset or drops at most
   twelve records, i.e. at most about four instructions. "The world
   synchronizes by ten visible records" is a from-reset statement. What a
   window dropped into the middle of a long episode sees — the prior over
   states is then something like a stationary law, not reset plus a short
   prefix — is unmeasured, and the census's per-endpoint evidence reaches
   only U ≤ 6 (H(S) at L = 8 is 0.38, 0.38, 0.30 bits at T = 10, 12, 14: flat
   in U over that short range, which says nothing about U = 40).
2. **No workload-side Part C intervention can be evaluated with the present
   enumerator.** Path enumeration is exponential in T (2.1 M paths at
   T = 16); the horizons where recurrence, exhaustion and mid-episode
   truncation live are T ≈ 50–100. The D4 budget (`d4-budget-freeze-v0.1.md`
   B4′: ≤ 1.5 × 10⁶ paths, ≤ 2 GB per aggregation pass) is already at its
   edge at T = 16.
3. **The prerequisite is an exact enumerator that scales in T for fixed L**:
   the window process — a forward recursion over (state, last-L projected
   records) per rung, exact rationals, with the endpoint law applied at the
   end. Its state space is reachable states × distinct L-windows, which for
   L ≤ 8–12 is the `n_windows` column we already know (tens of thousands to
   a few hundred thousand), independent of T. This is the M1-scale rerun's
   real content (map v4 blocking item 6), and it now sits above every
   workload-side intervention in dependency order. The recursive filter
   already computes exactly this per window; the enumerator side needs the
   same recursion run forward over all windows at once, with the
   independence firewall preserved (the two must not share code).
4. **The r0 result is unaffected** — it was measured at the same horizons as
   everything else and its range is identity, not contention.

## 4. Consequence for the Part C order (researcher's call)

Revised order: (1) window-process enumerator, priced under D4 at
T_ep ∈ {32, 64} for L ≤ 12 — instrument work, no statute change, the
two-path gate extended to cover it; (2) re-run the residual census and the
ladder at deep truncation (U ≫ L) on C1 *before* changing any program —
the collapse may already look different mid-episode; (3) only then the
C1′ pilot, at horizons where its programs recur. The v0.2.7 (r0) amendment
proceeds independently.

## 5. Not claimed

That mid-episode truncation restores the ladder (it might not; it is
unmeasured); that the window-process recursion fits the budget at L = 12
and T = 64 (to be priced); anything about C1′ beyond the throughput
table — its ladder was not censused because the census would have measured
C1 with different labels.

> **Pointer (2026-09-04 00:25 PDT):** the pilot did run, once the window-process enumerator existed: C1′ live-world census at (48, 4, 2) in `c1-prime-live-census-v0.1.md`, with the pricing that says context 8 needs the looping kernel proposed in `part2-amendment-proposal-v0.2.8.md`. §2–§4 above are preserved as written.
