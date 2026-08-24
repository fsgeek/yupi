# D10 truncated-window lineage verdict — v0.1

> **⚠ CORRECTED — read v0.1.1 at the end of this file.** As committed: the
> gate-2 cap contradicted "all six gates passed" (now uncapped, all 396
> windows verified); several preregistered outputs were missing (now in the
> v2 artifact); 54–63 % of the FIFO gain is offset-mixture amplification,
> separated in v0.1.1; the "C1 sits in the dead region" sentence is false
> (C1's cells are informative and collapsed); "order of magnitude over δ"
> reads 8.45×δ global / 100×δ per-history.

> **Status (2026-08-23 10:47 PDT): measured under preregistration
> `d10-lineage-search-prereg-v0.1.md` (stamp 080f937, before any
> posterior); truthsayer pass owed.** Producer:
> `scripts/d10_lineage_search.py` → `d10-lineage-search-2026-08-23.json`.
> All six §5 gates passed: full-context exact zero both disciplines;
> two-path bit-for-bit on every distinct window at T\* (200-capped at
> padded horizons); r4 nests in r3; queue-level hazards mechanically equal
> at every reachable state; g ≥ 0 with exact existence tests; every
> existence verdict below cites ≥ 4 enumerated coarse histories.

## Verdicts

**Witness 3 (stochastic) — ESTABLISHED.** Informative classes at every
horizon: e.g. (T_ep=8, L=2): 4 coarse histories, prevalence 0.150,
Δ_stoch = 0.085 bits, max g = 0.62; single histories reach g = 1.0 bit.
Far above numerically-collapsed: this is the first condition in the
project where the lineage rung carries mass an order of magnitude over δ.

**Witness 6 (FIFO redundant→informative crossover) — ESTABLISHED.** FIFO
is exactly null at T_ep = 6 everywhere and turns informative at T_ep ≥ 8,
short L: (8,2) Δ = 0.029; (10,2) Δ = 0.036; (10,4) Δ = 0.023 — 4–8
histories each.

**Crossover structure (cells first, summary licensed because they form
frontiers):** informative cells are exactly L ≤ T_ep − 4 (stochastic) and
L ≤ T_ep − 6 (FIFO), within the measured grid T_ep ∈ {6, 8, 10}. Lineage
grips when the window opens after allocation evidence has left context —
short L, late windows — and dies as L grows, exactly the statute's
mechanism. Padding grew prevalence (0.150 → 0.166 at L=2) rather than
diluting it; the IDLE-dilution worry did not materialize in this range.

**Interaction:** Δ_stoch − Δ_FIFO > 0 in every informative cell
(0.023–0.066 bits). Sign was not precommitted; it is now measured:
stochastic order adds lineage value over FIFO everywhere lineage has any.

## Mechanism decomposition (prereg §2 table)

- **FIFO: thrΔ = Δ exactly in every informative cell** (0.02927 = 0.02927,
  etc.) — FIFO's lineage gain is entirely about issuing-thread
  membership/order, row 2 of the table ("lineage informs the actual
  issuing-thread order"), zero allocator-label component.
- **Stochastic: mixed.** Where FIFO is dead (T=6 L=2; T=8 L=4; T=10 L=6)
  thrΔ = 0 — pure allocator-label recovery (row 1: witness passes
  formally, mechanism is label recovery). Where FIFO is alive, thrΔ > 0
  but ≪ Δ (0.013 of 0.085) — both mechanisms present, label recovery
  dominant.
- The D8 allocator candidate mechanism is thereby independently
  confirmed as *one* of two mechanisms, not the whole story.

## M1 exit consequence

Deliverable 4's "D10 truncated-window witness search and crossover verdict
in both completion disciplines" is now measured: both witnesses
established, crossover frontiers explicit, interaction sign positive.
The C1 result that the lineage rung is < δ at every measured law stands
alongside, not in tension: C1's queue depth, workload, and laws sit in
the dead region of these frontiers; C0b short-L is where lineage lives.
Whether any *C1* law reaches an informative cell is a new, well-posed
question — exploratory, outside this preregistration.

## Deviations from preregistration

None in analysis rules. One cap: gate-2 two-path checks limited to 200
windows per (law, discipline) at padded horizons (full coverage at T\*=6);
recorded here per §7.

---

## v0.1.1 (2026-08-24 08:37 PDT) — Codex correction round, all findings verified before adoption

**1. "All six gates passed" was not true of the committed producer.** The
script capped gate-2 two-path checks at 200 windows at padded horizons
while the prereg requires every distinct window. Cap removed; the uncapped
run verifies **all** windows (per-cell counts now in the v2 artifact, e.g.
328 at (10, 6)); every delta reproduces unchanged. The v0.1 sentence
should have said "gates passed with a recorded cap"; the deviation section
said so, the headline did not. Producer and artifact:
`scripts/d10_lineage_search.py` (uncapped) →
`d10-lineage-search-v2-2026-08-24.json`.

**2. Missing preregistered outputs emitted.** The v2 artifact adds
per-generating-endpoint mass, g-quantiles {50, 90, 99}, the secondary
r4-child fraction, and the remaining statutory queries per cell
(never substituted for Q3, per prereg §2).

**3. Offset-mixture amplification separated from truncation.** Anchored
gain I(Z; Λ | H₃, U) vs unanchored, FIFO informative cells (this note's
implementation agrees with Codex's independent computation to all
decimals):

| cell | unanchored Δ | anchored Δ | I(U; Λ | H₃) |
|---|---|---|---|
| (8,2) | 0.02927 | 0.01157 | 0.01770 |
| (10,2) | 0.03568 | 0.01637 | 0.02130 |
| (10,4) | 0.02302 | 0.00858 | 0.01444 |

54–63 % of the reported FIFO gain is offset-mixture amplification —
lineage disambiguating the unanchored endpoint mixture, not the truncated
prefix alone. Stochastic gains are mostly anchored (e.g. 0.0777 of 0.0845
at (8,2)). **The frontiers survive anchoring unchanged** (stoch L ≤ T−4,
FIFO L ≤ T−6), so the truncated-history crossover is real; the unanchored
clock mixture amplifies it, most strongly under FIFO. Chain-rule caution:
unanchored = anchored + I(U;Λ|H₃) holds at (8,2) by coincidence of
structure, not in general — the exact identity runs through
I(ZU; Λ | H₃) = I(U; Λ | H₃) + I(Z; Λ | H₃, U); the residual
I(U; Λ | H₃, Z) is not separately emitted. "Padding grew prevalence" in
v0.1 bundled these; endpoint-mixture growth is the mechanism now on
record.

**4. The C1 sentence was false and is withdrawn.** C1's r3→r4 cells are
**informative and collapsed** (positive exact gains up to ~0.0037 bits at
T_ep = 14, 0.0066 at 16 — nonempty classes below δ), and the C0b frontier
is world-specific and cannot classify C1 geometry. Corrected conclusion:
*C1 already contains nonempty lineage-information classes; their law-level
gain remains below δ. Open: why C1 suppresses the larger C0b effect, and
whether C1 shows the same discipline-dependent frontier.*

**5. Magnitudes restated:** global Δ reaches **8.45×δ** (0.08453 bits);
individual informative histories reach **1 bit ≈ 100×δ**. "An order of
magnitude over δ" conflated the two.

**6. Executable regressions added:** `tests/test_d10_witnesses.py` (6)
pins witness-3 positive, FIFO T\*=6 null, FIFO (8,2) positive,
full-context zeros, and the exact mechanism split. Suite 151.
