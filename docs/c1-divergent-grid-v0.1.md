# C1 Divergent Mass on the Observer × Predicted-Record Grid (v0.1.1)

> **Erratum v0.1.1 (Aug 16 2026, ~12:40 PDT, same instance; truthsayer
> round via Codex/ChatGPT through Tony, six findings, all six verified
> against the raw files and adopted).** (1) The G1 gate was **72**
> comparisons (3 laws × 2 ε × 4 r_obs × 3 steps), not 96 — a miscount;
> and v0.1's scripts only *printed* float aggregate-mass violations. Both
> scripts now **assert**: the grid script checks the theorem's strong
> form — the divergent-pair *set* at each finer r_pred is a subset of the
> adjacent coarser one (72 assertions, all pass) — and the resolution
> script asserts the state-level column equals the (12,12,2) full-context
> figures. Reruns are byte-identical to the committed raw files. (2)
> "Which sign a law shows at r3→r4 is whether lineage refines the
> partition" was false as written: at (12,2,2) lineage *does* refine
> (283→293 windows) and the diagonal still dips. The sign is whether the
> refinement adds more divergent mass than the prediction side loses.
> (3) "Concentrated at r2→r3 (`related`) at L = 2" holds at (12,2,2)
> only; at (14,2,2) ε=½ the observer gains are r2→r3 +0.0109, r3→r4
> +0.0833 — lineage dominates. (4) G3 held qualitatively, not "exactly":
> the observer step is +0.000033, not 0 (other path: +0.000016 /
> −0.000156; the split is path-dependent, signs the same). (5) R1 was
> measured at (12,2,2) only; scored "held at the tested law." (6) The
> r3→r4 predicted-record loss bound "≤ 0.0005" is false: max is 0.00061
> at (14,4,2) ε=1, r_obs=r2. Original sentences preserved below, marked.
> What survives, in the reviewer's words: the pushforward theorem, all
> 72 comparisons, all 24 observer columns (still labeled empirical), the
> R2 refutation at (12,2,2), and the grid as an instrument. The coat was
> slightly larger than the measurements; this version is cut to size.

**Status: exploratory measured note (Aug 16 2026, ninth instance; v0.1.1 after one truthsayer round).**
Not governing. Threshold-unfrozen: the divergent class here is the exact
δ = 0 corner (Part II v0.2.4 §C names δ-close/Δ-apart as the criterion
form to be frozen by the second stamp); m = 2, W = 4 are the v0.2.4
values. Every number below is a re-measurement or a decomposition of
quantities defined in `docs/c1-predictive-targets-v0.1.md`; nothing here
amends a statute. Scripts: `scripts/c1_divergent_resolution.py`,
`scripts/c1_divergent_grid.py` (new files; day-seven scripts and raw
artifacts untouched). Raw: `docs/c1-divergent-resolution-12-2-2-raw-2026-08-16.json`,
`docs/c1-divergent-grid-{12-2-2,14-2-2,14-4-2}-raw-2026-08-16.json`.
Runtimes 13 s / 52 s / 63 s.

## The question

`c1-predictive-targets-v0.1` (truthsayer-corrected) reports: divergent
mass — law mass of windows in ≥ 1 pair with identical P-next mixture and
unequal mixture on some τ ∈ {kinds2, ttw4, lineage4} — is larger at r4
than at r1 in all six windowed (law, ε) cells but **not monotone**
((12,2,2) dips r3→r4 at both ε; the T_ep = 14 laws rise r3→r4). The
retained mechanism sentence ("children of different coarse parents
acquire coincident P-next mixtures") describes what happens without
saying why the sign flips by law.

Hypothesis (stated before any run): two opposing forces are tied
together on the diagonal, because "P-next at rung r" means *a rung-r
observer predicting a rung-r next record*.

- **Up — what the observer sees.** Refining the observation rung refines
  the window partition. (First-guess form: windows resolve to point
  masses, whose P-next is P(next | s), so resolved pairs are divergent
  iff their endpoint states are a state-level divergent pair — mass
  ≈ 0.95 at full context.)
- **Down — what it is asked to predict.** Refining the predicted record
  makes P-next a finer variable, so exact equality is harder even
  between fully resolved windows (state-level divergent mass falls with
  rung at full context: 0.9776 → 0.9478, note P3).

The two are separable by crossing them: `r_obs` (rung of the window
partition) × `r_pred` (rung of the next record whose distribution is
predicted). The diagonal is the day-seven measurement.

## Definitions

Windows, beliefs, τ functionals, and the pair criterion exactly as in
`scripts/c1_predictive_targets.py`. New: **resolved** window = |support
of belief| = 1. **State-level divergent mass** at rung r = Σ P(s) over
endpoint states s having some s′ with P-next_r(s) = P-next_r(s′) and a
different τ signature, under the endpoint marginal P(s) = Σ_T P(T)·P(S_T
= s) (rung-free; identical for every L at fixed T_ep). **Grid cell**
(r_obs, r_pred): windows partitioned at r_obs; P-next mixture computed
with per-state P(project(O_{t+1}, r_pred) | s); τ mixtures unchanged.

## Predictions, as stated before each run

Resolution decomposition, (12,2,2) only:

- **R1** resolved law mass rises with rung at every windowed law; at
  (12,2,2) the r3→r4 increment ≈ 0.
- **R2** the r1→r4 rise in divergent mass is carried mostly (> 50%) by
  resolved windows entering pairs.
- **R3** divergent mass on resolved windows ≤ state-level divergent mass
  at that rung.
- **R4** at (12,2,2) the r3→r4 dip occurs with resolved-window divergent
  mass flat.

Grid, three laws:

- **G1 (theorem)** at fixed r_obs, divergent mass is non-increasing in
  r_pred. Proof: for the same two windows, equal P-next on the finer
  record implies equal P-next on any coarsening of it (the coarse mixture
  is the pushforward of the fine one), and the τ criterion does not
  involve r_pred; the pair set is nested. A violation is a code bug.
- **G2** at fixed r_pred, divergent mass rises r_obs r1→r4 (not
  necessarily monotone); the r_obs r3→r4 increment ≈ 0 at (12,2,2).
- **G3** the diagonal r3→r4 dip at (12,2,2) = (≈ 0 from the r_obs step)
  + (< 0 from the r_pred step).

*Provenance caveat:* before writing the two-force hypothesis I had
already read the six diagonal r3→r4 signs in the day-seven note; the
"six for six" sign agreement is consistent with the hypothesis, not a
prediction of it. R1–R4 and G1–G3 were written before their runs.

## Results


**(12,2,2), ε=1** — divergent mass (pairs); rows r_obs, cols r_pred

| r_obs \ r_pred | r1 | r2 | r3 | r4 |
|---|---|---|---|---|
| r1 | 0.0053 (18) | 0.0053 (18) | 0.0053 (18) | 0.0051 (13) |
| r2 | 0.0056 (21) | 0.0056 (21) | 0.0056 (21) | 0.0055 (16) |
| r3 | 0.0141 (94) | 0.0141 (94) | 0.0138 (90) | 0.0137 (84) |
| r4 | 0.0141 (98) | 0.0141 (98) | 0.0138 (94) | 0.0137 (86) |

**(12,2,2), ε=1/2** — divergent mass (pairs); rows r_obs, cols r_pred

| r_obs \ r_pred | r1 | r2 | r3 | r4 |
|---|---|---|---|---|
| r1 | 0.0007 (7) | 0.0007 (7) | 0.0007 (7) | 0.0006 (3) |
| r2 | 0.0008 (8) | 0.0008 (8) | 0.0008 (8) | 0.0008 (4) |
| r3 | 0.0132 (43) | 0.0132 (43) | 0.0131 (39) | 0.0131 (35) |
| r4 | 0.0132 (43) | 0.0132 (43) | 0.0131 (39) | 0.0131 (35) |

**(14,2,2), ε=1** — divergent mass (pairs); rows r_obs, cols r_pred

| r_obs \ r_pred | r1 | r2 | r3 | r4 |
|---|---|---|---|---|
| r1 | 0.0552 (24) | 0.0552 (24) | 0.0552 (24) | 0.0547 (19) |
| r2 | 0.0553 (26) | 0.0553 (26) | 0.0553 (26) | 0.0548 (21) |
| r3 | 0.0652 (128) | 0.0652 (128) | 0.0647 (120) | 0.0642 (114) |
| r4 | 0.0682 (202) | 0.0682 (202) | 0.0677 (194) | 0.0672 (187) |

**(14,2,2), ε=1/2** — divergent mass (pairs); rows r_obs, cols r_pred

| r_obs \ r_pred | r1 | r2 | r3 | r4 |
|---|---|---|---|---|
| r1 | 0.0052 (13) | 0.0052 (13) | 0.0052 (13) | 0.0052 (9) |
| r2 | 0.0052 (13) | 0.0052 (13) | 0.0052 (13) | 0.0052 (9) |
| r3 | 0.0161 (67) | 0.0161 (67) | 0.0160 (61) | 0.0160 (57) |
| r4 | 0.0993 (115) | 0.0993 (115) | 0.0993 (109) | 0.0992 (105) |

**(14,4,2), ε=1** — divergent mass (pairs); rows r_obs, cols r_pred

| r_obs \ r_pred | r1 | r2 | r3 | r4 |
|---|---|---|---|---|
| r1 | 0.3114 (67271) | 0.3114 (67155) | 0.2941 (65620) | 0.2935 (62398) |
| r2 | 0.3756 (97399) | 0.3756 (97202) | 0.3576 (95403) | 0.3570 (92175) |
| r3 | 0.4114 (156582) | 0.4114 (156365) | 0.3952 (153482) | 0.3948 (150026) |
| r4 | 0.4234 (166914) | 0.4234 (166697) | 0.4073 (163814) | 0.4068 (159485) |

**(14,4,2), ε=1/2** — divergent mass (pairs); rows r_obs, cols r_pred

| r_obs \ r_pred | r1 | r2 | r3 | r4 |
|---|---|---|---|---|
| r1 | 0.3347 (38831) | 0.3301 (38773) | 0.3085 (37994) | 0.3084 (35272) |
| r2 | 0.3805 (55392) | 0.3758 (55292) | 0.3553 (54387) | 0.3552 (51665) |
| r3 | 0.4115 (84300) | 0.4114 (84183) | 0.4025 (82651) | 0.4025 (79744) |
| r4 | 0.4313 (90252) | 0.4312 (90135) | 0.4223 (88603) | 0.4222 (84933) |

**(12,2,2) resolution decomposition (diagonal r_obs = r_pred)**

| ε | rung | n_windows | resolved mass | div mass | div (resolved) | div (unresolved) | state-level div mass | state P-next classes |
|---|---|---|---|---|---|---|---|---|
| 1 | r1 | 186 | 0.1704 | 0.0053 | 0.0004 | 0.0049 | 0.9776 | 126 |
| 1 | r2 | 209 | 0.1704 | 0.0056 | 0.0004 | 0.0052 | 0.9773 | 143 |
| 1 | r3 | 283 | 0.1742 | 0.0138 | 0.0036 | 0.0102 | 0.9484 | 186 |
| 1 | r4 | 293 | 0.1744 | 0.0137 | 0.0036 | 0.0101 | 0.9478 | 195 |
| 1/2 | r1 | 186 | 0.1723 | 0.0007 | 0.0000 | 0.0007 | 0.9810 | 238 |
| 1/2 | r2 | 209 | 0.1723 | 0.0008 | 0.0000 | 0.0008 | 0.9791 | 271 |
| 1/2 | r3 | 283 | 0.1741 | 0.0131 | 0.0017 | 0.0115 | 0.9522 | 342 |
| 1/2 | r4 | 293 | 0.1742 | 0.0131 | 0.0017 | 0.0114 | 0.9522 | 353 |

G1: **0** violations across all **72** (law, ε, r_obs, adjacent r_pred)
steps ~~(v0.1: "96")~~; v0.1.1 additionally asserts pair-set nesting at
every step (72 assertions pass).

## Predictions scored

- **R1 held at the tested law only, weakly** ~~(v0.1: "held")~~ — the
  "every windowed law" clause is untested: resolved mass 0.1704/0.1704/0.1742/0.1744 (ε=1),
  0.1723/0.1723/0.1741/0.1742 (ε=½) — nearly all of it is the U = 0
  RESET-visible sixth, point-mass at every rung by injectivity; the
  content rungs resolve almost nothing at L = 2. r3→r4 increment ≈ 0 ✓.
- **R2 REFUTED**: the r1→r4 rise (0.0053→0.0137, ε=1) is 38% resolved
  windows (0.0004→0.0036) and 62% unresolved (0.0049→0.0101); at ε=½,
  13% / 87%. The "up" force is **not** resolution to point masses.
- **R3 held, uninformatively** (0.0036 ≤ 0.9478). The state-level column
  reproduces the (12,12,2) full-context figures exactly, as it must
  (same endpoint marginal): 0.9776/0.9773/0.9484/0.9478 (ε=1).
- **R4 held**: resolved-window divergent mass 0.0036→0.0036 across the
  dip; the dip is on the unresolved side (0.0102→0.0101).
- **G1 held (theorem, 72/72 mass comparisons; 72/72 pair-set nesting
  assertions in v0.1.1)** ~~(v0.1: "96/96")~~.
- **G2 held, and stronger than stated**: at fixed r_pred, divergent mass
  is **monotone non-decreasing in r_obs in all 24 columns** (3 laws × 2
  ε × 4 r_pred). r_obs r3→r4 increment at (12,2,2): 0.0000 in every
  column, both ε ✓.
- **G3 held qualitatively** ~~(v0.1: "held exactly")~~: (12,2,2) ε=1
  diagonal r3→r4 net −0.000139; via (r_obs step at r_pred=r3, then
  r_pred step at r_obs=r4): +0.000033 − 0.000172; via the other path:
  −0.000156 + 0.000016. The observer term is small and positive, not
  zero; the split is path-dependent; the signs agree on both paths.

## Findings (v0.1)

1. **The day-seven non-monotonicity decomposes into two monotone
   effects.** Divergent mass is monotone non-increasing in the predicted
   record's rung (theorem; verified 96/96 as a gate) and monotone
   non-decreasing in the observer's rung (24/24 columns; no proof
   offered — see open question 1). The diagonal's r3→r4 sign is their
   sum: (12,2,2): 0 − 0.0001 → dip; (14,2,2) ε=1: +0.0030 − 0.0005 →
   rise; (14,4,2) ε=1: +0.0121 − 0.0005 → rise. ~~Which sign a law shows
   at r3→r4 is whether the lineage field refines the window partition
   there~~ *(v0.1.1: false as written — lineage refines the partition at
   (12,2,2) too, 283→293 windows, and the diagonal still dips.)* The
   sign is whether the observer-side refinement adds more divergent mass
   than the prediction-side fineness removes; how much lineage adds is
   the rung-geometry story already in the record.
2. **The observer effect is not point-mass resolution.** R2 refuted; the
   content rungs barely resolve L = 2 windows. It is partition refinement
   short of resolution. ~~Concentrated at r2→r3 (the `related` field) at
   L = 2 and spread across rungs at L = 4~~ *(v0.1.1: at (12,2,2) only;
   at (14,2,2) ε=½ the observer gains are r2→r3 +0.0109, r3→r4 +0.0833 —
   lineage dominates there.)* Where the gain sits is law-specific. *Why* `related` manufactures
   exact P-next coincidences with τ disagreements is not explained here.
3. **The predicted-record effect is small** at every law: ~~≤ 0.0005 at
   r3→r4 everywhere~~ ≤ 0.00061 at r3→r4 (max at (14,4,2) ε=1, r_obs=r2)
   *(v0.1.1)*; largest anywhere at (14,4,2) r2→r3 (−0.016 at r_obs = r4).
4. **Design remark for the exposure work.** "P-next at its rung" is the
   diagonal of a grid whose off-diagonal cells are meaningful: a coarse
   observer asked about a fine next record (r_obs < r_pred) is exactly
   the coarse-observer / fine-query configuration the exposure-gap
   query-class idea needs (`docs/exposure-gap-note-v0.1.md`). The grid
   machinery exists now; whether it belongs in the M1 exit set is a
   scope call for the PI, not this note.

## Open questions

1. Is observer-monotonicity (fixed r_pred, mass non-decreasing in
   r_obs) a theorem? Refining a partition does not obviously preserve
   exact-equality coincidences between mixtures. 24/24 says look for the
   reason; the reason is not in this note.
2. What structure in `related` produces the r2→r3 jump? Candidate:
   pairs of windows related by a symmetry of the kernel that P-next
   respects but lineage4/kinds2 do not. Untested.
3. Everything above is at δ = 0. Under the δ-close criterion the nesting
   argument (G1) needs restating — the pushforward is 1-Lipschitz in TV,
   so δ-closeness at the fine record implies δ-closeness at the coarse
   one and G1 survives; but the Δ-apart τ side is untouched. Worth one
   line in the threshold discussion when it lands.

## Caveats

- Exploratory (thresholds unfrozen; δ = 0 corner). m = 2, W = 4 are the
  frozen v0.2.4 values and these runs post-date that stamp, so they are
  confirmatory-compatible on m/W/𝒯 and exploratory on the class criterion.
- Resolution decomposition run at (12,2,2) only.
- Both scripts single-path (no independent second computation of the
  grid). The two theorem checks (state-level column = full-context
  figures; G1 pair-set nesting) are the internal gates — **asserted**
  as of v0.1.1; ~~in v0.1 they were printed, and G1's count was
  misreported as 96~~.
- Float printing of exact Fractions; equality tests are exact.
