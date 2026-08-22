# Observer-monotonicity is not a refinement theorem — and the mass it gains is created, not inherited (v0.1)

**Status: exploratory measured note (2026-08-21, eleventh instance).** Not
governing. Answers open question 1 of
[`c1-divergent-grid-v0.1.md`](c1-divergent-grid-v0.1.md) (v0.1.2): *"Is
observer-monotonicity (fixed r_pred, mass non-decreasing in r_obs) a
theorem? Refining a partition does not obviously preserve exact-equality
coincidences between mixtures. 24/24 says look for the reason; the reason
is not in this note."*

Threshold context: everything here is the exact δ_p = 0 corner, which
Part II v0.2.5 (2026-08-21) keeps as the anchor of the frozen δ_p axis, so
the class criterion used here is now statutory rather than provisional;
m = 2, W = 4 are the v0.2.4 frozen values. Nothing below amends a statute.

Producers: `scripts/observer_monotonicity_counterexample.py` (abstract),
`scripts/c1_observer_monotonicity_ledger.py` (measured),
`tests/test_observer_monotonicity_counterexample.py` (witness, 2 tests).

## Answer, in one line

**No — it is not a theorem of partition refinement**, and the empirical
24/24 does not hold for the reason one would guess. Refinement *shatters*
essentially every coincidence it touches; the observed rise comes from
**new coincidences created between windows whose parents were unrelated**.

## 1. Why it cannot be a refinement theorem

Both P-next and the τ functionals are **linear in the belief**, and a
coarse window's belief is exactly the mass-weighted mixture of its refined
pieces' beliefs (forced: a fine window key determines its coarse key, and
beliefs are path-aggregated). So a coincidence between two coarse windows
is a coincidence *between mixtures*, and mixtures can agree while no pair
of their components does.

Counterexample (exact rationals; witnessed in the test file). States x, y
share a next-record law but differ on τ; a third state z is unused.

| | coarse | fine |
|---|---|---|
| A | mass 1/10, belief ½x + ½y | A1 = 1/20 pure x; A2 = 1/20 pure y |
| B | mass 9/10, belief pure x | B unchanged |

Coarse: P-next(A) = P-next(B) = p, τ(A) = ½ ≠ 0 = τ(B) → divergent,
mass 2·(1/10)(9/10) = **9/50 = 0.18**.
Fine: (A1,B) has identical beliefs so τ ties and it dies; (A2,B) survives;
(A1,A2) is newly divergent. Total **19/200 = 0.095 < 0.18.**

The mechanism is a **mass asymmetry**: the destroyed cross-pair is weighted
by the *other* window's mass (m_A/2 · m_B), while the created sibling pair
is weighted only by its own (m_A/2 · m_A/2). Any m_A < m_B gives a
decrease. Refinement is therefore free to lose divergent mass, and no
appeal to nesting — the argument that makes the r_pred direction a theorem
(pushforward, G1) — is available in the r_obs direction.

## 2. What actually happens in C1 (the measured ledger)

Per observer step, decomposing the change in divergent mass into: **kept**
(coarse pair mass surviving as fine cross-piece pairs), **lost**,
**new-cross** (fine divergent pairs whose parents were *not* a divergent
pair), **new-within** (fine divergent pairs sharing a parent —
structurally impossible at the coarse rung). At r_pred = r1:

| law | ε | step | coarse → fine | kept | lost | new-cross | new-within |
|---|---|---|---|---|---|---|---|
| (12,2,2) | 1 | r1→r2 | 0.000004 → 0.000004 | 0.000004 | 0 | 0 | 0 |
| (12,2,2) | 1 | r2→r3 | 0.000004 → 0.000011 | 0.000003 | **0.000002** | **0.000009** | 0 |
| (12,2,2) | 1 | r3→r4 | 0.000011 → 0.000011 | 0.000011 | 0 | 0 | 0 |
| (12,2,2) | ½ | r2→r3 | 0.000000 → 0.000022 | 0 | 0 | **0.000022** | 0 |
| (14,2,2) | 1 | r2→r3 | 0.000017 → 0.000025 | 0.000017 | 0 | **0.000007** | **0.000001** |
| (14,2,2) | 1 | r3→r4 | 0.000025 → 0.000026 | 0.000025 | 0 | 0.000001 | 0 |
| (14,2,2) | ½ | r2→r3 | 0.000012 → 0.000031 | 0.000012 | 0 | **0.000017** | **0.000001** |

((12,2,2) and (14,2,2) complete; (14,4,2) is a longer run, not included in
v0.1 — see caveats. Rows with all-zero change omitted for space; the full
set is the script's output.)

Two facts, both against the natural guess:

1. **Loss is real.** At (12,2,2) ε=1 r2→r3, 0.000002 of coarse divergent
   mass is destroyed — the counterexample's mechanism fires in the actual
   world. Monotonicity survives that step only because creation exceeds it
   roughly 4:1.
2. **Inheritance is not the mechanism.** A separate check
   (`obs_mono_mechanism`, scratch) measured the mass whose P-next survives
   refinement *conditional on the parent actually splitting*: **0–1%**, and
   the mass whose full (P-next, τ) tuple survives: **exactly 0%**, at every
   step and both ε at (12,2,2). Splitting a window essentially always moves
   both mixtures. The rise is therefore not preserved coincidences plus
   extras; it is a near-total turnover in which creation happens to
   dominate.

**new-within is worth naming**: at (14,2,2) sibling pairs under one parent
contribute divergent mass. These are pairs the coarse observer cannot even
form — the divergence exists only because the finer interface split them
apart. That is interface-created divergence in the strictest sense.

## 3. What this does to open question 1

Restated for the next instance: *observer-monotonicity is an empirical
regularity of C1 with a known counterexample class, not a theorem.* The
question is no longer "why is it preserved" (it isn't) but **"why does
creation beat destruction at every measured step?"** Candidates, untested:

- **Mass asymmetry cuts the other way here.** The counterexample needs a
  heavy window paired against a light one that splits. If C1's divergent
  pairs sit predominantly between windows of comparable mass, the
  destruction term is small by construction.
- **Coincidence supply grows superlinearly.** Refinement multiplies the
  number of windows (209 → 277 → 287 at (12,2,2)); if exact P-next
  coincidences are roughly a fixed *rate* per pair, pair count grows
  quadratically while destroyed pairs grow linearly in split windows.
  This predicts monotonicity should weaken or fail at laws where
  refinement adds few windows — a testable prediction.
- The `related` field's role (open question 2) is presumably the same
  mechanism seen from the other side, since r2→r3 is where both the
  creation term and the historical observer gain concentrate.

## Caveats

- δ_p = 0 corner only. Under the frozen δ_p axis's larger values the
  coincidence sets grow and both terms change; not measured here.
- Ledger run at r_pred = r1 only; the grid's other columns are unmeasured
  in this decomposition (the 24/24 claim itself spans all four).
- (14,4,2) ledger not included: the pair enumeration is quadratic in
  window count (≈1400–2400 classes) and exceeded the interactive budget.
  A law where the decomposition might differ is therefore untested —
  **this note's evidence is two laws, not three.**
- Single-path: the ledger shares the window-aggregation and mixture code
  with `c1_divergent_grid.py`; it is a decomposition of the same
  computation, not an independent second path. Its totals do reproduce the
  grid note's masses, which is a consistency check, not a gate.
- The counterexample is abstract. It proves no theorem exists for general
  refinements; it does not exhibit a *reachable C1 configuration* with
  decreasing mass. Whether the C1 rung ladder can realize a net decrease
  at some law is open — the measured 0.000002 loss at (12,2,2) shows the
  ingredients are present.
