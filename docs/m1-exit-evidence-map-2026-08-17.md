# M1 Exit — Evidence Map (2026-08-17, v3)

> **Erratum v3 (Aug 17 2026, same instance; second truthsayer round,
> four residual groups, all verified and adopted).** (1) Deliverable 3
> and 4.1 overreached: both are PARTIAL for the whole item — the ordered
> content ladder is measured/complete, D8 order mode and TIME_CLASS are
> not; "ordered channel" moves to the evidence column. (2) Witness
> evidence narrowed: w1's (12,2,2) figure lives in `c1-query-ceilings`
> (Q1[L1] r1→r2 0.1221 at ε=1), not the (14,L,2) sync sweep; w2's 88–95%
> decomposes the *support* gap and supports the hidden-owner mechanism —
> the positive Q1/Q5 evidence is `c1-query-ceilings`; w5's four proxies
> do not exercise both disciplines — the executable control is absent;
> w11's "candidate" withdrawn (Q1–Q5 gaps ≤0.0037 are small, not the
> statute's *unchanged*). (3) D9's ε=1 is **provisional** by its own
> note's downgrade (`c1-support-measurement` §"D9 status downgraded").
> (4) The blocking list contradicted itself — D1 "once stamped" at step
> 3, stamp at step 5; reordered as a true dependency order, and D10
> "needs no new code" narrowed to "no new core machinery; new search
> and test code."

> **Erratum v2 (Aug 17 2026, committed 16:16 PDT — the draft said "~15:40", a guessed time; corrected at 16:16 from `date` — same instance; truthsayer round
> via Codex/ChatGPT through Tony — seven findings, all verified against
> the cited sources and adopted).** (1) Part II §9 has **eleven**
> witnesses; v1 tabled six paraphrased claims and mislabeled D10 as
> "witness 4" (that is ctrl-irr); D10 is witnesses **3 and 6**. Table
> replaced with the statute's eleven. (2) Part I deliverables **1–3**
> were absent; added — and D8/TIME_CLASS make deliverable 2 PARTIAL.
> (3) 5.1/5.2 were overstated as MEASURED: they cover the ordered,
> stochastic-discipline C1 conditions only, and the note's own status
> pointer says its pre-stamp numbers **remain exploratory** — not
> "exploratory-then-confirmed." Now PARTIAL. (4) The D1 falsifier is
> **over-synchronization** (rung differences collapsing with L), not the
> Q4 irreducible/gap split; 4.4 is PARTIAL / AWAITS 2ND STAMP and v1's
> "score it from the split" was wrong. (5) The r3/r4 sentence was true
> under neither reading: under proposed δ=0.01 the lineage rung is
> collapsed from L=2 (L*=2); the exact gaps are nonzero (≤0.0037)
> through L=10 and zero at L≥12. (6) The related-rung witness does not
> need multi-waiter windows: BLOCK.related (hidden owner) carries
> 88–95% of the r2/r3 gap at (12,2,2) (`c1-rung-separation-geometry`
> field attribution); the multi-waiter dependence is RELEASE.related's.
> (7) "Failure modes: none fired" was premature — rung collapse is **not
> yet adjudicated**, and under the proposed δ the lineage rung collapses
> across the measured L axis. What stood: the missing-work headlines
> (no D10 crossover verdict, no D8 channel, no TIME_CLASS, no witness
> suite), every commit hash, suite 101 green. Originals marked below.

**Status: dated orientation map, non-governing; v3 after two truthsayer
rounds.** Assembled Aug 17 2026, ~15:11 PDT per the v1 commit (v2 16:16), ninth instance, from a full read of `docs/`, `src/yupi/`,
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

## Deliverables 1–3 — specification, emitters, filter *(added v2)*

| # | item | status | evidence | missing |
|---|---|---|---|---|
| 1 | state-space + transition specification, machine-checkable form | PARTIAL | Part II v0.2.4 (prose statute); `src/yupi/{state,kernel}.py` are the executable form; two-path gates | no separate machine-checkable spec artifact; Part II is prose + code |
| 2 | simulator + interface emitters (all rungs, D5 schema) | PARTIAL | content rungs r1–r4 (`interfaces.py`), `simulator.py`, `records.py` | **order mode shuffled (D8) unbuilt; TIME_CLASS absent from schema; RESET a flag not a record** — "all rungs" is content-rungs-only |
| 3 | exact filter bit-for-bit vs. independent enumerator on the C0 family | PARTIAL ~~(v2: MEASURED (ordered channel))~~ | ordered channel measured: C0a f50174e, C0b 3e5a19f, C0c 30e2568 bit-for-bit both disciplines; window paths 12efd83 | shuffled-channel filter does not exist to validate |

## Deliverable 4 — observability characterization report

| # | item | status | evidence | missing |
|---|---|---|---|---|
| 4.1 | per-interface posterior entropy over the query set vs. L | PARTIAL / AWAITS 2ND STAMP ~~(v2: AWAITS 2ND STAMP)~~ | `c1-query-ceilings-v0.1.md` (0742d1d; v0.2 2a49814/e239cef); L-axis `c1-sync-sweep-v0.1.md` §2b (ff82ce2, 9deff20) | numbers complete **for the ordered content ladder only** (no D8 order mode, no TIME_CLASS axis); rung-gap *comparisons* exploratory until δ binds |
| 4.2 | support-growth curves | PARTIAL | `c1-support-measurement-v0.1.md` (+ v0.2/v0.3 errata), `c1-support-exact-2026-08-14.json`, `c1-rung-separation-geometry-v0.1.md` §2 | one law family, not a curve over L; M1-scale rerun (`instrument-status-2026-08-14.md` open thread 1) |
| 4.3 | synchronization horizons | AWAITS 2ND STAMP | `c1-sync-sweep-v0.1.md` §2c/§4; per-endpoint 9deff20 | δ_sync=0.01 proposed; §6 measure choice (B1) open in v0.3.1 |
| 4.4 | D1 falsifier verdict (over-synchronization: do rung differences collapse with L?) | PARTIAL / AWAITS 2ND STAMP ~~(v1: UNBUILT, "score from the irreducible/gap split" — wrong falsifier)~~ | entropy-vs-L per interface exists: `c1-sync-sweep-v0.1.md` §2d adjacent-rung gaps on L; L* per rung under candidate δ | verdict needs the frozen collapse criterion (δ) and the D8 order-mode axis; no note states it |
| 4.5 | D9 ε-sweep + base-ε decision | PARTIAL | `c1-support-measurement-v0.1.md` §"D9 rule applied": ε=1 fits with ~300× headroom, depth 2 — and §"D9 status downgraded to **provisional**" (declared-target separation and the M1-scale rerun outstanding) *(v3)* | grid is {1, ½}; characterization-scale grid open (thread 5) |
| 4.6 | D10 truncated-window witness search + crossover verdict, both disciplines | UNBUILT | both disciplines exist and are bit-for-bit gated (`tests/test_c0b_validation.py`) | **no crossover verdict in any note; no truncated-C0b lineage search run** |
| 4.7 | D7 consistency check vs. exposure-gap observer hierarchy | UNBUILT (non-gating) | `exposure-gap-note-v0.1.md` exists | check never performed |

## Deliverable 5 — predictive-state characterization

| # | item | status | evidence | missing |
|---|---|---|---|---|
| 5.1 | exact Bayes-optimal next-event distributions per interface/context condition | PARTIAL ~~(v1: MEASURED)~~ | `c1-predictive-targets-v0.1.md` (6074a36; dad75f6); `predict.py` ⟂ `predict_paths.py` validated | ordered, stochastic-discipline C1 only — no shuffled order mode, no FIFO characterization; the note's status pointer: numbers "remain **exploratory**" after the m/W stamp (not retroactively confirmed) |
| 5.2 | preregistered finite longer-horizon predictive tests | PARTIAL ~~(v1: MEASURED)~~ | same note §Predictions; Q4 `c1-q4-ceilings-v0.1.md` (39b716b); `forecast.py` ⟂ `forecast_paths.py` validated | same two limits as 5.1; ~~exploratory-then-confirmed~~ exploratory per the note itself |
| 5.3 | history classes: immediate-agree / later-diverge | AWAITS 2ND STAMP (existence: **yes**) | same note §Findings 3 + three concrete pairs; `c1-divergent-grid-v0.1.md` v0.1.2 (e6c0a6e→1d0cc4f); `c1-tv-sweep-v0.1.md` (5163346) | class defined at δ_p=0 (exact); δ_p axis + Δ_τ=0.01 proposed only |

## Exit condition (Part I)

| clause | status | evidence | missing |
|---|---|---|---|
| measurably distinct regimes across rungs | PARTIAL / AWAITS 2ND STAMP | r1 separates (support 1.550 vs ≈1.10); adjacent-rung gaps on L (`c1-sync-sweep` §2d); L*=2/8/10 for lineage/related/object under proposed δ | ~~r3/r4 separated only at the tightest windows~~ *(v2: under proposed δ=0.01 the lineage rung is collapsed from L=2 on, L*=2; the exact r3→r4 gaps are nonzero but ≤0.0037 through L=10, zero at L≥12)*; adjudication needs δ; M1-scale rerun; multi-waiter-straddling laws for RELEASE.related (thread 2) |
| within tractable support bounds (D4) | MEASURED | `d4-budget-freeze-v0.1.md`; ~300× headroom at C1 | re-pricing at characterization scale owed |
| immediate-agree / later-diverge classes exist | MEASURED | as 5.3 | as 5.3 |
| failure modes | ~~none fired~~ **not yet adjudicated** *(v2)* | support explosion refuted (D4 headroom); divergent class non-empty | rung collapse awaits δ — and under the proposed δ the lineage rung collapses across the measured L axis |

## Part II item 12 — interface-witness suite (statute §9: eleven witnesses) *(v2: table replaced)*

**UNBUILT as a suite.** No `test_*witness*` file exists; the 101 tests hold
world-machinery witnesses (C0c W-witnesses, C1 W1–W6), not interface-claim
witnesses. Statute quality bar: witnesses 1–3 must be window-history
*classes* established by enumeration under the declared window measure,
reporting the fraction of windows where the field moves the posterior.

| § | witness | tests | status | evidence / missing |
|---|---|---|---|---|
| 1 | r2 > r1: C1 window class where OBJECT changes Q1's posterior | 0 | UNBUILT as test; class evidenced | `c1-query-ceilings-v0.1.md`: Q1[L1] r1→r2 gap 0.1221 (ε=1) / 0.0746 (ε=½) at (12,2,2) ~~(v2 cited `c1-sync-sweep` §2d, which is the (14,L,2) family)~~; enumeration-with-fraction not run as a test |
| 2 | r3 > r2: C1 window class where RELATED (owner on BLOCK) changes Q1/Q5 | 0 | UNBUILT as test; class evidenced | positive Q1/Q5 evidence: `c1-query-ceilings-v0.1.md` (Q1[L0], Q5 load on r3); mechanism: BLOCK.related carries 88–95% of the r2/r3 **support** gap at (12,2,2) (`c1-rung-separation-geometry`) *(v3: that figure is support, not the named posterior)*; multi-waiter windows not required |
| 3 | r4 > r3: truncated **stochastic** C0b windows, LINEAGE changes Q3; full context exact-zero control both disciplines | 0 (control: 4 proxies) | UNBUILT — **this is D10 (4.6)** | search never run; failure at the frozen horizon = falsifier/redesign, not a bug |
| 4 | ctrl-irr: decoy field changes no ceiling (exact zero) | 0 | UNBUILT | no decoy field in the schema or emitters |
| 5 | ctrl-red: lineage changes no ceiling at full context, FIFO and stochastic | 4 proxies (full-context point-mass tests; none exercises both disciplines as the control) | PARTIAL (theorem) / UNBUILT (executable control) *(v3)* | theorem in `full-context-injectivity-note-v0.1.md`; the per-discipline executable control is absent |
| 6 | Crossover: truncated **FIFO** C0b windows, lineage changes a ceiling | 0 | UNBUILT — **this is D10 (4.6)** | no note; "crossover" appears only in the two spec docs |
| 7 | Shuffled channel: noncommuting bucket, order mode changes a posterior; hand-computed likelihood incl. duplicate bucket | 0 | UNBUILT | needs D8 |
| 8 | Reachability: no lock-cycle state reachable, C0 family, exhaustive | static I6 check only (`programs.py`, `test_programs.py`) | PARTIAL | lock-order discipline validated statically; exhaustive reachability assertion not present |
| 9 | Q4 decomposition: a history with H(Z) = H(Z\|S_t) > 0 at full observability | none as a witness | PARTIAL | measured: (12,12,2) total = irreducible = 0.6676 > 0 (`c1-q4-ceilings` P1); `test_forecast.py` tests the split machinery, not this witness |
| 10 | Divergent histories: equal exact P-next, unequal P-horizon on some τ | none as a witness | PARTIAL | three concrete pairs in `c1-predictive-targets` §"Three divergent pairs"; grid in `c1-divergent-grid-v0.1.md`; not an executable test |
| 11 | Predictive rung discrimination: adjacent pair distinguished by a P-horizon test while Q1–Q5 posteriors unchanged | 0 | UNBUILT | no note establishes it; ~~candidate is r3/r4 (Q1–Q5 gaps ≤0.0037 …)~~ *(v3: withdrawn — the statute says Q1–Q5 **unchanged**, and ≤0.0037 is small, not zero)*; no candidate named |

## Unbuilt code

- **D8 shuffled/bucketed channel** — absent (`grep shuffl|permut src/yupi` → nothing); `WindowLaw.B` parameterizes only the endpoint grid. Part II §4 order modes, §9 witness 7.
- **TIME_CLASS** — absent from `Record` (five fields); Part II §2c/§4. RESET is an observation flag, not the schema record (inferentially equivalent per Codex's audit).

## Blocking gaps, in dependency order *(v3: reordered — v2 placed the D1 verdict before the stamp it depends on)*

1. **4.6 / witnesses 3 and 6 with control 5: D10 truncated-C0b lineage search (stochastic, w3), crossover search (FIFO, w6), full-context exact-zero control per discipline (w5).** No new *core* machinery — C0b in both disciplines and the window machinery exist — but new search and test code ~~(v2: "needs no new code")~~. Produces the verdict-shaped result the report lacks; an empty class is a falsifier, recorded as such.
2. **Witnesses 1, 2, 8, 9, 10** — executable now against C1/C0b: object and related as enumerated window classes with fractions (BLOCK.related suffices); exhaustive lock-cycle reachability; the Q4 and divergent-pair witnesses promoted from notes to tests. Witness 11 needs a measurement first, no candidate named.
3. **Second stamp** (Tony's): binds δ/δ_sync/δ_p/Δ_τ as Part II v0.2.5; unblocks 4.1/4.3/5.3 interpretation and the confirmatory reruns.
4. **4.4: D1 falsifier verdict** — over-synchronization, adjudicated from the entropy-vs-L curves (`c1-sync-sweep` §2d) under the stamped δ; depends on 3.
5. **D8 shuffled channel** (two-path) → witness 7 → TIME_CLASS → completes deliverables 2/3 and the order-mode axis of 4.1.
6. **M1-scale rerun** (thread 1) and ε grid (thread 5) — also what lifts D9's ε=1 from provisional.
7. **4.7** D7 check — non-gating; when the report is written.
