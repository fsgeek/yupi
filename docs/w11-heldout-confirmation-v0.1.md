# Witness 11 — held-out confirmatory search: results and scorecard

**v0.1 — 2026-09-03.** Pre-registration `w11-heldout-prereg-v0.1.md` (commit
e5a8af4, stamped a4d586d at 10:40 PDT; runs launched 10:43, finished 11:22).
Producer `scripts/w11_predictive_rung_search.py` as committed with the
pre-registration; raws `w11-predictive-rung-search-{16-L-2, 14-L-2, 14-L-1}-heldout-2026-09-03.json`
(21 files); pins in `tests/test_w11_witness.py`. Corrected kernel, canonical
track. The reading, laws and predictions are the pre-registration's; nothing
was added or dropped after the stamp. Every number is copied from the raws
in-session.

## 1. Verdict under the frozen reading

**Thresholded witness 11: SATISFIED on a held-out law.** F2, (14, 2, 2),
ε = ¼, r3 → r4, the r3 window [IO_COMPLETE(0), IO_COMPLETE(3)] and its
mirror: every Q1–Q5 posterior (statutory Q4 at W = 4) exactly unchanged
across the r4 refinement; next-2 EVENT_KINDs moves by
TV = 891594459/79619545438 ≈ **0.01120 ≥ Δ_τ = 1/100** on the (0,1) piece.
Law mass of the two witnessing windows 2 × 5978341/998603250204672 ≈
1.2 × 10⁻⁸. Support two states differing only in the cursor κ. The
pre-registration said a single witness at threshold falsifies P3 and makes
the thresholded statement SATISFIED; that is the outcome, 12 % over the
threshold, on a law and an ε the exploratory search never touched.

The existence statement from the exploratory note (§10 there) is unchanged
and is now also confirmed on fresh ε: exact-corner witnesses exist at ε = ¼
and ε = ⅝ (F2, L = 2, kinds2 TV 0.0112 and 0.00517).

## 2. Scorecard

| prediction | result | detail |
|---|---|---|
| **P1** no split at U ≤ 2 | **PASS** | `n_split = 0` at F1 L = 14, F2 L = 12 and 14, F3′ L = 13, every pair, every ε (partition identity holds at T_ep = 16 and at B = 1) |
| **P2** exact-corner witness at every ε < 1 family's shortest L | **FAIL** (2 of 4 conjuncts) | F2 ε = ¼ ✔, F2 ε = ⅝ ✔; F1 ε = ½ L = 2 ✘ — **no candidate at all** (see §3); F3′ ε = ½ ✘ — candidates at L = 3 exist (24) but all inert |
| **P3** no witness at threshold anywhere | **FAIL** | F2 ε = ¼ L = 2 r3→r4: 2 windows, kinds2 TV 0.01120 ≥ 0.01 — the thresholded statement is SATISFIED |
| **P4** ε = 1 candidates all inert | **PASS** | F1 L = 4: 216/216 inert; F3′ L = 3: 30/30 inert; no other ε = 1 candidates |
| **P5** non-inert supports differ only in κ | **PASS** | all 8 non-inert candidates (F2, both ε) have `support_differs_in = [rr_cursor]` |
| **P6** candidates only at each family's shortest L | **PASS F2; FAIL F1, F3′** | F1 has 216 (ε = 1) / 202 (ε = ½) candidates at L = 4 and none at L = 2; F3′ has 30 / 24 at L = 3 and none at L = 1 — every one inert, so no *witness* exists off the shortest L, but P6 was written on candidates and is scored as written |

Three PASS, three FAIL. The failures are the informative part.

## 3. Why P2 failed at T_ep = 16 (checked, not guessed)

At (16, 2, 2), ε = ½, the same two-record IO_COMPLETE windows are still
split by r4 into the two request-id assignments — but the r3 window now
mixes endpoints T = 14 and T = 16, its support is six states differing in
`lock_owner` and `pc` as well as κ, and the request ids inform **Q1[L0]**
(the owner of lock 0) on both pieces. The window is not a candidate because
clause (a) of D2 is exercised on it: the lineage field reaches a fact query.
The κ-only witness at T_ep = 14 lives in the U = 12 corner where the two
completions are the last records of a full episode; two more ticks of
episode put lock activity behind them and the fact queries wake up. So the
mechanism is real and narrow: it needs the endpoint mixture to leave κ as
the *only* open coordinate.

At B = 1 (F3′) the shortest windows are single records (L = 1: no
candidate) and the three-record candidates at L = 3 are all inert. The
cursor effect does not appear at B = 1 in this family.

## 4. Per-law table (r3 → r4 only; r1→r2 and r2→r3 have zero candidates at every held-out law, as in the exploratory family)

| family | L | U | ε | split | cand | inert | witness (exact / Δ_τ) |
|---|---|---|---|---|---|---|---|
| F1 (16,·,2) | 2 | 14 | 1, ½ | 71 | 0 | — | — |
| F1 | 4 | 12 | 1 / ½ | 607 | 216 / 202 | all | none |
| F1 | 6–12 | 10–4 | 1, ½ | 694, 576, 740, 734 | 0 | — | — |
| F1 | 14 | 2 | 1, ½ | 0 | 0 | — | — |
| F2 (14,·,2) | 2 | 12 | ¼ | 47 | 4 | 0 | **2 / 2** (kinds2 0.01120) |
| F2 | 2 | 12 | ⅝ | 47 | 4 | 0 | 2 / 0 (kinds2 0.00517) |
| F2 | 4–10 | 10–4 | ¼, ⅝ | 121, 90, 106, 110 | 0 | — | — |
| F2 | 12, 14 | 2, 0 | ¼, ⅝ | 0 | 0 | — | — |
| F3′ (14,·,1) | 1 | 13 | 1, ½ | 6 | 0 | — | — |
| F3′ | 3 | 11 | 1 / ½ | 161 | 30 / 24 | all | none |
| F3′ | 5–11 | 9–3 | 1, ½ | 272, 178, 197, 220 | 0 | — | — |
| F3′ | 13 | 1 | 1, ½ | 0 | 0 | — | — |

Split counts are ε-independent within a family (partition is a property of
the trace alphabet). Secondary-horizon figures are in the raws and adjudicate
nothing: at F2 ε = ¼ the (2,3) window has ttw8 0.01364 with Q4@8 0.01324 in
the same piece, the same entanglement the exploratory note recorded.

## 5. Cost

F1 (16, L, 2): 2.5 → 7.4 min per L, peak RSS 4.5 → 15.8 GB (L = 14); F2:
1.2–1.7 min, ≤ 3.4 GB; F3′: 1.0–2.1 min, ≤ 3.0 GB. Single core each, three
families in parallel.

## 6. What is now on the record for witness 11

- Existence (exact, primary horizon): SATISFIED in C1 at statutory ε
  (exploratory, v0.1.1) and at held-out ε = ¼, ⅝ (this note).
- Thresholded at Δ_τ = 1/100 (reading frozen before the run): SATISFIED at
  held-out ε = ¼; not at ε = ½, ⅝, 1 or at T_ep = 16 or B = 1.
- Mechanism: κ, confirmed on every non-inert candidate in both rounds (P5);
  confined to the U = T_ep − 2 corner of two-record windows at B = 2, and
  displaced by clause (a) once the endpoint mixture carries lock activity
  (§3).
- Prevalence: 10⁻⁸ to 10⁻⁶ of law mass wherever it exists.

D2 clause (b) is exercised for the lineage rung in this world, exactly and
at the frozen threshold, and it is a corner. Both halves of that sentence
are the finding. The Part C evidence set is unchanged by this note (item (d)
was ✔ after v0.1.1); the intervention selection remains the PI's.

## 7. Not claimed

Anything at ε other than the five searched; anything about worlds other
than C1; that P6's scoring rule was the right one (it counted candidates
where the prediction's intent was witnesses — recorded, not re-scored).
