# Held-out Tier 1 confirmation — v0.1

> **Status (2026-08-22 03:08 PDT): measured, not yet truthsayer-reviewed.**
> First confirmatory round at the v0.2.5 thresholds (δ = δ_sync = Δ_τ =
> 0.01). Laws enacted by stamp `7564482` (Tier 1, PI decision 22:51 PDT);
> ε pair drawn by recorded seed (`held-out-selection-e-draw-2026-08-21.json`,
> commit `a34fd81`) → ε ∈ {¼, ⅝}. Predictions P1–P5 were written in
> `held-out-laws-proposal-v0.1.md` v0.2/v0.3 before any F-law ceiling
> existed. This note scores them as written. Scorer:
> `scripts/c1_heldout_score.py` → `c1-heldout-tier1-score-2026-08-22.json`.

## 0. The headline, stated first

**The ladder structure generalizes; three of five predictions fail; every
failure is traceable to an error the instance made at writing time, and
each was checkable against committed data or source before the draw.**
The thresholds did not fail. The predictions did. Both facts matter and
they are different facts.

| | as written | verdict | cause |
|---|---|---|---|
| P1 | r2=r3=r4, r1 ≥ +2, both new ε | **PASS** (measure b) | — |
| P2 | L\*(¼) ≥ L\*(½) ≥ L\*(⅝) | **FAIL** (inverted) | mechanism wrong: ε is scheduler randomness, not trace coverage |
| P3 | max r3→r4 gap ≤ 0.003 | **FAIL** (F3′: 0.003255) | bound set from a (12,·) figure; baseline (14,·,2) already 0.003728 |
| P4 | F3′ L\* unchanged from (14,·,2) | **ILL-POSED** | odd-L grid cannot equal even values |
| P5a | pair_prob(δ_p=0) > 0 | **PASS** | — |
| P5b | δ_p=10⁻⁴ jump ≥ 10× | **FAIL** (1.0–2.6×) | "65.9×" was one (12,2,2) ε=½ cell; baseline (14,2,2) is 1.0–1.6× |

## 1. What was run

28 ceiling runs (`c1_query_ceilings.py`, `c1_q4_ceilings.py` W4) launched
22:56 PDT, complete 03:04 PDT (~6 h wall, 28-way contention; the proposal's
"~7 min/run" was a lone-process figure and is corrected here):

- **F2** (14, L ∈ {2,…,14} even, 2), ε ∈ {¼, ⅝} — 14 artifacts
  `c1-{query,q4}-ceilings-14-L-2[-W4]-heldout-2026-08-21.json`.
- **F3′** (14, L ∈ {1,…,13} odd, **1**), ε ∈ {1, ½} — 14 artifacts
  `…-14-L-1[-W4]-heldout-2026-08-21.json`.

Sweeps on those artifacts (`YUPI_ARTIFACT_TAG=heldout`):
`c1-sync-sweep-{F2,F3}-heldout-2026-08-21.json`,
`c1-delta-sweep-{F2,F3}-heldout-2026-08-21.json`,
`c1-tv-sweep-14-{2,4}-2-F2-heldout-2026-08-21.json` (L=4 appended in §5).

Code: `src/yupi/eps_grid.py` (`YUPI_EPS`), 9 witnesses; defaults verified
byte-identical to three committed corrected artifacts before use (commit
`60b79d2`). One wiring bug (artifact-tag glob) produced empty sweeps on the
first pass; those outputs were never committed and were regenerated.

## 2. Synchronization horizons (δ_sync = 0.01)

Measure (b) = truncation-conditional mean (statutory, v0.2.5 §6); measure
(a) = law-mass mean, co-reported as the statute requires.

| family | ε | r1 (a/b) | r2 | r3 | r4 |
|---|---|---|---|---|---|
| baseline (14,·,2) | 1 | 10 / 12 | 10 / 10 | 10 / 10 | 10 / 10 |
| baseline | ½ | 10 / 12 | 8 / 10 | 8 / 10 | 8 / 10 |
| **F2** | **¼** | 8 / **10** | 8 / **8** | 8 / **8** | 8 / **8** |
| **F2** | **⅝** | 10 / **12** | 8 / **10** | 8 / **10** | 8 / **10** |
| **F3′** (B=1) | 1 | 11 / **13** | 9 / **11** | 9 / **11** | 9 / **11** |
| **F3′** | ½ | 11 / **11** | 9 / **11** | 9 / **11** | 9 / **11** |

**P1 — PASS.** At both drawn ε, r2 = r3 = r4 on measure (b) and r1 sits
exactly two steps above. On measure (a) r1 *joins* the pack at ε = ¼
(8/8/8/8) — reported because the statute co-reports (a), and because it
is the first cell in the project where the actor rung's advantage
vanishes on any measure. Mechanism (post hoc, not credited): at low ε the
scheduler is nearly round-robin, so the actor identity is nearly
predictable from the clock and r1's extra information is small.

**P2 — FAIL.** Predicted L\*(¼) ≥ L\*(½). Measured (b): r1 10 < 12; r2–r4
8 < 10. Inverted at every rung. The prediction was derived from "ε
governs tracing coverage," read from the `WorldConfig` docstring
("epsilon for tracing"). `kernel._epsilon_policy` is uniform-among-
runnable with probability ε, round-robin with 1−ε: ε is *world* entropy.
Lower ε → more deterministic world → faster synchronization. The corrected
mechanism predicts L\*(¼) ≤ L\*(½) ≤ L\*(⅝), which the data satisfy
(10 ≤ 12 = 12; 8 ≤ 10 = 10) — recorded as an *exploratory* regularity, not
a confirmation. Note ⅝ and ½ coincide at this L-resolution.

**P4 — ILL-POSED.** v0.3 restated P4 for F3′ as "L\* unchanged from the
(14,·,2) values," which an odd-L grid cannot satisfy. The interval reading
(each F3′ crossing lies within one step of the baseline crossing) holds in
all 8 cells, but that is a reading invented after the grids were seen.
What F3′ does establish without a prediction: under B = 1 the ladder
shape is unchanged (r2 = r3 = r4, r1 above except at ε = ½ where r1 = r2 on
the odd grid — crossing intervals (10,11] vs (9,10] remain disjoint).

## 3. Rung collapse (δ = 0.01) and the lineage rung

L-axis collapse horizons L\*(pair):

| family | ε | r1→r2 | r2→r3 | r3→r4 |
|---|---|---|---|---|
| baseline | 1, ½ | 10 | 8 | 2 |
| F2 | ¼ | 8 | 6 | 2 |
| F2 | ⅝ | 10 | 8 | 2 |
| F3′ | 1 | 11 | 9 | 1 |
| F3′ | ½ | 11 | 7 | 1 |

Ordering r1→r2 > r2→r3 > r3→r4 holds in every family (was v0.1 P2; kept as
a reported regularity, not scored).

**P3 — FAIL, by 0.000255 bits, against a bound that was wrong when
written.** Max r3→r4 gap: F2 0.000777 (ε=⅝, L=2); F3′ **0.003255** (ε=1,
L=3); baseline (14,·,2) **0.003728** (ε=1, L=2). The bound "0.003 = ~0.002
+ 50 %" used the (12,·) figure from memory; the committed (14,2,2) artifact
already exceeded it. What survives: the lineage rung is ≤ 0.0037 bits at
every measured (law, ε, L) — 2.7× below δ — so the r3/r4 collapse from
L = 2 (or L = 1) is confirmed at every fresh law; P3's number is not.

## 4. Divergent class at (14,2,2), new ε (P5)

| ε | rung | pair_prob(δ_p=0, Δ_τ=0.01) | at δ_p=10⁻⁴ | ratio |
|---|---|---|---|---|
| ¼ | r1,r2 | 3.88e-6 | 9.94e-6 | 2.6 |
| ¼ | r3,r4 | 1.94e-5 | 3.50e-5 | 1.8 |
| ⅝ | r1,r2 | 1.51e-5 | 1.51e-5 | 1.0 |
| ⅝ | r3,r4 | 3.09e-5 | 5.22e-5 | 1.7 |

**P5a — PASS** (class non-empty at every cell). **P5b — FAIL.** Baseline at
the same law: 1.0–1.6×. The 65.9× lives at (12,2,2) ε=½ r1/r2 only, where
the exact corner is 5e-8 — a near-empty corner makes any jump large. The
proposal generalized a one-cell ratio to a law it had never applied to.
(14,4,2) appended in §5 when the run lands.

## 5. (14,4,2) TV sweep — appended 2026-08-22 03:09 PDT

pair_prob at Δ_τ = 0.01; columns: δ_p = 0 exact corner, δ_p = 10⁻⁴, ratio.

| ε | rung | δ_p=0 | δ_p=10⁻⁴ | ratio | source |
|---|---|---|---|---|---|
| 1/4 | r1 | 4.75e-04 | 9.31e-04 | 2.0 | held-out |
| 1/4 | r2 | 5.62e-04 | 9.68e-04 | 1.7 | held-out |
| 1/4 | r3 | 5.55e-04 | 9.85e-04 | 1.8 | held-out |
| 1/4 | r4 | 5.72e-04 | 9.85e-04 | 1.7 | held-out |
| 5/8 | r1 | 7.76e-04 | 1.09e-03 | 1.4 | held-out |
| 5/8 | r2 | 8.76e-04 | 1.20e-03 | 1.4 | held-out |
| 5/8 | r3 | 1.03e-03 | 1.36e-03 | 1.3 | held-out |
| 5/8 | r4 | 1.12e-03 | 1.36e-03 | 1.2 | held-out |
| 1 | r1 | 1.15e-03 | 1.20e-03 | 1.0 | baseline |
| 1 | r2 | 1.31e-03 | 1.48e-03 | 1.1 | baseline |
| 1 | r3 | 1.69e-03 | 1.88e-03 | 1.1 | baseline |
| 1 | r4 | 2.03e-03 | 2.07e-03 | 1.0 | baseline |
| 1/2 | r1 | 7.51e-04 | 1.11e-03 | 1.5 | baseline |
| 1/2 | r2 | 8.86e-04 | 1.20e-03 | 1.3 | baseline |
| 1/2 | r3 | 9.57e-04 | 1.25e-03 | 1.3 | baseline |
| 1/2 | r4 | 1.02e-03 | 1.25e-03 | 1.2 | baseline |


P5a holds at (14,4,2) (all corners > 0; the class is ~100× more prevalent
at L = 4 than at L = 2, as in the baseline). P5b fails here too: 1.2–2.0×
held-out against 1.0–1.5× baseline. Verdicts in §0 are unchanged.

## 6. What this round establishes, and what it does not

**Establishes (confirmatory, thresholds as frozen):** under unseen ε and
an unseen bucket law, r2 = r3 = r4 synchronize together and r1 later
(P1); the divergent class is non-empty (P5a); rung collapse follows
r1→r2 > r2→r3 > r3→r4 and the lineage rung is < δ everywhere.

**Does not establish:** any monotone-in-ε claim (P2 failed; the corrected
mechanism is exploratory); any numeric bound on the lineage rung tighter
than δ (P3's number was wrong); any δ_p-jump magnitude (P5b); anything
about B = 1 beyond ladder shape (P4 ill-posed).

**The methodological finding**, which is the one I would put first if this
were a paper section: three of five pre-stated predictions were mis-set
from stale numbers or an unread mechanism, and every one was checkable
before the draw — `kernel.py` for ε, the committed (14,2,2) artifacts for
P3 and P5b. Pre-statement did not launder them; it made them auditable,
which is the thing it is for. The next round's predictions should be
checked against every committed artifact at the same (T_ep, B) before
they are stamped, mechanically, by script.

## 7. Provenance

All artifacts named above are appended under `-heldout-2026-08-21` /
`-2026-08-22` and never overwrite. Raws, sweeps, score JSON, scorer, and
this note are committed together; the stamp on that commit is the
confirmation's timestamp. Truthsayer pass owed.
