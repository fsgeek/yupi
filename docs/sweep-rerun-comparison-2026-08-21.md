# Corrected-kernel sweep rerun — comparison for the v0.3.1 reaffirmation decision

**Status: corrected-kernel exploratory.** Written 2026-08-21 09:25 PDT.
This is the sweep comparison the [Aug-20 handoff] queued (step 2): the three
Part II v0.2.4 §C sweeps rerun under the fixed kernel (direct-handoff erratum,
fix d69fa87), old-versus-new at every quantity
[threshold proposal v0.3.1](part2-threshold-freeze-proposal-v0.3.1.md) cites,
so the PI can reaffirm or reconsider that proposal. Per the fixed stamp order
(sweeps-exploratory → reaffirm → stamp → fresh held-out laws), nothing here is
confirmatory; the reaffirmation and stamp come after this document, not from it.

Producer: `scripts/c1_sweep_rerun_comparison.py` →
`docs/c1-sweep-rerun-comparison-2026-08-21.json` (machine-readable form of every
table below). Suite 113 green before and after the script changes.

## 0. Inputs — what was rerun and what was generated first

The corrected-raw inventory had three holes relative to the original 08-15 sweep
inputs; they were generated first (same scripts, corrected kernel, run date
2026-08-21):

- `c1-query-ceilings-12-12-2-corrected-2026-08-21.json` (control law, δ sweep input)
- `c1-q4-ceilings-12-2-2-W8-corrected-2026-08-21.json`
- `c1-q4-ceilings-14-4-2-W8-corrected-2026-08-21.json`

Then the sweeps:

| sweep | script | new artifact | inputs |
|---|---|---|---|
| δ_sync (2 of 3) | `c1_sync_sweep.py` (repointed) | `c1-sync-sweep-corrected-2026-08-21.json` | corrected query+Q4-W4 ceilings, (14, L∈{2..14}, 2); filenames recorded in the artifact's `inputs` field |
| δ (1 of 3) | `c1_delta_sweep.py` (repointed) | `c1-delta-sweep-corrected-2026-08-21.json` | corrected ceilings at (12,2,2), (14,2,2), (14,4,2), (12,12,2), W4+W8 where present; filenames recorded per law |
| (δ_p, Δ_τ) (3 of 3) | `c1_tv_sweep.py` (no repoint needed — it recomputes from the kernel) | `c1-tv-sweep-{12-2-2,12-12-2,14-2-2,14-4-2}-corrected-2026-08-21.json` | kernel at fix d69fa87 |

Both repointed scripts now read the latest `-corrected-*.json` per prefix and
record the actual filenames read inside their output JSON; the buggy-kernel
inputs and the scripts' prior form are in git history.

## 1. δ_sync sweep — unchanged at every decision point

- **L\*(δ_sync), all statutory queries: identical in all 48 grid cells**
  (2 ε × 4 rungs × 6 δ_sync values), and identical per-query at δ_sync = 0.01.
- **Measure-(b) horizons (truncation-conditional, §B1/B2): identical** —
  L\* = 12 (r1), 10 (r2–r4) at both ε, recomputed from both kernels' curves
  with the same code.
- **L-axis collapse horizons (§A): identical** — L\* = 10 (r1→r2), 8 (r2→r3),
  2 (r3→r4) at both ε under δ = 0.01.
- The §A knife-edge cell (ε=1, r2→r3, L=8) is **0.009985 under both kernels**
  (unchanged at 6 d.p.); it remains a knife-edge, and remains below 0.01.
- Max curve drift: **0.015476 bits** at (ε=1, r2, Q1[L0], L=2) — drift lives at
  short L, as in the ceilings rerun, and dies to exactly zero by L=12–14
  (the injectivity fingerprint).

## 2. δ sweep — one coverage change, at ten times the proposed δ

36 cells compared (all four laws, both W where the original had them; the two
W8 entries and the control law now have corrected counterparts).

- Max per-cell max-gap drift: **0.015388** at ((14,2,2), ε=1, r2→r3, W4).
- **Argmax (binding query): unchanged in all 36 cells.**
- **Collapse coverage: identical at every δ in the grid except δ = 0.1**, where
  ((14,2,2), ε=½, r2→r3, W4) newly collapses. δ = 0.1 is 10× the proposed
  value; at δ = 0.01 coverage is unchanged.
- §A band around 0.01: (0.003728, 0.049943) → **(0.003728, 0.046568)**.
  0.01 remains inside, one significant figure, as §A states.

## 3. (δ_p, Δ_τ) sweep — classes shifted, decisions untouched

The kernel fix changes which exact-mixture classes exist: class counts changed
in 26 of 32 (law, ε, rung) cells — largest at (12,12,2) (e.g. ε=1 r3: 535→489)
and (14,4,2). Despite that structural shift:

- Max pair_prob surface drift over all cells and grid points: **1.47×10⁻³**
  (at (14,2,2), ε=1, r4). Exact δ_p=0 corners move in the third decimal;
  the largest relative corner move is ≈ −8% at (14,4,2) ε=½ r1/r2, consistent
  in sign and size with the corrected-rerun's −10% divergent-mass finding.
- **v0.3.1 §C/§D claim re-checks, same code on both kernels** (this required an
  extraction fix noted in §4):

| claim | old (buggy) | new (corrected) |
|---|---|---|
| §C flatness at δ_p=10⁻², Δτ∈[10⁻³,3·10⁻²], the 16 L=2 cells: exactly flat / ≤0.5% / ≤4% | 7 / 12 / 15 | **7 / 12 / 15 (identical)** |
| §C max rel spread, L=2 cells | 0.0411 | 0.0411 |
| §C rel spread at (14,4,2) | 0.2990 | **0.2658 (improves)** |
| §D monotone in δ_p at Δτ=10⁻² | 0 violations | 0 violations |
| §D ratio pair_prob(10⁻²)/pair_prob(0) span | 1.36–85.5 | **1.37–85.5** |
| §D largest δ_p=10⁻⁴ jump | 65.9× at (12,2,2) ε=½ r2 | **65.9×, same cell** |
| §D full-context δ_p-invariance up to 0.1 | exact (spread 0) | exact (spread 0) |

## 4. Two wording findings about v0.3.1 §C — present on BOTH kernels

These are not kernel drift; they date from the original analysis and were found
because the re-check computes at full float precision:

1. **"exactly flat in twelve L=2 cells" is print-precision flatness.** At full
   precision 7 of 16 cells are exactly flat; 12 of 16 are flat to ≤0.5% — a
   count that matches the cited twelve exactly, consistent with the original
   count having been read from the sweep's printed 3-significant-figure tables
   (not re-verified against the original analysis steps). True under both
   kernels.
2. **"within 4% in the other four" is 4.11% in one cell** — also under both
   kernels. ("Within 30% at (14,4,2)" was 29.9% old — accurate — and is 26.6%
   corrected.)

Recommended: amend §C's evidence sentence to the exact-precision form
(7 exactly flat, 12 within 0.5%, 15 within 4%, all 16 within 4.2%; (14,4,2)
within 27%) when the proposal is reaffirmed. No number that binds a decision
changes.

## 5. Verdict offered for the reaffirmation

Every decision-bearing quantity v0.3.1 cites survives the corrected kernel
unchanged: all synchronization horizons on all three measures, all collapse
horizons, all binding queries, coverage at the proposed δ, the knife-edge cell
to 6 d.p., the §D ratio structure, and full-context δ_p-invariance. Drift is
confined to short-L magnitudes (≤0.016 bits) and to which exact-mixture classes
exist (pair_prob effects ≤1.5×10⁻³ absolute). The §C evidence sentence should
be re-worded per §4; nothing else in v0.3.1 needs to move.

Recommendation: **reaffirm v0.3.1 with the §4 wording amendment**, then stamp,
then generate fresh held-out laws for confirmation per the fixed order.

[Aug-20 handoff]: corrected-kernel-rerun-v0.1.md
