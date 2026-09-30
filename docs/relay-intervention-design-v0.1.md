# The relay intervention: moving information closer without adding any — design v0.1 (2026-09-30)

> **Status: DESIGN.** Written by the owner (instance of 2026-09-28/29/30) for the first of the
> three tests owed by `docs/d1-long-lag-verdict-v0.1.md` ("not established: causation"). The
> predictions are stamped in a separate pre-registration **after** the exact side (§4) is
> computed and **before** any relay model is trained.

## 1. The question

The verdict shows that within cells a learner's KIND excess rises with ι_kind,4, the exact
information about the next KIND lying more than four records back. That is a correlation over
prefix classes. Classes with far-back information could differ in other ways the controls
missed. **The intervention holds the world, the histories and the information fixed, and
changes only where in the window the information sits.**

## 2. The relay rung r1ʀ

For each record t of a window at r1 (kind + actor visible), fill one slot that r1 masks with

> relay_t = the KIND of the most recent earlier record **in the same window** with the same
> actor as record t; NONE if the actor has no earlier record in the window, or record t has
> no actor.

Constraints (each is a gate):

1. **Window-local.** relay_t is a function of the window's records 1..t only. It never uses
   the episode before the window. Otherwise it would add information and change the ceiling.
2. **Literal.** Relay values are KIND names. They are not entities and must pass through Π_all
   renaming untouched (`naming.extend_binding` today renames any non-None, non-MASKED value in
   a slot; the relay needs a value type it leaves alone).
3. **Token-matched.** The relay reuses a slot that r1 masks, so a record keeps its token count
   (this answers the token-budget confound the simulated reviewer raised). The vocabulary gains
   nothing if KIND tokens are reused as values; otherwise the addition is stated.
4. **Paired.** The r1ʀ corpora render the **same episodes and windows** as the r1 ε = 1 2M
   corpus (same manifest seeds, same draws), so every test window exists at both rungs.

## 3. Why the ceiling is exactly unchanged

The r1ʀ prefix is a bijective function of the r1 prefix, since relay is computed from it and
dropping it recovers the prefix. The next r1ʀ record is a function of the r1 prefix together
with the next r1 record. So P*(next r1ʀ record | r1ʀ prefix) is the push-forward of
P*(next r1 record | r1 prefix), with equal entropy, and the KIND marginal is identical per
class. **The r1ʀ ceiling tables are derived from the r1 tables by this map, not recomputed.**
The derivation is gated by an independent route on a small world: at (8, 4, 2), the pattern
table computed through the ordinary recursion with a relay-aware projection must equal the
derived table class by class, exactly. If that recursion is infeasible, brute-force enumeration
of windows is the fallback.

## 4. Exact side, computed before any training

For k = 1..7 and both ε, but ε = 1 carries the test: the derived tables; the KIND H* equality
per class (must be exact); the lag profile ι_kind,m for m = 1..6 at r1ʀ; and **per class,
Δι_kind,4 = ι_kind,4(r1) − ι_kind,4(r1ʀ)**. That distribution sizes the predictions: if the
law-mass mean Δι is small, the test is underpowered and is redesigned (for example with a
richer relay), not run.

## 5. Learner side

- Three seeds at the recipe the verdict was confirmed at (d = 128, 5 epochs, 2M windows, lr
  1e-3 → 1e-4), so the r1 ε = 1 seeds 1–3 (already censused) are the matched controls. Three
  more seeds at the converged budget (15 epochs) against the r1 15-epoch seeds are a
  secondary arm.
- Census at k = 7 on the paired test split. The analysis is **per window, paired**:
  Δexcess_w = mean over r1 seeds of the KIND excess − mean over r1ʀ seeds, regressed on
  Δι_kind,4 of the window's class, with the same controls as the verdict (they are identical
  across the pair by §3, so they enter only through interactions). HC1 errors.
- The relay field's own excess is reported separately. The model must learn a deterministic
  field; its cost is not the quantity tested.

## 6. Predictions (their numeric form is fixed in the pre-registration after §4)

- **R1 (causal slope).** The paired slope of Δexcess on Δι_kind,4 is positive, with magnitude
  within a factor of two of the verdict's r1 ε = 1 β_long (0.033, frequency-controlled pooled).
- **R2 (no-change control).** Windows with Δι_kind,4 = 0 (the relay moved nothing past lag 4)
  show mean Δexcess within ±2 se of zero.
- **R3 (the relocated model obeys the same law).** In r1ʀ models, the frozen verdict analysis
  (β_long on r1ʀ's own ι) is positive with t ≥ 3 in every seed.

A pass on R1 and R2 makes distance causal for this learner, with the information held fixed. A
null R1 with a sufficient Δι means the correlation was carried by something else about those
histories, and the verdict's reading is withdrawn.
