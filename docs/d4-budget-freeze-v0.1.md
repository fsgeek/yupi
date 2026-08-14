# D4 Budget Freeze — v0.1

**v0.1 — 2026-08-14.** Drafted by the day-five instance. Status: **frozen,
binding** per Part I's D4/D9 precedence rule ("the D4 budget itself … is
frozen from hardware benchmarks **before** any observability curve is
computed, preserving the preregistration discipline"). As of this commit,
no **C1** support-growth or observability curve has been computed anywhere
in the repository; the harness generates pricing states by
world-reachability BFS only, consulting no observations and no rungs.
*(Precision added v0.1.1, truthsayer round: the window-prior experiments
on worlds A/B predate this freeze, so "before any observability curve" is
true only C1-scoped — which is the scope D4 governs.)* Measurements: commit
8de5564 (`src/yupi/benchmark.py`, `scripts/d4_budget_benchmark.py`, raw
sweep in `docs/d4-pricing-raw-2026-08-14.json`; 9 harness tests, suite 60
green).

**Hardware/software:** AMD Ryzen Threadripper 3990X (64 cores / 128
threads), 256 GB RAM, CPython 3.14.3, x86_64 Linux (WSL2). Single-process,
single-threaded measurements; exact `Fraction` arithmetic throughout.

## Measurements

**Filter path** (`filter.step`, dynamometer world 5T/2CPU/2L/1D, ε=1/2,
stochastic discipline, rung r1 — the sparsest, binding condition):

| support | transitions expanded | wall s (median of 3) | peak MB | s per 1k transitions |
|---|---|---|---|---|
| 1 | 5 | 0.0001 | 0.0 | 0.0111 |
| 10 | 33 | 0.0004 | 0.0 | 0.0126 |
| 100 | 263 | 0.0040 | 0.0 | 0.0151 |
| 1,000 | 2,930 | 0.0416 | 0.1 | 0.0142 |
| 5,000 | 14,951 | 0.2076 | 0.5 | 0.0139 |
| 20,000 | 59,251 | 0.8310 | 1.5 | 0.0140 |
| 50,000 | 145,546 | 2.0868 | 3.8 | 0.0143 |
| 100,000 | 283,593 | 4.0349 | 6.4 | 0.0142 |

Cost is linear in expanded transitions at **~14 ms per 1,000 transitions**
(stable 0.0139–0.0151 across four orders of magnitude); memory is linear
and negligible at this scale. Mean branching in the pricing states: ~2.9
transitions per support state.

**Enumerator path** (`enumerator.paths`, C0a): **~3 µs per path-tick** at
shallow horizons (H ≤ 48), degrading to ~5–6 µs at deep horizons — the
degradation is the enumerator's O(H²) record-list copying (`recs +
[record]` per recursion), a known cost accepted for that module's
deliberate structural independence from the filter. Incidental finding:
C0a's path count grows only *linearly* beyond termination (the IDLE
self-loop carries mass without branching), so C0a alone cannot stress the
enumeration budget; branching worlds at shallow horizons are the binding
regime, where path count is exponential and dominates.

## The frozen budget

Declared tolerances (choices, stated here once; everything after is
measurement):  per-step filter latency ≤ 1 s; per-posterior enumerator
validation ≤ ~60 s; per-process memory sized to allow ≥ 24 concurrent
history-sampling workers in 256 GB.

- **B1 — Max support per filtering step: 20,000 states** (measured 0.83
  s/step there; the 1 s tolerance at ~14 ms/1k transitions and ~3
  transitions/state). Equivalently **≤ 70,000 expanded transitions per
  step**, which is the quantity the cost actually tracks — a world with
  higher branching hits the budget at proportionally smaller support.
- **B2 — Peak memory per filtering process: ≤ 8 GB.** Measured usage is
  ~three orders of magnitude below this; the ceiling is parallelism
  headroom, not a fitted number.
- **B3 — Wall-clock per filtering step: ≤ 1 s** at or below B1. A
  measured step exceeding 1 s within B1's support bound is a *finding*
  (branching or Fraction-denominator growth beyond the dynamometer's
  regime), to be reported, not silently absorbed.
- **B4 — Enumeration budget (validation path): ≤ 10⁶ paths per
  posterior check at horizons ≤ 24** (~10⁷ path-ticks ≈ 60–120 s
  measured). Full validation suites should stay under ~15 minutes.

**Binding consequence (Part I D4):** if C1's reachable support under the
actor-only rung exceeds B1/B4 at the horizons the M1 characterization
needs, **the world shrinks — not the ladder.** The ε selection rule is
D9's: largest ε satisfying budget and rung separation; if none, shrink C1.

## Caveats recorded at freeze time

1. The dynamometer's ~2.9 mean branching is a property of its pricing
   states; C1's true branching under contention may differ. B1 is
   therefore stated in both support and transition units, and the
   transition form governs on any conflict.
2. Timings are single-process CPython; history-sampling parallelism (up
   to the B2-implied ~24+ workers) multiplies throughput, not per-step
   latency. The budget binds per process.
3. Fraction-denominator growth was not separately stress-priced: the
   uniform pricing beliefs keep denominators small. If C1 posteriors
   develop large denominators, B3 is the tripwire that surfaces it.
4. The enumerator's O(H²) copying means deep-horizon validation is
   disproportionately expensive; validation designs should prefer
   branching-rich shallow histories, which are also the informative ones.
