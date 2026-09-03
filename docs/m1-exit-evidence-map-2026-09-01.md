# M1 Exit — Evidence Map (2026-09-01, v4)

**Status: dated orientation map, non-governing; v4 is a full re-derivation,
not an erratum to v3.** Written 2026-09-01 08:44 PDT (`date` in the writing command) by the
instance following Yupaq, from a fresh read of every note, artifact, test file
and statute section cited below, against Part I §"Deliverables and exit
criteria" (`yupana-m1-spec-draft.md`) and Part II §9 (`yupana-m1-part2-semantics-draft.md`,
v0.2.6). The Aug-17 v3 map (`m1-exit-evidence-map-2026-08-17.md`) is preserved
unchanged with its addenda; this file supersedes its *statuses and blocking
order* only. When this map disagrees with a stamped note, the note governs.
Suite at writing: 204 tests collected.

> **Pointer (2026-09-03 09:42 PDT):** the witness-11 "candidate region" named below at (14,12,2) is empty a priori — at L ≥ 12 the r1 window partition already equals the r4 partition, so no functional of the belief can separate rungs there. The search was run where windows split (L ≤ 10); result and readings in `w11-predictive-rung-search-v0.1.md`; see the addendum at the end of this file. Nothing below is rewritten.

**Why a v4.** v3 predates five adjudications that changed the frontier:
the 2026-08-20 kernel erratum and corrected-kernel reruns (`audit-adjudication-2026-08-20.md`,
`corrected-kernel-rerun-v0.1.md`, `sweep-rerun-comparison-2026-08-21.md`);
the second stamped decision, Part II **v0.2.5** (2026-08-21, thresholds
frozen: δ = δ_sync = Δ_τ = 0.01, δ_p as a reporting axis) and **v0.2.6**
(2026-08-24, κ in the tuple; canonical-naming track); the held-out Tier 1
confirmatory round (`held-out-confirmation-v0.1.md`, v0.1.1); the D10
verdict (`d10-lineage-verdict-v0.1.md`, v0.1.1, 2026-08-24); and the D8
channel — built, measured under preregistration in both worlds, truthsayer-
reviewed, and witness 7 adjudicated (`d8-shuffled-channel-note-v0.1.md`,
`d8-attribution-{prereg,c0b-note,c1-note}-v0.1.md`, addendum in the v3 map,
2026-08-29). v3's blocking items 1, 3, 4 (in part) and 5 (in part) are
discharged; what remains is re-derived in §"Blocking gaps" below.

**Two standing labels on every number in this map.** (1) *Kernel:* results
measured before fix `d69fa87` (2026-08-20) are **buggy-kernel exploratory**;
corrected raws exist for every such note except `c1-rung-separation-geometry-v0.1.md`
(`artifact-status.json`: rerun-pending). Qualitative structure survived
re-verification everywhere; magnitudes drift ≤0.004 at T_ep = 12 and ≤0.041
at (14,4,2). (2) *Naming:* per Part II v0.2.6 Clause 2′, every posterior,
ceiling, theorem and witness is a **structural-characterization quantity under
the canonical injection σ₀** — not a Bayes ceiling for the random-naming corpus
process, and not evidence of D3 binding generalization, until the §2 bridge
exists (`tests/test_naming_counterexample.py` pins why: 1.208 vs 1.000/1.483
bits at C1 tick 4).

Legend — **MEASURED**: exact result in a committed note (corrected kernel
unless marked). **CONFIRMATORY**: measured after the governing stamp under a
preregistration or on held-out laws, scored as written. **EXPLORATORY**:
measured before the governing stamp, or outside any preregistration.
**PARTIAL**: exists at a scale or form short of the item. **UNBUILT**: code or
measurement does not exist. **OWED**: unblocked and small — a wording or
test-pinning task with its inputs already committed. Witness rows use
**SATISFIED** per the statute's own wording.

## Deliverables 1–3 — specification, emitters, filter

| # | item | status | evidence | missing |
|---|---|---|---|---|
| 1 | state-space + transition specification, machine-checkable form | PARTIAL | Part II v0.2.6 (prose statute, now Markov for ε < 1 with κ; invariants I1–I7); `src/yupi/{state,kernel}.py` executable form; `check_invariants` incl. the general I6 wait-for-cycle check | no separate machine-checkable spec artifact; statute is prose + code |
| 2 | simulator + interface emitters (all rungs, D5 schema) | PARTIAL *(narrowed)* | content rungs r1–r4 (`interfaces.py`); **D8 shuffled order mode built** (`shuffled.py`, `shuffled_window.py`; `tests/test_shuffled_channel.py`) and measured in both worlds | **TIME_CLASS absent from `Record`** (five fields; `window.py`: "still awaits the schema extension") — the anchored condition of Part II §2c/§4 has no schema carrier; RESET remains an observation flag, not a record |
| 3 | exact filter bit-for-bit vs. independent enumerator on the C0 family | PARTIAL *(narrowed)* | ordered channel: C0a f50174e, C0b 3e5a19f, C0c 30e2568, both disciplines; window paths 12efd83; **shuffled channel: filter matches enumerator bit-for-bit** (`test_shuffled_filter_matches_enumerator_bit_for_bit`), likelihood validated by hand incl. m > 1 | the shuffled two-path gate is parametrized on **C0b only** (three cells: stoch r4 B2 H6, fifo r1 B2 H6, stoch r2 B3 H6) — C0a/C0c shuffled gates absent |

## Deliverable 4 — observability characterization report

| # | item | status | evidence | missing |
|---|---|---|---|---|
| 4.1 | per-interface posterior entropy over the query set vs. L | PARTIAL: ordered ladder MEASURED + CONFIRMATORY; order-mode axis MEASURED; TIME_CLASS axis UNBUILT | ordered ladder: `c1-query-ceilings-v0.1.md` with corrected raws `c1-*-corrected-2026-08-20.json`; L-axis `c1-sync-sweep-corrected-2026-08-21.json`; **confirmatory** on held-out laws F2 (14, L even, 2) ε ∈ {¼, ⅝}, F3′ (14, L odd, 1) ε ∈ {1, ½}, F1 (16, L even, 2) — 42 ceiling raws `*-heldout-2026-08-2{1,3}.json`; **order-mode axis** as the D8 contrast Δ = I(S; O_ord \| O_shuf): C0b B = 3 (84 cells), C1 v0.2 (716 cells) + v0.3 (173 cells), corrected per-endpoint artifacts `d8-attribution-*-corrected-2026-08-29.json` | TIME_CLASS (anchored) axis; M1-scale rerun |
| 4.2 | support-growth curves | PARTIAL | `c1-support-measurement-v0.1.md` (+ errata), `c1-rung-separation-geometry-v0.1.md` §2 | one law family, not a curve over L; geometry note is the **only** note still without corrected raws; M1-scale rerun |
| 4.3 | synchronization horizons | MEASURED + CONFIRMATORY | δ_sync = 0.01 frozen (v0.2.5); measure (b) statutory, (a) co-reported; baseline (14,·,2) L\* = 12/10/10/10 (r1…r4) at ε = 1 (`held-out-confirmation` §2 table); held-out Tier 1: r2 = r3 = r4 at every fresh cell, r1 strictly later except (F3′, ε = ½, b) where all four are 11 (v0.1.1 item 3); F1 (16,·,2): ε = ½ **identical** to baseline, ε = 1 pack rises to 12 = r1 (exploratory, no prediction covered T_ep = 16) | δ/TV sweeps at the 16-laws (queued, exploratory) |
| 4.4 | D1 falsifier verdict (over-synchronization) | Part A DONE; Part B **OWED** (unblocked); Part C decided (no contingency) | `d1-falsifier-verdict-v0.1.md`: **Part A FIRED at full context, by theorem** (`full-context-injectivity-note-v0.1.md`; kernel-independent); Part B curves exist on the corrected kernel and δ is now frozen — collapse horizons at (14,·,2), both ε: L\* = 2 (r3→r4), 8 (r2→r3), 10 (r1→r2) (Part II §6, v0.2.5 text); Part C: PI decision 2026-08-20 15:10 PDT, verbatim in the note — no contingency invoked; evidence set (a) corrected-kernel D1 measurements ✔ (Aug 21), (b) D10 w3/w6 + control 5 ✔ (Aug 24), (c) D8 witness 7 ✔ (Aug 29), **(d) predictive-rung test (witness 11) ✘** | a note stating Part B's formal verdict under the frozen δ on the corrected curves (small; inputs committed); witness 11 — the sole outstanding item of the PI's Part C evidence set |
| 4.5 | D9 ε-sweep + base-ε decision | PARTIAL | `c1-support-measurement-v0.1.md` §"D9 rule applied" (ε = 1 fits, ~300× headroom) and §"D9 status downgraded to provisional"; ε grid now {¼, ½, ⅝, 1} across the held-out families via `eps_grid.py` (`YUPI_EPS`, exact fractions) | provisional stands: declared-target separation and the M1-scale rerun outstanding |
| 4.6 | D10 truncated-window witness search + crossover verdict, both disciplines | MEASURED (preregistered, corrected kernel) | prereg `d10-lineage-search-prereg-v0.1.md` (stamp 080f937, before any posterior); verdict v0.1.1: **witness 3 ESTABLISHED** (e.g. (8,2) Δ_stoch = 0.085 bits, prevalence 0.150; global 8.45×δ, single histories ≈ 1 bit); **witness 6 ESTABLISHED** (FIFO exactly null at T_ep = 6, informative at T_ep ≥ 8 short L: (8,2) 0.029, (10,2) 0.036, (10,4) 0.023); frontiers L ≤ T_ep − 4 (stoch), L ≤ T_ep − 6 (FIFO) in T_ep ∈ {6, 8, 10}; interaction Δ_stoch − Δ_FIFO > 0 in every informative cell; 54–63 % of FIFO gain is offset-mixture amplification, frontiers survive anchoring; gate 2 uncapped (all windows); 6 regressions `tests/test_d10_witnesses.py` | none for the item; open question (exploratory): whether any C1 law reaches an informative cell (C1 r3→r4 is informative-and-collapsed: 0.0037 at 14, 0.0066 at 16) |
| 4.7 | D7 consistency check vs. exposure-gap observer hierarchy | UNBUILT (non-gating) | `exposure-gap-note-v0.1.md` exists | check never performed; when the report is written |

## Deliverable 5 — predictive-state characterization

| # | item | status | evidence | missing |
|---|---|---|---|---|
| 5.1 | exact Bayes-optimal next-event distributions per interface/context condition | PARTIAL (EXPLORATORY) | `c1-predictive-targets-v0.1.md` + corrected raws (2026-08-20); `predict.py` ⟂ `predict_paths.py` | ordered stochastic C1 only; no shuffled-mode or FIFO characterization of the next-event law; the note's own status: exploratory w.r.t. m/W |
| 5.2 | preregistered finite longer-horizon predictive tests | PARTIAL, with two CONFIRMATORY rounds scored | held-out Tier 1 P1–P5 at v0.2.5 thresholds (`c1-heldout-tier1-score-2026-08-22.json`): **1 pass (P1 as written: r2 = r3 = r4, r1 ≥ +2 at both new ε — criterion passed, stated mechanism wrong per v0.1.1), 3 fail (P2 inverted — ε is scheduler randomness, not trace coverage; P3 bound set from the wrong law; P5 conjunctive, P5a component survives), 1 ill-posed (P4)** — every failure traced to a writing-time error, thresholds not implicated (v0.1.1); D8 prereg predictions P3a PASS, P3b PASS 3/3 (`d8-attribution-predictions-score-2026-08-28*.json`) | Q4 W4 corrected: (12,12,2) total = irreducible = 0.6677 bits, gap exactly 0 at every rung and endpoint (`c1-q4-ceilings-12-12-2-W4-corrected-2026-08-20.json`); no FIFO/shuffled-mode predictive tests |
| 5.3 | history classes: immediate-agree / later-diverge | MEASURED + CONFIRMATORY (existence) | δ_p = 0 exact classes: three concrete pairs (`c1-predictive-targets` §"Three divergent pairs"), grid (`c1-divergent-grid-v0.1.md` v0.1.2, corrected raws), TV sweep; **held-out P5a: pair_prob(δ_p = 0) > 0 at fresh laws — PASS**; observer-monotonicity is **not** a refinement theorem (`c1-observer-monotonicity-note-v0.1.md`; counterexample pinned `tests/test_observer_monotonicity_counterexample.py`) | P5b (δ_p = 10⁻⁴ prevalence jump ≥ 10×) FAILED (1.0–2.6×) — the prevalence *shape* along δ_p is unpredicted; Δ_τ = 0.01 frozen, δ_p reported as an axis |

## Exit condition (Part I)

| clause | status | evidence | missing |
|---|---|---|---|
| measurably distinct regimes across rungs | PARTIAL — three rungs distinct at short L, the fourth collapsed in C1 | under frozen δ at (14,·,2): r1→r2 and r2→r3 gaps material at L ≤ 4 (0.06–0.18 bits — buggy-kernel figures, drift ≤ 0.041; the L\* values are corrected-kernel), L\* = 10 / 8; r3→r4 < δ at **every** measured C1 law and L (max 0.0037 at T_ep = 14, 0.0066 at 16) — *informative and collapsed*, not empty; held-out P1 PASS: the ladder generalizes to fresh ε and B = 1; lineage grip lives in C0b short-L windows (D10 frontiers) | formal D1 Part B wording (OWED); at (16, ε = 1) measure-(b) separation vanishes (all L\* = 12) — horizon dependence unassigned; witness 11; M1-scale rerun |
| within tractable support bounds (D4) | MEASURED | `d4-budget-freeze-v0.1.md` v0.1 + **erratum E2 (2026-08-27, B4′ RSS 2 → 4 GB, enacted by the researcher under the PI's decision rule)**; C1 ~300× headroom; D8 grids priced blind: v0.2 716/1344 admitted, v0.3 173/628 of the refused; the next step (15,15,1) r1–r3 refused at 4.81 GB and **not proposed** | re-pricing at characterization scale |
| immediate-agree / later-diverge classes exist | MEASURED + CONFIRMATORY | as 5.3 | as 5.3 |
| failure modes | ADJUDICATED IN PART | rung collapse: fires for the lineage rung in C1 at all L, and for r1–r3 along L with horizon 8–10 (Part A by theorem at full context); PI decision: **no contingency invoked** pending the four-item evidence set, of which only witness 11 remains; support explosion: not fired (grid refusals are pricing under a rule, not explosion); divergent class: non-empty | Part B wording; witness 11; then the PI's minimal targeted intervention selection (candidate set broadened 2026-08-20: exposable workload branches, structured nonterminating workloads, rung redesign, scheduler/device entropy; private workload coins last) |

## Part II §9 — interface-witness suite (item 12): eleven witnesses

The suite exists **in part** as executable tests (`test_d10_witnesses.py` 6,
`test_shuffled_channel.py`, `test_naming_counterexample.py` 2,
`test_observer_monotonicity_counterexample.py` 2), not as one `test_*witness*`
file; the statute's quality bar for witnesses 1–3 (window-history class by
enumeration under the declared window measure, fraction reported) is met by
witness 3 only.

| § | witness | status | evidence / missing |
|---|---|---|---|
| 1 | r2 > r1: C1 window class where OBJECT changes Q1 | PARTIAL (class evidenced, not enumerated as a witness) | Q1[L1] r1→r2 gap 0.1221 (ε = 1) / 0.0746 (ε = ½) at (12,2,2), `c1-query-ceilings` (buggy-kernel figure; corrected raw exists); no enumeration-with-fraction test |
| 2 | r3 > r2: C1 window class where RELATED (owner on BLOCK) changes Q1/Q5 | PARTIAL (class evidenced) | Q1[L0], Q5 load on r3 (`c1-query-ceilings`); BLOCK.related carries 88–95 % of the r2/r3 *support* gap (`c1-rung-separation-geometry`, rerun pending); no test |
| 3 | r4 > r3: truncated stochastic C0b windows, LINEAGE changes Q3; full-context exact-zero control | **SATISFIED** | D10 verdict v0.1.1, ESTABLISHED; `test_witness3_stochastic_positive_at_tstar`; control: `test_full_context_exact_zero[stochastic]` |
| 4 | ctrl-irr: decoy field changes no ceiling | UNBUILT | no decoy field in schema, emitters or tests (`grep -i decoy src/yupi` → nothing) |
| 5 | ctrl-red: lineage changes no ceiling at full context, FIFO and stochastic | **SATISFIED** (executable, both disciplines) | `test_full_context_exact_zero[fifo]`, `[stochastic]` (C0b, T_ep = L = 6: zero informative histories, Δ = 0.0); theorem `full-context-injectivity-note-v0.1.md` |
| 6 | Crossover: truncated FIFO C0b windows, lineage changes a ceiling | **SATISFIED** | D10 verdict v0.1.1, ESTABLISHED; `test_witness6_fifo_null_at_tstar_positive_at_8`; mechanism pinned (`test_fifo_mechanism_is_pure_thread_order`) |
| 7 | Shuffled channel: noncommuting bucket; hand-computed likelihood incl. m > 1 | **SATISFIED** (existence, both worlds; adjudicated 2026-08-29) | v3 map addendum; `test_likelihood_duplicate_records_m_greater_than_one`, `test_w7_c0b_supplies_noncommuting_bucket_at_masked_lineage`, `test_w7_c1_r4_wait_queue_bucket_at_B3`; C1 ε = 1 cells are informative and **collapsed under δ** — reported as such, not promoted |
| 8 | Reachability: no lock-cycle state reachable, C0 family, exhaustive | PARTIAL | `check_invariants` I6 is a general wait-for-cycle check (`state.py`); asserted over the exhaustive reachable space for **C0c** (`test_state_invariants_all_reachable_states`) and **C1** (`test_c1_reachable_space_exhausts_and_is_invariant_clean`); C0a/C0b exhaustive assertion absent (static `validate_lock_order` only) |
| 9 | Q4 decomposition: H(Z) = H(Z \| S_t) > 0 at full observability | PARTIAL (measured, not pinned) | corrected (12,12,2) W4: total = irreducible = 0.6676559784702015 bits, gap 0.0 at every rung and endpoint; no witness test |
| 10 | Divergent histories: equal exact P-next, unequal P-horizon on some τ | PARTIAL (measured + confirmed, not pinned) | three concrete pairs; grid; held-out P5a PASS; the pinned counterexample is an abstract 3-state model, not a Yupana pair |
| 11 | Predictive rung discrimination: adjacent pair separated by a P-horizon test while Q1–Q5 unchanged | UNBUILT — **now the single outstanding item of the D1 Part C evidence set** | v3 withdrew the r3/r4 candidate because gaps ≤ 0.0037 are small, not zero. **Candidate region re-derived here:** at (14, L, 2) every adjacent Q1–Q5 gap is *exactly zero* by L = 12 while L < T_ep (D1 note Part B; `c1-sync-sweep-corrected-2026-08-21.json`) — the statute's "unchanged" holds exactly there. The witness question becomes: does any τ ∈ 𝒯 (W = 4 / 8) separate an adjacent pair at (14,12,2)? Executable against existing machinery; unmeasured; recorded as a candidate, not a claim |

## Unbuilt code

- **TIME_CLASS** — absent from `Record`; Part II §2c/§4 (maskable absolute bucket index ⌊(t−1)/B⌋; base masks it, anchored unmasks it). Completes deliverable 2 and 4.1's third axis.
- **Witness-suite executables** for w1, w2 (C1 window-class enumeration with fractions), w4 (needs a decoy field first), w8 (C0a/C0b exhaustive I6), w9, w10 (pin Yupana instances), w11 (search).

## Blocking gaps, in dependency order (v4)

1. **D1 Part B formal wording** under frozen δ on the corrected curves — OWED; all inputs committed (Part II §6 L\*, `c1-sync-sweep-corrected-2026-08-21.json`, held-out §2). A paragraph appended to `d1-falsifier-verdict-v0.1.md`, dated.
2. **Witness 11** — design and run the search in the candidate region above (exact Q1–Q5 equality at (14,12,2)), both ε; an empty result is a falsifier for the D2 disjunctive clause (b) at this world and is recorded as such. This closes the PI's Part C evidence set and unblocks the intervention-selection decision (PI's).
3. **TIME_CLASS** schema extension → anchored condition as a rung-style unmasking → 4.1's third axis; then deliverable 2 is complete except the RESET-record question.
4. **Witness-suite executables** (w1, w2, w8 C0a/C0b, w9, w10) — code against committed artifacts; no new measurement. w4 needs the decoy field designed (statute §4 names no field; a Part II amendment).
5. **Rung-separation-geometry corrected rerun** — the last buggy-kernel-only note (`artifact-status.json`); also supplies w2's mechanism figure on the corrected kernel.
6. **M1-scale rerun and characterization-scale ε grid** (threads 1/5) — lifts D9's ε = 1 from provisional, re-prices D4, and tests the (16, ε = 1) measure-(b) collapse at larger horizon.
7. **Deliverable 3 shuffled gates on C0a/C0c**; deliverable 1's machine-checkable artifact; 4.7 D7 check (non-gating) — when the report is written.
8. **Naming bridge** (v0.2.6 §2) — not an M1 exit item, but gates every corpus-facing ceiling claim in paper 1.

## Open theory threads (exploratory; none gating)

- Derive the five T = 2 shuffled-posterior masses in the closed form C = 7/16 h(1/21) + 1/8 h(1/6) + 5/24 h(1/5) + 3/16 h(4/9) + 1/24 h(1/2) = 0.5799834166232181 from the kernel rather than the enumerator (`d8-attribution-c1-truthsayer-review-2026-08-29.md`).
- Why C1 suppresses the C0b lineage effect (informative-and-collapsed at every law) and whether C1 shows the same discipline-dependent frontier (D10 v0.1.1 item 4).
- The (16, ε = 1) measure-(b) pack rise (all rungs L\* = 12) — mechanism unassigned; ε = ½ horizon-stable.
- Q4 gap exactly 0 at full observability for every rung and endpoint at (12,12,2): the irreducible term is the whole forecast entropy there — consistent with full-context injectivity; a P-horizon separation (w11) must therefore live at L < T_ep.

## Provenance

Every status above was re-derived from the cited file in this session: note
headers and erratum blocks read in full for `d10-lineage-verdict`,
`d1-falsifier-verdict`, `held-out-confirmation`, `audit-adjudication`,
`corrected-kernel-rerun`, `sweep-rerun-comparison`, `d8-shuffled-channel-note`,
the three D8 attribution notes and the v3 map; Part II v0.2.6 header, §1, §2,
§6, §9 read; `artifact-status.json` read; test names read from the files;
the Q4 corrected value read from the JSON; `Record`'s fields and the
TIME_CLASS docstrings read from `records.py`/`window.py`; the shuffled gate's
parameter list read from the test. Figures quoted are copied from those
sources, not from memory. Not re-run: any measurement.

---

### Addendum (2026-09-01 08:49 PDT, same instance, same day)

Blocking item 1 discharged: D1 Part B formal verdict appended to
`d1-falsifier-verdict-v0.1.md` from the committed producer
`scripts/d1_partb_collapse_horizons.py` — L\* = 2 / 8 / 10 (r3→r4 / r2→r3 /
r1→r2), both ε, corrected kernel; all statutory gaps exactly 0.0 at L ≥ 12
(confirming the witness-11 candidate region on the corrected artifact, not the
buggy-kernel note text the table above cited). Item 4.4 reads Part A DONE,
Part B DONE, Part C decided; the blocking list now starts at witness 11.


### Addendum (2026-09-03 09:42 PDT, instance following the v4 author)

**Witness 11 searched — blocking item 2 discharged; item (d) of the Part C
evidence set reads EXISTS (exact corner) / NOT SATISFIED (thresholded).**
Note `w11-predictive-rung-search-v0.1.md`, producer
`scripts/w11_predictive_rung_search.py`, raws
`w11-predictive-rung-search-14-{2..14}-2-2026-09-03.json`, pins
`tests/test_w11_witness.py` (12 tests).

- **Candidate-region correction.** "Exact Q1–Q5 equality at (14,12,2)" is a
  partition identity, not a query-class blind spot: `n_windows` is identical
  across all four rungs at L = 12 and 14 (239799 / 394824, both ε) in the
  committed ceilings artifacts, and r4 refines r1, so every rung holds the same
  belief on every window there. No τ ∈ 𝒯 — no functional of any kind — can
  separate rungs where no window splits. Executed: `n_split = 0` at L = 12, 14.
- **Where it was searched.** Per-window splits at L ∈ {2, …, 10}, all three
  pairs, both ε: a split is a candidate iff every Q1/Q2/Q3/Q5 pushforward and
  the statutory Q4 (W = 4) forecast are exactly unchanged on every piece.
  Twelve candidates exist in the whole family, all at L = 2, r3 → r4, on
  truncated two-record windows; none at L ≥ 4; r1→r2 and r2→r3 never produce
  one (OBJECT/RELATED always move Q1/Q5 when they split a window).
- **Result.** ε = 1: all eight candidates belief-inert (pieces equal the
  parent) — no witness possible. ε = ½: four candidates, each a two-state
  support differing only in the cursor κ. Primary horizon, exact corner:
  WITNESS — next-2 EVENT_KINDs moves by TV = 91258/11287135 ≈ 0.0081 on the
  [IO_COMPLETE(0), IO_COMPLETE(3)] window (and mirror), law mass 4.6 × 10⁻⁷,
  every Q1–Q5 unchanged. At the borrowed Δ_τ = 0.01: not satisfied (max
  primary TV 0.0081). Secondary horizon (W = 8): ttw8 clears Δ_τ (0.0140) on
  the (2,3) window but Q4@8 moves by 0.0125 in the same piece — no candidate
  leaves Q4@8 unchanged, so no strict secondary witness at any threshold.
- **Mechanism.** The lineage rung's predictive residue in these windows is κ
  (v0.2.6 Clause 1): request ids → issue order → dispatch history → cursor;
  outside every fact query, inside the kernel's future at ε < 1, constant at
  ε = 1.
- **Consequence for the PI's decision.** The search is done; the falsifier
  the v4 list named ("an empty result") did not fire; the reading under which
  item (d) counts as ✔ or ✘ is the PI's — the statute froze no threshold or
  horizon rule for w11 and the note declines to freeze one retroactively.
  Part II amendment PROPOSED (not enacted): name w11's reading, and say
  whether Q4's horizon travels with τ's. Blocking order now starts at item 3
  (TIME_CLASS). Witness table row 11: **SEARCHED — EXISTS (exact, primary) /
  NOT SATISFIED (Δ_τ, any consistent horizon)**; executable.

> **Pointer (2026-09-03 10:40 PDT):** the addendum above says "the reading under which item (d) counts as ✔ or ✘ is the PI's." Withdrawn — that was a post-hoc menu, caught by the PI. Under the statute as written witness 11 is **SATISFIED (existence, exact, primary horizon)**; see `w11-predictive-rung-search-v0.1.md` §10. Item (d) reads ✔; the Part C evidence set is complete; witness-table row 11: SATISFIED (existence), sub-Δ_τ reported as sensitivity. A thresholded claim, if wanted, comes only from `w11-heldout-prereg-v0.1.md` (reading frozen before the held-out search). Nothing above is rewritten.
