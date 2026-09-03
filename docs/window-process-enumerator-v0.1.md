# The window-process enumerator — exact window-law aggregation at horizons the path enumerator cannot reach

**v0.1 — 2026-09-03.** Instrument work, exploratory in status (no statute
touched; the D4 budget is re-priced below but not re-frozen). Built the
same afternoon the C1′ pilot (`c1-prime-pilot-note-v0.1.md`) showed that
every collapse measurement so far was a from-reset statement and that no
workload-side Part C intervention could be evaluated without an enumerator
that scales in the horizon. Module `yupi.window_process`; gate
`tests/test_window_process.py` (41 tests); pricing producer
`scripts/window_process_pricing.py`; raws
`window-process-pricing-{32,64}-{4,8}-2-r1-2026-09-03.json`,
`window-process-pricing-64-8-2-{r0,r4}-2026-09-03.json`. The two census
scripts accept `YUPI_AGG=window` and record it in their artifacts.

## 1. What it computes, and the firewall

The ceilings producers build one dictionary: for every endpoint T on the
law's grid, for every path to T, the key (RESET observed, projected
in-window suffix) accumulates the path's law mass on its final state. The
window-process recursion builds the identical dictionary by carrying the
joint law of (S_t, last-L projected records) forward one tick at a time
and applying the endpoint prior at each grid point. Its memory is the
number of distinct (state, window) pairs at a tick, which saturates once
t > L; the path enumerator's memory is the number of paths, exponential
in T.

It is a third exact implementation. It imports neither `window_filter`
(recursive mixture filtering per observed window) nor `enumerator` /
`window_enumerator` (brute-force path summation); it shares the world
definition and the law structure only. Its gate is bit-for-bit equality
with the path aggregation wherever both exist — the relation `filter`
bears to `enumerator`. The gate as committed: C1 (8, L, 2) for L ∈ {2, 4, 8},
all five rungs, both statutory ε; C0b (6, L, 1) both disciplines; C1
(12, 4, 2) with a pair-count check; and the committed (14, L, 2) corrected
ceilings artifacts at L ∈ {2, 10, 14} (window counts exact, mean state
entropies to 10⁻⁹). Both census scripts were rerun under `YUPI_AGG=window`
at (14, 4, 2) and produced their committed artifacts row for row.

Incidental cross-check: at (16, 8, 2) the recursion reports 122567 windows
at r1, the count in the held-out F1 ceilings artifact produced by path
enumeration on 2026-08-23.

## 2. Pricing (C1, corrected kernel, one core)

| law | rung | ε | windows | max (state, window) pairs | max support | wall | peak RSS |
|---|---|---|---|---|---|---|---|
| (16, 8, 2) | r1 | 1 / ½ | 122567 | 79510 | 54 | 10 s / 12 s | 0.24 / 0.43 GB |
| (32, 4, 2) | r1 | 1 / ½ | 9962 | 9996 | 292 | 8 s / 10 s | 0.09 / 0.15 GB |
| (32, 8, 2) | r1 | 1 / ½ | 675117 | 182938 | 214 | 122 s / 156 s | 1.5 / 2.8 GB |
| (32, 12, 2) | r1 | 1 | 14513064 | 3040459 | 39 | 1597 s | 23.7 GB |
| (64, 4, 2) | r1 | 1 / ½ | 10585 | 9996 | 300 | 12 s / 15 s | 0.09 / 0.15 GB |
| (64, 8, 2) | r1 | 1 / ½ | 734811 | 182938 | 220 | 155 s / 197 s | 1.6 / 3.0 GB |
| (64, 12, 2) | r1 | 1 | 16364901 | 3040459 | 45 | 1961 s | 25.1 GB |
| (64, 8, 2) | r4 | 1 / ½ | 1119952 | 206130 | 167 | 181 s / 227 s | 2.0 / 3.9 GB |
| (64, 8, 2) | r0 | 1 / ½ | 25855 | 35528 / 39779 | 531 / 702 | 32 s / 47 s | 0.24 / 0.48 GB |

The pair count saturates in t (9996 at L = 4 and 182938 at L = 8 for every
horizon ≥ 32), so cost is linear in T_ep at fixed L. L = 12 is feasible but
heavy — ~27–33 min and ~24 GB per ε; the ε = ½ runs at L = 12 were killed
by the chain's 3600 s per-law timeout and produced no artifact. Against
the D4 freeze (`d4-budget-freeze-v0.1.md`, B4′: ≤ 1.5 × 10⁶ paths and ≤ 2 GB
per aggregation pass): the pass count is now irrelevant; L ≤ 8 sits under
the RSS line at every horizon tried, L = 12 does not. A D4 erratum stating
the new unit (pairs, not paths) and an RSS line for L = 12 is owed before
any L = 12 ceiling at M1 scale is called statutory.

Path enumeration for comparison: 2.1 × 10⁶ paths at T = 16; at T = 32 the
count would be of order 10¹².

## 3. What the first numbers say (C1, r1, ε = 1; mean state entropy in bits / ambiguous law mass)

| L | T_ep = 14 (from reset) | T_ep = 32 | T_ep = 64 |
|---|---|---|---|
| 4 | 1.344 / 0.670 | **2.012 / 0.857** | 1.228 / 0.910 |
| 8 | 0.152 / 0.165 | **0.484 / 0.541** | 0.309 / 0.699 |
| 12 | 0.001 / 0.040 | **0.107 / 0.212** | 0.073 / 0.472 |

Mid-episode windows are harder than from-reset windows, as the pilot note
guessed: at horizon 32 the r1 observation gap at L = 8 is three times the
horizon-14 figure and at L = 12 a hundred times (0.107 against 0.001 bits).
"The world synchronizes by ten visible records" was a statement about
windows that start at, or two dropped instructions after, reset.

Horizon 64 is *beyond C1's life*: its sixteen instructions are spent by
roughly forty records, after which threads are TERMINATED and the trace is
IDLE, so late windows are certain and drag the means down while the
ambiguous-mass fraction (dominated by the cursor and dead-thread residue)
rises. C1 at T_ep = 64 measures a dead world; the C1′ programs exist for
exactly this, and can now be censused where their contention recurs.

The r0 → r1 → r4 step at (64, 8, 2): H(S) 1.714 / 0.309 / 0.217 (ε = 1) —
the identity rung's range persists at long horizon, and the r1 → r4 ladder
has 0.09 bits there against 0.04 at horizon 14 (r1 0.152, r4 0.109). Not a
ceiling claim; the deep-truncation census on the full ladder is running as
this note is written.

## 4. What changes in the plan

- The **M1-scale rerun** (map v4 blocking item 6) is unblocked as instrument
  work: every (·, L ≤ 8, 2) ceiling can be produced at any horizon in
  minutes; L = 12 in half an hour and 24 GB per ε.
- The **deep-truncation census** on C1 at T_ep = 32 comes before any
  program change (running); then the C1′ pilot at T_ep ≈ 64–96.
- The **two-path gate for M1-scale ceilings** needs a policy: the filter can
  validate any individual window at any horizon (it never enumerates), so
  the statutory gate at M1 scale is "every window through the filter" as
  before, with the recursion on the enumerator side instead of paths — no
  statute change, one sentence in the D4 erratum.
- The **held-out and exposure machinery** (`c1_query_ceilings.py`,
  `c1_q4_ceilings.py`, `c1_predictive_targets.py`,
  `w11_predictive_rung_search.py`) still build from `paths`; each gains the
  same `YUPI_AGG=window` switch when it is next run at scale — not done
  here, to keep this commit to the enumerator, its gate, and its price.

## 5. Not claimed

That the recursion's pair count stays bounded for every world (it is
bounded by reachable states × distinct windows; C1′ and larger worlds
must be priced); that the horizon-32 numbers above are statutory (ungated
per window; the L ≤ 8 ones will be, once the ceilings producer is
switched); anything about worlds other than C1.
