# D10 truncated-window lineage verdict — v0.1

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
