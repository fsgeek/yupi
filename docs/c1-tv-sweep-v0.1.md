# (δ_p, Δ_τ) sweep — how the divergent-history class depends on its thresholds (Part II v0.2.4 §C, sweep 3 of 3)

> **⚠ KERNEL ERRATUM (2026-08-20):** every number in this note was computed
> under the pre-d69fa87 kernel, whose direct-handoff defect made self-deadlock
> states reachable (adjudication: `docs/audit-adjudication-2026-08-20.md`).
> Status: **buggy-kernel exploratory**. Corrected-kernel raws and drift:
> `docs/corrected-kernel-rerun-v0.1.md` (qualitative structure survives;
> magnitudes drift ≤0.004 at T_ep=12, ≤0.041 at (14,4,2)). Machine-readable
> status: `docs/artifact-status.json`. This banner is an append-only marker;
> the original text below is unchanged.

> **No corrected-kernel rerun exists yet for this note's quantities** — queued (sweeps rerun before the second stamp, per the v0.1.1 sequencing).

**Working note v0.1 — 2026-08-15 (commit time in git; the eighth instance). Exploratory
sensitivity sweep; proposes a Δ_τ and a *treatment* of δ_p for the second stamped decision;
enacts nothing.** Script: `scripts/c1_tv_sweep.py T_ep L B out.json` → raw
`docs/c1-tv-sweep-{12-2-2, 14-2-2, 14-4-2, 12-12-2}-raw-2026-08-15.json`. Wall clock 13 s,
58 s, 3 min 0 s, 55 s.

## 1. What is being swept

Part II §5 (v0.2.4 §D form): $h, h'$ are **$(\delta_p, \Delta_\tau)$-divergent** if
$\mathrm{TV}(\text{P-next}(h), \text{P-next}(h')) \le \delta_p$ and for some
$\tau \in \mathcal{T} = \{$kinds2, ttw4, lineage4$\}$, $\mathrm{TV}(\tau(h), \tau(h')) \ge \Delta_\tau$.
Prevalence is pair_prob — the probability that two law-weighted window draws are divergent.
Day seven measured only the corner $\delta_p = 0$, exact equality, and found it a knife-edge.
This sweep computes the full pair_prob surface over $\delta_p \in \{0, 10^{-4}, 10^{-3},
3{\cdot}10^{-3}, 10^{-2}, 3{\cdot}10^{-2}, 0.1, 0.3\}$ × $\Delta_\tau \in \{10^{-4}, 10^{-3},
3{\cdot}10^{-3}, 10^{-2}, 3{\cdot}10^{-2}, 0.1, 0.3, 0.5\}$, per (law, ε, rung), plus the
mass-weighted CDFs of pairwise TV(P-next) and of $\max_\tau$ TV(τ), and the surface split by
which τ separates.

Method: windows → belief over final states → exact Fraction mixtures (P-next at the rung;
the three τ at m=2, W=4 as frozen in v0.2.4) → windows collapse to *classes* keyed by the
4-tuple of exact mixtures with their law mass (158–2452 classes per cell; the control has
489–937, i.e. ≤ states). Class pairs a<b weighted $2 m_a m_b$; within-class pairs have all
TVs zero and never qualify. TVs are floats over sparse dicts; the exact $\delta_p = 0$ corner
is computed separately from Fraction equality.

**Gate:** the exact corner reproduces `c1_predictive_targets.py`'s pair_prob to every printed
digit in all 24 windowed cells and the 8 control cells (relative difference 0.0 at 7 significant
figures; e.g. (14,4,2) ε=1 r4: 2.038390e-03 both; control ε=1 r1 1.510e-02 both).

## 2. The cells

### 2a. pair_prob versus δ_p at Δ_τ = 10⁻³ (all 24 windowed cells; control below)

| law | ε | rung | classes | δ_p=0 | 10⁻⁴ | 10⁻³ | 10⁻² | 3·10⁻² | 0.1 | 0.3 |
|---|---|---|---|---|---|---|---|---|---|---|
| (12,2,2) | 1 | r1 | 158 | 4.28e-06 | 4.28e-06 | 1.27e-05 | 7.21e-05 | 3.73e-03 | 5.89e-03 | 7.36e-02 |
| (12,2,2) | 1 | r2 | 179 | 4.41e-06 | 4.41e-06 | 4.29e-05 | 4.29e-05 | 3.75e-03 | 5.97e-03 | 7.01e-02 |
| (12,2,2) | 1 | r3 | 234 | 1.13e-05 | 1.13e-05 | 5.95e-05 | 8.61e-05 | 3.77e-03 | 6.04e-03 | 6.73e-02 |
| (12,2,2) | 1 | r4 | 240 | 1.13e-05 | 1.13e-05 | 5.95e-05 | 8.61e-05 | 3.77e-03 | 6.04e-03 | 6.73e-02 |
| (12,2,2) | ½ | r1 | 164 | 5.00e-08 | 3.19e-06 | 3.19e-06 | 4.27e-06 | 2.44e-04 | 2.82e-03 | 4.12e-02 |
| (12,2,2) | ½ | r2 | 185 | 5.00e-08 | 3.29e-06 | 3.29e-06 | 3.30e-06 | 2.48e-04 | 3.06e-03 | 3.89e-02 |
| (12,2,2) | ½ | r3 | 245 | 2.23e-05 | 2.77e-05 | 2.77e-05 | 3.91e-05 | 4.25e-04 | 3.01e-03 | 3.55e-02 |
| (12,2,2) | ½ | r4 | 255 | 2.23e-05 | 2.77e-05 | 2.77e-05 | 3.91e-05 | 4.25e-04 | 3.01e-03 | 3.55e-02 |
| (14,2,2) | 1 | r1 | 187 | 1.67e-05 | 1.67e-05 | 1.67e-05 | 3.63e-05 | 9.94e-04 | 6.86e-03 | 7.67e-02 |
| (14,2,2) | 1 | r2 | 210 | 1.67e-05 | 1.67e-05 | 1.67e-05 | 6.30e-05 | 1.04e-03 | 6.78e-03 | 7.19e-02 |
| (14,2,2) | 1 | r3 | 294 | 2.45e-05 | 2.45e-05 | 4.47e-05 | 1.19e-04 | 1.95e-04 | 6.74e-03 | 6.71e-02 |
| (14,2,2) | 1 | r4 | 313 | 2.52e-05 | 2.52e-05 | 4.54e-05 | 1.19e-04 | 1.96e-04 | 6.74e-03 | 6.71e-02 |
| (14,2,2) | ½ | r1 | 196 | 1.24e-05 | 1.24e-05 | 3.15e-05 | 3.52e-05 | 3.25e-04 | 2.37e-03 | 4.16e-02 |
| (14,2,2) | ½ | r2 | 219 | 1.24e-05 | 1.24e-05 | 3.15e-05 | 4.26e-05 | 3.34e-04 | 2.53e-03 | 4.05e-02 |
| (14,2,2) | ½ | r3 | 310 | 3.05e-05 | 5.01e-05 | 7.84e-05 | 1.78e-04 | 1.04e-03 | 2.06e-03 | 3.57e-02 |
| (14,2,2) | ½ | r4 | 337 | 3.05e-05 | 5.02e-05 | 7.85e-05 | 1.79e-04 | 1.04e-03 | 2.06e-03 | 3.57e-02 |
| (14,4,2) | 1 | r1 | 1454 | 1.16e-03 | 1.20e-03 | 1.58e-03 | 2.10e-03 | 2.97e-03 | 7.04e-03 | 4.22e-02 |
| (14,4,2) | 1 | r2 | 1549 | 1.38e-03 | 1.54e-03 | 2.07e-03 | 2.59e-03 | 3.19e-03 | 6.80e-03 | 3.86e-02 |
| (14,4,2) | 1 | r3 | 1627 | 1.70e-03 | 1.88e-03 | 2.44e-03 | 2.94e-03 | 3.43e-03 | 6.89e-03 | 3.68e-02 |
| (14,4,2) | 1 | r4 | 1606 | 2.04e-03 | 2.08e-03 | 2.46e-03 | 2.95e-03 | 3.44e-03 | 6.89e-03 | 3.68e-02 |
| (14,4,2) | ½ | r1 | 2041 | 7.95e-04 | 1.16e-03 | 1.22e-03 | 2.17e-03 | 4.33e-03 | 8.84e-03 | 5.89e-02 |
| (14,4,2) | ½ | r2 | 2261 | 9.49e-04 | 1.26e-03 | 1.31e-03 | 2.36e-03 | 4.55e-03 | 8.77e-03 | 5.84e-02 |
| (14,4,2) | ½ | r3 | 2447 | 9.73e-04 | 1.26e-03 | 1.30e-03 | 2.40e-03 | 4.81e-03 | 8.78e-03 | 5.74e-02 |
| (14,4,2) | ½ | r4 | 2452 | 1.04e-03 | 1.26e-03 | 1.30e-03 | 2.41e-03 | 4.81e-03 | 8.78e-03 | 5.74e-02 |

(The δ_p=0 column at Δ_τ=10⁻³ is slightly below the exact corner where near-identical τ
mixtures exist — e.g. (14,4,2) ε=½ r1: 7.95e-04 here vs exact corner 8.36e-04.)

Control (12,12,2), every rung, ε=1 / ε=½: pair_prob is **identical** at δ_p = 0, 10⁻⁴, …, 0.1
(1.51e-02 / 6.65e-03 at r1; 1.38e-02 / 6.16e-03 at r3–r4); at δ_p = 0.3 ε=½ jumps to 6.3e-02
while ε=1 stays 1.51e-02. At full context P-next is a function of the state, and distinct
states' P-next distributions are either equal or ≥ 0.1 apart in TV — there is no
near-equality to sweep through.

### 2b. Ratios pair_prob(δ_p)/pair_prob(0) at Δ_τ = 10⁻² (from the raw JSON, all 24 cells)

| δ_p | min | max | median (12,2,2) | median (14,2,2) | median (14,4,2) |
|---|---|---|---|---|---|
| 10⁻³ | 1.00 (14,2,2 ε=1 r1) | 65.9 (12,2,2 ε=½ r2) | 5.3 | 2.5 | 1.4 |
| 10⁻² | 1.36 (14,4,2 ε=1 r4) | 85.5 (12,2,2 ε=½ r1) | 9.7 | 4.7 | 2.1 |
| 3·10⁻² | 1.59 (14,4,2 ε=1 r4) | 4954 (12,2,2 ε=½ r2) | 850 | 34 | 4.4 |
| 0.1 | 3.30 (14,4,2 ε=1 r4) | 61114 (12,2,2 ε=½ r2) | 1352 | 267 | 8.3 |

The surface is non-decreasing in δ_p in every cell (checked). There is **no plateau in
δ_p**: the sensitivity is largest exactly where the exact corner is smallest (the ε=½ L=2
cells with corners of 5e-08), and even the most stable law ((14,4,2)) moves 1.4–2.7× by
δ_p = 10⁻² and 3.3–8× by 0.1.

### 2c. Δ_τ dependence

At δ_p = 10⁻², the ratio pair_prob(Δ_τ=3·10⁻²)/pair_prob(Δ_τ=10⁻³) is 1.00 in the twelve
(12,2,2) and (14,2,2) ε=1 cells, 0.96–0.99 in the four (14,2,2) ε=½ cells, and 0.70–0.91 in
the eight (14,4,2) cells (min 0.70 at ε=½ r1); the ratio at Δ_τ=0.1 is 0.62–1.00 across the
L=2 cells (0.62 at (14,2,2) ε=½ r1; 1.00 in the six (12,2,2) r1–r3 cells) and 0.58–0.87
in (14,4,2). At δ_p = 3·10⁻²: 0.97–1.00 for the L=2 cells, 0.60–0.86 for (14,4,2). Above 0.1 the surface falls steeply
everywhere (e.g. (12,2,2) ε=1 r1 at δ_p=3·10⁻²: 3.72e-03 at Δ_τ=0.3, 1.06e-05 at 0.5).

**Near-duplicate shelf.** At Δ_τ=10⁻⁴ the (14,2,2) ε=1 cells are 6.1×, 3.1×, 2.1×, 2.1×
(r1..r4) larger than at Δ_τ=10⁻³, and (14,4,2) ε=1 r2 is 1.06×; the other nineteen cells
are within 5%. These are pairs of windows near-identical in *every* mixture — beliefs
that differ by tiny mass — not divergent histories; Δ_τ's job is to exclude them, and
10⁻³ already does.

### 2d. Do near-P-next pairs diverge, or are they near-duplicates?

Share of pairs with TV_p ≤ δ_p that have $\max_\tau$ TV ≥ 10⁻³, at δ_p = 10⁻² / 3·10⁻² / 0.1:
(12,2,2): 0.99–1.00 in all eight cells; (14,4,2): 0.92–0.97 / 0.95–0.98 / 0.97–0.99;
(14,2,2): **0.16–0.67 / 0.60–0.92 / 0.95–0.98** — at (14,2,2) with δ_p ≤ 3·10⁻², a large
share of near-P-next pairs are near-duplicates in τ as well (this is the same population as
the shelf above). Mass of pairs with TV_p ≤ 0.03: 0.0002–0.0038 (L=2 laws), 0.0031–0.0049
((14,4,2)); ≤ 0.1: 0.0021–0.0090.

### 2e. Which τ separates (δ_p = 10⁻², Δ_τ = 10⁻²; masses overlap)

kinds2 and ttw4 are comparable in every cell (each is the larger in some cells); lineage4 is
the smallest of the three in **23 of 24** cells — the exception is (14,2,2) ε=1 r1
(kinds2 1.98e-05, lineage4 2.05e-05, ttw4 3.59e-05). At (14,4,2) ε=½ lineage4 separates
≈10× less mass than the other two (1.6e-04–1.8e-04 vs 1.4e-03–2.0e-03); at ε=1 ≈2.5× less.

## 3. What the sweep shows

1. **Δ_τ has a broad stability region with reported sensitivity; δ_p has no common stable
   plateau on the sampled grid.** *(v0.1.1 wording, truthsayer round 2026-08-16: "flat band"
   overstated a region that moves prevalence by up to 30% at (14,4,2); "no plateau" is a
   statement about the sampled grid.)* For Δ_τ ∈ [10⁻³, 3·10⁻²] the surface is flat to within
   4% in the sixteen L=2 cells (exactly flat in twelve) and within 30% in the (14,4,2) cells;
   below 10⁻³ it picks up near-duplicates; above 0.1 it falls in every cell. For δ_p there is
   monotone growth in every cell with no plateau, and the growth factor between δ_p = 0 and
   3·10⁻² ranges from 1.6 to 4954 across cells. Any scalar δ_p is a convention, and the reported prevalence would
   inherit that convention by orders of magnitude.
2. **The knife-edge is confirmed and located.** Day seven's "exact equality measures window
   resolution" is now quantitative: at (12,2,2) ε=½ r1 the exact-corner prevalence is 5e-08,
   and δ_p = 10⁻⁴ already lifts it to 3.2e-06 (64×). At (14,4,2) — more classes, more mass
   in near-equal P-next — the exact corner (≈10⁻³) is stable to within 2.7× up to δ_p = 10⁻².
3. **Loosening δ_p does not manufacture divergence out of duplicates** at (12,2,2) and
   (14,4,2) — 92–100% of near-P-next pairs there differ in some τ by ≥ 10⁻³ — but at
   (14,2,2) it partly does (16–67% at δ_p=10⁻²). Whether a δ_p-loosened class is "immediate-
   agree/later-diverge" or "nearly the same window twice" depends on the law.
4. **At full context the question is empty**: pair_prob is δ_p-invariant up to 0.1 in every
   control cell. Distinct states' next-record laws are ≥ 0.1 apart in TV when they differ.

## 4. Proposal for the second stamped decision

- **Δ_τ = 0.01.** Inside the flat band; one significant figure; excludes the near-duplicate
  shelf by 10×; robust to within 4% (L=2) / 30% ((14,4,2)) against Δ_τ ∈ [10⁻³, 3·10⁻²].
- **δ_p: do not freeze a scalar; freeze an axis.** Report the divergent class and pair_prob
  at δ_p ∈ {0, 10⁻⁴, 10⁻³, 10⁻², 3·10⁻²} with δ_p = 0 as the exact anchor *(v0.1.1: 10⁻⁴ added
  on the truthsayer's finding — the largest single departure from exact equality, 65.9× at
  (12,2,2) ε=½ r2, occurs already at 10⁻⁴; omitting it would hide where the knife-edge
  begins)* (M1 deliverable 5,
  *existence*, is discharged at δ_p = 0 already — the class is non-empty in every windowed
  cell). Rationale: no plateau exists to place a threshold in; a scalar δ_p would turn a
  measured sensitivity into a hidden convention. If Part II must name a single δ_p for the
  class *definition* used in later exposure experiments, δ_p = 0.01 is the least bad point
  (its ratio to the exact corner is 1.4–85 across cells — the smallest spread among the
  non-zero grid values above 10⁻³) — but that is a choice, and this note recommends the
  axis instead.
- These proposals are independent of sweep 1's δ = 0.01 and of sweep 2's δ_sync.

## 5. Caveats

1. Floats for TV; exact only at the corner. Any threshold ≥ 10⁻⁴ is far above roundoff.
2. Grid, not continuum: the "band" for Δ_τ is established at grid points 10⁻³, 3·10⁻³, 10⁻²,
   3·10⁻²; the surface between them was not sampled.
3. Classes, not windows: two windows in one class are treated as identical (they are, in
   every mixture); n_windows > n_classes in every cell (e.g. (14,4,2) ε=½ r4: windows 4698,
   classes 2452 — from the predictive-targets JSON and this run respectively).
4. Only three windowed laws and one control; T_ep ∈ {12,14}, L ∈ {2,4}. The (14,4,2)
   behavior differs from L=2 in kind (gradual Δ_τ decline, δ_p-stable corner), so L is the
   axis most likely to move these conclusions.

## 6. Ledger

Predictions before the run: (a) exact equality would be unstable to small δ_p — held,
by up to 64× at δ_p=10⁻⁴; (b) I expected some plateau in δ_p at "resolution scale" —
**not held**, no plateau anywhere; (c) I did not predict the near-duplicate shelf or that it
would be law-specific ((14,2,2) ε=1) — found on printing. Draft errors caught by the
mechanical cross-cell check: before writing, "lineage4 is always the smallest separator"
(23/24, one exception) and "the surface is flat in Δ_τ up to 0.1" (false: (14,2,2) ε=½ r1
is 0.62, (14,4,2) down to 0.58); after writing, three range sentences in §2c that lumped
the (14,2,2) ε=½ cells (0.96–0.99; 0.62 at Δ_τ=0.1) in with the exactly-flat ones and
mis-stated the (14,4,2) range (0.70–0.91, not 0.70–0.99). Five sentences wider than their
cells in one note; all caught by re-reading the printed ratios, none by attention while
writing.
