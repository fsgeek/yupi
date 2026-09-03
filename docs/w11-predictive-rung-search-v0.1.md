# Witness 11 — predictive rung discrimination: search, verdict, mechanism

**v0.1 — 2026-09-03.** Instance following the one that wrote map v4 and the
D1 Part B adjudication. Producer `scripts/w11_predictive_rung_search.py`;
raw artifacts `docs/w11-predictive-rung-search-14-{2,4,6,8,10,12,14}-2-2026-09-03.json`;
executable pins `tests/test_w11_witness.py`. Corrected kernel (fix d69fa87),
canonical-naming track (Part II v0.2.6 Clause 2′), both statutory ε, (14, L, 2).
Every number below is copied from those artifacts in-session. No other
measurement was rerun.

## 1. The statute and how it was read

Part II §9 item 11: *"an adjacent interface pair distinguished by a P-horizon
test while all Q1–Q5 posteriors are unchanged — the D2 disjunctive clause (b)
exercised, proving the query suite alone does not define interface value."*
Part I D2 (v0.2.3): a rung must change *either* (a) a Q1–Q5 posterior *or* (b)
a preregistered finite-horizon predictive distribution; clause (b) exists so
"a field can leave every fact posterior unchanged while altering
future-observation distributions."

The statute is about posteriors, so it was read **per window class**, not on
the law-mass mean: for an adjacent pair (r, r′), an r-window w whose
r′-refinement splits it into pieces w₁…w_k is a **candidate** iff every
statutory fact query's pushforward is exactly unchanged on every piece —
Q1, Q2, Q3 (ids), Q5 (per pair), and statutory Q4 (the wake forecast) — and a
**witness** iff some τ ∈ 𝒯 = {next-2 EVENT_KINDs; time-to-next-wake ≤ W;
LINEAGE of the next IO_COMPLETE ≤ W} (frozen v0.2.4, m = 2, W = 4 primary /
8 secondary) differs on a piece.

The statute names no separation threshold for this witness, and Q4 carries
the same horizon parameter W as two of the three τ. Three readings are
therefore reported rather than one chosen:

| reading | "unchanged" set | τ tested | thresholds |
|---|---|---|---|
| **primary** (W = 4) | Q1, Q2, Q3, Q5, Q4@4 | kinds2, ttw4, lin4 | TV > 0 (exact corner) and TV ≥ Δ_τ = 0.01 (v0.2.5, borrowed — frozen for divergent histories, not for this witness) |
| **secondary, strict** (W = 8) | the above **and** Q4@8 | ttw8, lin8 | same |
| **secondary, loose** | primary set only | ttw8, lin8 | same — the asymmetric reading (fact forecast held at W = 4 while the predictive test runs to W = 8); reported, not claimed |

## 2. The candidate region was empty a priori

Map v4 placed the search at (14, 12, 2) because every law-mass-mean Q1–Q5 gap
is exactly 0.0 there (D1 Part B). That exactness has a mechanism the mean
hides: in `c1-query-ceilings-14-{L}-2-corrected-2026-08-20.json` the number of
distinct projected windows per rung is

| L | r1 | r2 | r3 | r4 |
|---|---|---|---|---|
| 2 | 221 | 248 | 330 | 377 |
| 4 | 3489 | 3931 | 4488 | 4609 |
| 6 | 19887 | 21411 | 22428 | 22518 |
| 8 | 65709 | 68122 | 68990 | 69096 |
| 10 | 146926 | 148977 | 149073 | 149183 |
| **12** | **239799** | **239799** | **239799** | **239799** |
| **14** | **394824** | **394824** | **394824** | **394824** |

(identical at both ε). The r4 partition of windows refines the r1 partition
(each rung adds fields; `interfaces.project`), so equal counts mean equal
partitions: at L = 12 no r1 window is split by any higher rung, every rung
holds the *same* belief on every window, and every functional of the belief —
Q1–Q5, P-next, every τ in 𝒯, anything else — is rung-invariant bit for bit.
That is why the Part B gaps are exactly zero and the L = 12 residual H(S)
(0.00064 bits at ε = 1, from two dropped records) is rung-invariant to every
digit, not "to five decimals". No P-horizon test can separate rungs where no
window splits. The claim is executed, not argued: the producer reports
`n_split = 0` for every pair at L = 12 and L = 14, and
`test_candidate_region_has_no_split_by_counting` pins it from the artifacts.

Witness 11 can only live where windows split — L ≤ 10 at T_ep = 14 — and there
the statute's "unchanged" must be checked per split, since the mean gaps are
nonzero.

## 3. Method

Path aggregation by (RESET observed, projected window) at all four rungs in
one pass (as `c1_query_ceilings.py`), the r′ → r parent map recorded per path.
Per-rung window counts asserted equal to the committed ceilings artifact's
`n_windows` for the same law (gate passed at every L, both ε). For every split
parent: exact fact signature on each piece (Fractions); per-state τ and Q4
functionals memoised once per ε (`yupi.forecast.q4_forward`,
`yupi.predict.{next_kinds,time_to_wake,next_complete_lineage}`); TV between
each piece's mixture and the parent's. Every candidate window is dumped in
full: pieces, support, the state fields in which the support states differ,
whether the pieces' beliefs equal the parent's ("inert"), every TV as an exact
rational. Wall clock 1.1–1.7 min per L on one core; peak RSS 1.1 GB (L = 2) rising to 4.2 GB (L = 14).

## 4. Results, (14, L, 2), both ε

`split` = r-windows split by r′; `cand` = splits with every fact query and
Q4@4 exactly unchanged on every piece. Masses are law mass.

| L | pair | split (ε=1 / ½) | mass split (ε=1 / ½) | cand (ε=1 / ½) |
|---|---|---|---|---|
| 2 | r1→r2 | 27 / 27 | 0.1700 / 0.1164 | 0 / 0 |
| 2 | r2→r3 | 63 / 63 | 0.2476 / 0.2462 | 0 / 0 |
| 2 | r3→r4 | 47 / 47 | 0.1580 / 0.1558 | **8 / 4** |
| 4 | r1→r2 | 442 / 442 | 0.1627 / 0.1205 | 0 / 0 |
| 4 | r2→r3 | 472 / 472 | 0.1424 / 0.1265 | 0 / 0 |
| 4 | r3→r4 | 121 / 121 | 0.0762 / 0.0523 | 0 / 0 |
| 6 | r1→r2 | 1524 / 1524 | 0.1026 / 0.0809 | 0 / 0 |
| 6 | r2→r3 | 929 / 929 | 0.0492 / 0.0368 | 0 / 0 |
| 6 | r3→r4 | 90 / 90 | 0.0013 / 0.0001 | 0 / 0 |
| 8 | r1→r2 | 2413 / 2413 | 0.0448 / 0.0360 | 0 / 0 |
| 8 | r2→r3 | 868 / 868 | 0.0118 / 0.0128 | 0 / 0 |
| 8 | r3→r4 | 106 / 106 | 0.0010 / 0.0001 | 0 / 0 |
| 10 | r1→r2 | 2051 / 2051 | 0.0104 / 0.0079 | 0 / 0 |
| 10 | r2→r3 | 96 / 96 | 0.0003 / < 0.0001 | 0 / 0 |
| 10 | r3→r4 | 110 / 110 | 0.0006 / < 0.0001 | 0 / 0 |
| 12, 14 | all | 0 | 0 | 0 |

Split counts are ε-independent (the partition is a property of the trace
alphabet, not the law's weights); masses are not. **Every candidate in the
whole family is at L = 2, r3 → r4, on truncated (no-RESET) two-record
windows.** For r1→r2 and r2→r3 at every L, every split moves some fact
query — OBJECT and RELATED feed Q1/Q5 directly — so clause (a) is exercised
for those pairs wherever they separate at all, and clause (b) is never
reached.

## 5. The twelve candidates, in full (L = 2, r3 → r4)

**ε = 1 — eight candidates, all inert.** Windows [IO_COMPLETE(i), DISPATCH(3)]
and [DISPATCH(3), IO_COMPLETE(i)] for i ∈ {0, 2} (support 2, the states
differing in `running`/`status`) and [IO_COMPLETE(i), IO_COMPLETE(3)] in both
orders for i ∈ {0, 2} (support 1). In every one the request id revealed at r4
is *independent* of the residual state ambiguity: each piece's belief equals
the parent's exactly, so every functional — fact or predictive, any horizon —
is unchanged. Total candidate mass 1.57 × 10⁻⁴. The lineage rung reveals
something here (which id the completion carried) that is simply not about the
state.

**ε = ½ — four candidates, none inert, every support a two-state set
differing ONLY in the cursor κ (`rr_cursor` ∈ {2, 3} in the (0,3) windows,
{1, 2} in the (2,3) windows); pc, status, running, lock owners, wait queues
and device queues identical.** Two mirror pairs:

| window (r3) | mass | piece (r4 ids) | kinds2 | ttw4 / lin4 | ttw8 | Q4@8 |
|---|---|---|---|---|---|---|
| [IO_COMPLETE(0), IO_COMPLETE(3)] and mirror | 37007/162533081088 ≈ 2.28e-7 each | (0,1) | **91258/11287135 ≈ 0.00809** | 0 / 0 | 3330917/69348157440 ≈ 4.8e-5 | 4973561/69348157440 ≈ 7.2e-5 |
| | | (1,0) | 410661/633966917 ≈ 0.00065 | 0 / 0 | ≈ 3.8e-6 | ≈ 5.7e-6 |
| [IO_COMPLETE(2), IO_COMPLETE(3)] and mirror | 7913/81266540544 ≈ 9.74e-8 each | (0,1) | 0 | 0 / 0 | **274301873/19544223744 ≈ 0.01403** | **3404179/271447552 ≈ 0.01254** |
| | | (1,0) | 0 | 0 / 0 | ≈ 0.00181 | ≈ 0.00162 |

(TV of the piece's mixture from the parent's; Q4@4 is exactly unchanged on all
four by construction of the candidate set; lin8 ≤ 1.6 × 10⁻⁶ everywhere.) All
mass sits at endpoint T = 14, U = 12: the observer sees the last two records
of a full episode. The two request ids say which of the two completing
threads issued first; issue order is entangled with dispatch order, and at
ε < 1 dispatch order is what writes κ. The κ posterior in the (2,3) window
moves from 17585/23739 on κ = 2 (parent) to 47/67 and 31363/42051 on the two
pieces.

## 6. Verdict

- **Primary horizon, exact corner (TV > 0): WITNESS EXISTS.** At ε = ½,
  r3 → r4, (14, 2, 2), the [IO_COMPLETE(0), IO_COMPLETE(3)] window and its
  mirror: every Q1–Q5 posterior (Q4 at W = 4) exactly unchanged on both
  pieces; next-2 EVENT_KINDs moves by TV = 91258/11287135 ≈ 0.0081 on the
  (0,1) piece. Law mass of the witnessing windows 4.55 × 10⁻⁷. D2 clause (b)
  is exercised for the lineage rung in this world, at ε < 1, exactly.
- **Primary horizon at Δ_τ = 0.01: NOT SATISFIED.** Max primary TV over all
  candidates is 0.0081 (19 % under the borrowed threshold).
- **Secondary horizon, strict: NOT SATISFIED at either threshold.** No
  candidate leaves Q4@8 unchanged; in the window where ttw8 clears Δ_τ
  (0.0140), Q4@8 moves by 0.0125 in the same piece. The predictive test and
  the fact forecast see the same κ shift through the same wake.
- **Secondary horizon, loose: two windows clear Δ_τ** (the (2,3) pair,
  mass 1.95 × 10⁻⁷). Reported so the asymmetric reading is visible; not
  claimed, because holding Q4 at W = 4 while running τ to W = 8 is not what
  "all Q1–Q5 unchanged" says.
- **ε = 1: NO WITNESS possible in this family** — every candidate is inert,
  and κ ≡ 0 at ε = 1 (Part II v0.2.6 Clause 1), which closes the only
  mechanism found.
- **L ≥ 4: no candidates**; L ≥ 12: no splits.

So: witness 11 holds as an existence statement in the exact corner on the
primary horizon, on ~5 × 10⁻⁷ of law mass, for the lineage rung only, at
ε = ½ only, at the shortest context only. Under any thresholded reading at a
consistent horizon it fails. The map-v4 line "an empty result is a falsifier
for the D2 disjunctive clause (b) at this world" is therefore **not
triggered** (the result is not empty), and the clause is also not exercised
in any quantity the frozen thresholds would count.

## 7. Mechanism, stated once

The predictive information the lineage rung carries in these windows is the
round-robin cursor κ — the coordinate v0.2.6 Clause 1 added to the state
tuple because the prose was non-Markov without it. κ is outside every fact
query by definition (Q1–Q5 are predicates on own/st/dq/wq), inside the
kernel's future through dispatch order whenever ε < 1, and constant at ε = 1.
The lineage rung reaches κ only indirectly (request ids → issue order →
dispatch history), only when two completions are all the observer sees, and
only weakly (the κ posterior shifts by a few percent). This is a mechanism
for one world at one law; nothing here says κ is the *only* seat of clause
(b) at larger horizons or other worlds — pc, the running set and wait-queue
order are the other coordinates Q1–Q5 cannot see, and none of them produced a
candidate at L ≥ 4 in C1.

## 8. Consequences

- **Evidence map v4, item (d):** the witness-11 search is done. Its result is
  neither the ✔ the map's Part C evidence set was waiting for nor the falsifier
  it named: EXISTS (exact corner) / NOT SATISFIED (thresholded). The PI's
  intervention-selection decision is unblocked by the search having been run;
  the reading it should be made under is the PI's call, because the statute
  froze no threshold or horizon rule for w11 and this note declines to freeze
  one retroactively. A Part II amendment naming the reading (and whether Q4's
  horizon travels with τ's) is proposed, not enacted.
- **Map v4 candidate-region wording** ("exact Q1–Q5 equality at (14,12,2)")
  is corrected here: that region is empty by partition identity; a pointer is
  appended to the map where the reader meets the region first. Nothing in
  the map is rewritten.
- **Interpretation of the lineage rung in C1:** consistent with "informative
  and collapsed" (D10 v0.1.1, D1 Part B): its residual information at short
  truncated context is predictive, seated in κ, sub-δ on every measure the
  statute counts, and gone by L = 4.
- **Not claimed:** any random-naming ceiling (canonical track, §2 bridge
  outstanding); anything about worlds other than C1 or horizons other than
  T_ep = 14; that Δ_τ = 0.01 is the right threshold for this witness; that
  "primary horizon" is the right reading — only that under each reading the
  numbers are as stated.

## 9. Provenance

Producer committed with this note; raw JSON per L with every candidate's
exact rationals; `tests/test_w11_witness.py` recomputes §5's two ε = ½
windows and the ε = 1 inertness from the enumerator and `yupi.predict`
without touching the producer (≈ 40 s), and pins §2 from the ceilings
artifacts. Two-path filter validation was not rerun here: every window in
this family passed it when the ceilings artifacts were produced (2026-08-20),
and the window sets are asserted identical by count.
