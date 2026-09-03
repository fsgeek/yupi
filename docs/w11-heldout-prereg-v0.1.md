# Witness 11 — held-out confirmatory search: pre-registration

**v0.1 — 2026-09-03, written and stamped BEFORE any run on the laws named
below.** Instance following the map-v4 author; same day as
`w11-predictive-rung-search-v0.1.md` (exploratory, (14, ·, 2), statutory ε)
and `partition-identity-note-v0.1.md`. Purpose: the exploratory search
settled witness 11 as an existence statement under the statute as written.
A *thresholded* statement about the same witness cannot be made from that
search without choosing the threshold after the result; it can be made by
freezing the reading here and searching laws the exploratory run never
touched. This document is that freeze. It changes no statute; it binds this
run.

## 1. Reading, frozen

For an adjacent pair (r, r′) under a window law, an r-window w whose
r′-refinement splits it into pieces w₁…w_k is

- a **candidate** iff, on every piece, the pushforward of every statutory
  fact query — Q1 (per lock), Q2 (per thread), Q3 (ids, per device), Q5 (per
  ordered pair) — and the statutory Q4 forecast at its primary horizon
  **W = 4** are **exactly** equal to the parent's (rational equality);
- a **witness at the exact corner** iff some primary-horizon τ ∈ 𝒯 —
  next-2 EVENT_KINDs (m = 2), time-to-next-wake ≤ 4, LINEAGE of the next
  IO_COMPLETE ≤ 4 — differs from the parent's on some piece (TV > 0);
- a **witness at threshold** iff that TV is **≥ Δ_τ = 1/100** (the v0.2.5
  divergence threshold, adopted here for this witness by this freeze).

Q4 at W = 8 and the secondary τ (ttw8, lin8) are computed and co-reported;
they adjudicate nothing in this run. The reading is the same one the
exploratory producer used; the only thing new here is that it is frozen
before the data.

## 2. Laws, fixed

All held-out families already enacted for Tier 1 (`held-out-laws` stamp
`7564482`), for which ceilings artifacts exist and the window-count gate can
be asserted:

| family | law | ε | L searched |
|---|---|---|---|
| F1 | (16, L, 2) | 1, ½ | 2, 4, 6, 8, 10, 12, 14 |
| F2 | (14, L, 2) | ¼, ⅝ (seeded draw, `held-out-selection-e-draw-2026-08-21.json`) | 2, 4, 6, 8, 10, 12, 14 |
| F3′ | (14, L, 1) | 1, ½ | 1, 3, 5, 7, 9, 11, 13 |

Producer: `scripts/w11_predictive_rung_search.py` as committed with this
document (ε from `YUPI_EPS`; window-count gate against the held-out ceilings
artifact for the same law). Corrected kernel, canonical-naming track. No
other law, ε, horizon or τ will be added after this stamp; if the producer
must change, the change is committed and the affected laws rerun in full.

## 3. Predictions, written before the run

Derived from the exploratory result and the two notes cited above; each is
scored PASS / FAIL / NO_CHECK, conjunctively where stated.

- **P1 (structural).** No split at any law with U = T_ep − L ≤ 2: F1 L = 14;
  F2 L = 12, 14; F3′ L = 13. `n_split = 0`, every pair, every ε.
  *(Partition-identity rule.)*
- **P2 (existence, exact corner).** At every ε < 1 law family, at least one
  exact-corner witness (primary τ, TV > 0) exists at the family's shortest
  L, r3 → r4. Conjunctive over F1 ε = ½ (L = 2), F2 ε = ¼ and ⅝ (L = 2),
  F3′ ε = ½ (L = 1 or 3; scored on the union). *(κ mechanism at ε < 1.)*
- **P3 (the thresholded claim).** **No witness at threshold** (primary-τ
  TV ≥ 1/100 on a candidate) at any law, ε or pair in §2. *(Exploratory max
  0.0081 at the deepest truncation; the κ shift is a few percent.)* A single
  witness at threshold falsifies P3 and makes the thresholded statement
  SATISFIED on held-out laws; P3 PASS makes it NOT SATISFIED. Either outcome
  is the confirmatory result; neither is revisited.
- **P4 (ε = 1 inertness).** Every candidate at ε = 1 (F1, F3′) is
  belief-inert: each piece's belief equals the parent's.
- **P5 (mechanism).** Every non-inert candidate's support differs only in the
  cursor κ (`rr_cursor`), all other state fields identical.
- **P6 (locality).** No candidate at any L with U ≥ 3 other than the shortest
  L of its family, at any ε. *(Exploratory: none at L ≥ 4.)* Scored per
  family.

## 4. Reporting

One note, `w11-heldout-confirmation-v0.1.md`, with every prediction scored,
every candidate dumped (the producer does this), and the per-law table in
the exploratory note's §4 format. Raw artifacts
`w11-predictive-rung-search-{16-L-2,14-L-2,14-L-1}-heldout-2026-09-0X.json`.
Executable pins added to `tests/test_w11_witness.py` for whatever P2/P3
produce. Wall-clock and peak RSS per law recorded.

## 5. Not decided here

Whether Δ_τ = 1/100 is the right threshold for witness-11-type searches in
general — that is the prospective Part II question raised in the
exploratory note's §10, and this run tests one value, not the question.
