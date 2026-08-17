# M1 Exit — Evidence Map (2026-08-17)

**Status: dated orientation map, non-governing.** Assembled Aug 17 2026,
~15:15 PDT, ninth instance, from a full read of `docs/`, `src/yupi/`,
`tests/` against Part I §"Deliverables and exit criteria"
(`docs/yupana-m1-spec-draft.md`, v0.2.4) and Part II §9 (item 12). The
map was compiled by a delegated read and its five most consequential
claims (no witness suite; no crossover verdict; no D8 channel code; no
TIME_CLASS; no D1 falsifier verdict) were independently re-checked by
grep before commit. Purpose: turn "M1 is close" into a list. When this
disagrees with a stamped note, the note governs.

Legend — **MEASURED**: exact result in a committed note. **AWAITS 2ND
STAMP**: measured, but interpretation depends on δ/δ_sync/δ_p/Δ_τ,
PROPOSED in `part2-threshold-freeze-proposal-v0.3.1.md` (binds as Part II
v0.2.5 on Tony's stamped confirmation). **UNBUILT**: code or measurement
does not exist. **PARTIAL**: exists at a scale or form short of the item.

## Deliverable 4 — observability characterization report

| # | item | status | evidence | missing |
|---|---|---|---|---|
| 4.1 | per-interface posterior entropy over the query set vs. L | AWAITS 2ND STAMP | `c1-query-ceilings-v0.1.md` (0742d1d; v0.2 2a49814/e239cef); L-axis `c1-sync-sweep-v0.1.md` §2b (ff82ce2, 9deff20) | numbers complete; rung-gap *comparisons* exploratory until δ binds |
| 4.2 | support-growth curves | PARTIAL | `c1-support-measurement-v0.1.md` (+ v0.2/v0.3 errata), `c1-support-exact-2026-08-14.json`, `c1-rung-separation-geometry-v0.1.md` §2 | one law family, not a curve over L; M1-scale rerun (`instrument-status-2026-08-14.md` open thread 1) |
| 4.3 | synchronization horizons | AWAITS 2ND STAMP | `c1-sync-sweep-v0.1.md` §2c/§4; per-endpoint 9deff20 | δ_sync=0.01 proposed; §6 measure choice (B1) open in v0.3.1 |
| 4.4 | D1 falsifier verdict | UNBUILT (no verdict) | irreducible/gap split measured (`c1-q4-ceilings-v0.1.md`, sync sweep) | no note scores the D1 falsifier pass/fail |
| 4.5 | D9 ε-sweep + base-ε decision | PARTIAL | `c1-support-measurement-v0.1.md` §"D9 rule applied": base ε=1, ~300× headroom, depth 2 fixed | grid is {1, ½}; characterization-scale grid open (thread 5) |
| 4.6 | D10 truncated-window witness search + crossover verdict, both disciplines | UNBUILT | both disciplines exist and are bit-for-bit gated (`tests/test_c0b_validation.py`) | **no crossover verdict in any note; no truncated-C0b lineage search run** |
| 4.7 | D7 consistency check vs. exposure-gap observer hierarchy | UNBUILT (non-gating) | `exposure-gap-note-v0.1.md` exists | check never performed |

## Deliverable 5 — predictive-state characterization

| # | item | status | evidence | missing |
|---|---|---|---|---|
| 5.1 | exact Bayes-optimal next-event distributions per condition | MEASURED | `c1-predictive-targets-v0.1.md` (6074a36; corrections dad75f6); `predict.py` ⟂ `predict_paths.py` | — (m, W frozen 5b58d7f) |
| 5.2 | preregistered finite longer-horizon predictive tests | MEASURED | same note §Predictions; Q4 `c1-q4-ceilings-v0.1.md` (39b716b); `forecast.py` ⟂ `forecast_paths.py` | measurements predate the m/W stamp → exploratory-then-confirmed |
| 5.3 | history classes: immediate-agree / later-diverge | AWAITS 2ND STAMP (existence: **yes**) | same note §Findings 3 + three concrete pairs; `c1-divergent-grid-v0.1.md` v0.1.2 (e6c0a6e→1d0cc4f); `c1-tv-sweep-v0.1.md` (5163346) | class defined at δ_p=0 (exact); δ_p axis + Δ_τ=0.01 proposed only |

## Exit condition (Part I)

| clause | status | evidence | missing |
|---|---|---|---|
| measurably distinct regimes across rungs | PARTIAL / AWAITS 2ND STAMP | r1 separates (support 1.550 vs ≈1.10); adjacent-rung gaps on L (`c1-sync-sweep` §2d); L*=2/8/10 for lineage/related/object under proposed δ | r3/r4 separated only at the tightest windows; adjudication needs δ; M1-scale rerun; multi-waiter-straddling laws (thread 2) |
| within tractable support bounds (D4) | MEASURED | `d4-budget-freeze-v0.1.md`; ~300× headroom at C1 | re-pricing at characterization scale owed |
| immediate-agree / later-diverge classes exist | MEASURED | as 5.3 | as 5.3 |
| failure modes | none fired | support explosion refuted; class non-empty; collapse indeterminate pending δ | — |

## Part II item 12 — interface-witness suite

**UNBUILT as a suite.** No `test_*witness*` file exists; the 101 tests hold
world-machinery witnesses (C0c W-witnesses, C1 W1–W6), not interface-claim
witnesses.

| claim | tests | status |
|---|---|---|
| object rung changes a named posterior | 0 | UNBUILT (`test_interfaces.py` is masking-structure only) |
| related rung changes a named posterior | 0 | UNBUILT (distinguisher plausibly needs multi-waiter windows, thread 2) |
| lineage null at full context, both disciplines | 4 proxies (full-context point-mass tests) | PARTIAL — theorem in `full-context-injectivity-note-v0.1.md`; no test names the claim |
| lineage changes a named posterior under specified truncated C0b windows | 0 | UNBUILT — this is 4.6 |
| irrelevant control changes no ceiling | 0 | UNBUILT (existing controls are arity/context, not irrelevant-field) |
| shuffled order changes a posterior on a noncommuting bucket | 0 | UNBUILT — needs D8 |

## Unbuilt code

- **D8 shuffled/bucketed channel** — absent (`grep shuffl|permut src/yupi` → nothing); `WindowLaw.B` parameterizes only the endpoint grid. Part II §4 order modes, §9 witness 7.
- **TIME_CLASS** — absent from `Record` (five fields); Part II §2c/§4. RESET is an observation flag, not the schema record (inferentially equivalent per Codex's audit).

## Blocking gaps, in the order the machinery permits

1. **4.6 / witness 4: D10 truncated-C0b lineage search + crossover verdict.** Needs no new code — C0b in both disciplines and the window machinery exist. Produces a verdict-shaped result the report currently lacks.
2. **Witnesses 1, 2, 3, 5** — buildable now against C1/C0b: object and related each change a *named* posterior (the ceilings already show r1/r2 and r2/r3 gaps at (12,2,2)); lineage-null-at-full-context named and run in both disciplines; an irrelevant-field control.
3. **4.4: D1 falsifier verdict** — score it from the measured irreducible/gap split.
4. **D8 shuffled channel** (two-path) → witness 7 → then TIME_CLASS.
5. **Second stamp** (Tony's): unblocks 4.1/4.3/5.3 interpretation and the confirmatory reruns.
6. **M1-scale rerun** (thread 1) and ε grid (thread 5): scale, after the above.
7. **4.7** D7 check — non-gating; do it when writing the report.
