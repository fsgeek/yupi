# The three-arm intervention: relay, decoy, self-copy — design v0.1 (2026-10-05)

> **Status: DESIGN.** Skeleton v0.3 §3 items 2–3. Written by the instance of 2026-10-05, which owns the project.
> It extends `docs/relay-intervention-design-v0.1.md` (r1ʀ) to two more window-level rungs. Each step has the
> same order as the relay's: code with tests, then the exact side with gates, then corpora with pairing gates,
> then a pre-registration stamped with severities, then training. Nothing is trained before the stamp.

## 1. The question

The relay's learner gain was V-shaped in Δι (it tracked |Δι|, not the sign), it was zero where ι4 = 0, and about
60 % of it persisted at convergence. Two readings fit:

- **H_move:** relocating long-lag KIND information helps the learner in proportion to how much moves (|Δι|),
  whatever the field says.
- **H_bind:** the relay helps because its content is entity-conditional (the last KIND *of this actor*), making a
  binding explicit. Moving KIND information without binding content helps little.

A third possibility confounds both: **H_field**, where any extra deterministic field changes learning (capacity,
format, token statistics) regardless of what it carries.

## 2. The rungs (all window-level over r1, value in the OBJECT slot that r1 masks, Lit values)

| rung | name on disk | OBJECT slot of record t | binding content | Δι_kind,4 vs r1 (exact, ε = 1) |
|---|---|---|---|---|
| relay | r1R | KIND of the latest earlier record in the window with t's actor; NONE if none | yes | mean 0.094 |
| decoy | r1D | KIND of record t − 1 in the window; NONE for t = 1 | no | mean 0.068, per-class corr with relay 0.29 |
| self-copy | r1S | KIND of record t | no | 0 exactly (scratch check) |

All three are window-local, token-matched (they reuse a masked slot), injective (dropping the field gives the r1
window back), and literal (Lit passes Π_all untouched). So relay design §3's argument holds unchanged: the ceiling
is the push-forward of r1's, with an identical KIND marginal class by class.

## 3. Code (tests first)

- Generalize `interfaces.RELAY_RUNGS` from {r1R: r1} to a registry of window-level rungs, each with its window
  map and its next-record map. `relay_window`/`relay_next` stay as they are, and frozen scripts that call them or
  `derive_relay_table` without a rung keep r1R behaviour byte for byte.
- `pattern_ceiling` (derived tables, gates A/B, the independent route), `pattern_enumerator` (brute force, gate C),
  `corpus.manifest` (RUNGS), and the evaluator's OBJECT-slot reading (a KIND or NONE at every registered rung)
  dispatch on the registry.
- Tests, per new rung: a hand example pinned; next-step equals the step of the window map; window-locality;
  injectivity; Lit commutes with pattern; the derived table equals the recursion route and brute force at
  (8, 4, 2); gates detect a broken derivation. For r1S, also Δι_kind,m = 0 exactly for every class at every m.
- The existing relay tests must pass unchanged.

## 4. Exact side (before any corpus)

For r1D and r1S, at (40, 8, 2), k = 1..7, both ε:
- derived tables with gates A and B, and gate C at (8, 4, 2);
- the lag profile ι_kind,m for m = 1..6;
- the per-class Δι_kind,4 cache, in the format of the relay's;
- for every pair of arms, the per-class |Δι| joint distribution. This sizes the discriminating set: classes where
  one arm moves information and the other does not.

## 5. Corpora: fresh, paired

A **fresh** r1 ε = 1 2M corpus (a new run key and seeds, never seen by any instance's analysis), plus r1R, r1D and
r1S renderings of the same episodes and windows. Gates: `relay_corpus_check` generalized, so that each arm's
windows with the field dropped equal the r1 windows token for token.

## 6. Learner side (shapes; numbers are fixed in the prereg)

- Four rungs × seeds 1–3 × two budgets: d = 128, 5 epochs and 15 epochs, the converged recipe. 24 runs under the
  ayllu-gpu lease. CountKind on each rung's fresh corpus (CPU).
- Census at k = 7 on the paired test split. Per window and per arm, the paired gain is G_arm = (mean r1 excess) −
  (mean arm excess).
- **Primary statistic per arm:** the slope of G_arm on |Δι_arm| over classes. Same controls as relay_paired, HC1
  by window plus CR1 by class reported.
- The rivals' predictions, stated before the prereg fixes bands:

| | relay slope on |Δι_R| | decoy slope on |Δι_D| | self-copy mean gain |
|---|---|---|---|
| H_move | > 0 | ≈ relay's (ratio band set in the prereg) | ≈ 0 |
| H_bind | > 0 | ≈ 0 | ≈ 0 |
| H_field | any | any | > 0, about equal to the decoy's mean gain |

- The ι4 = 0 classes: zero gain in every arm (all three readings predict this, so it is a check, not a test).

## 7. Severity, before stamping

For each prediction, simulate the rivals' outcomes. Plant per-class gains under H_move, H_bind and H_field on the
real class mix, Δι distributions and window counts, add seed noise matched to the relay arm's observed seed
spread, and report the share of each rival's simulated outcomes the prediction rejects. A prediction that rejects
under 80 % of its rival's outcomes is redesigned or demoted to descriptive before the stamp.
`tests/test_relay_paired.py`'s planted-slope test is the template.

## 8. What would change this

- If gate A or B fails for r1D or r1S, the rung is not a ceiling-preserving intervention and is dropped.
- If the discriminating set (§4) is too small for any prediction to reach the §7 bar, the decoy is redesigned
  before any training, for example as a decoy of the actor's *second*-latest KIND (binding content, different
  distance) or one with a larger Δι.
