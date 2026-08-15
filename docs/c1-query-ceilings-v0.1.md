# C1 Query Ceilings — the declared targets under windows (v0.1)

**v0.2 — 2026-08-15 (same day, truthsayer round).** Codex's audit
verified the measurements (state and query entropies reproduced by direct
path aggregation; the second-issue-at-t=11 enumeration; the strong-zero
Q3-id surplus at (12,2,2)/(14,4,2) and its appearance at (14,2,2) — 25
distinguishing windows at r1–r3, 11 at r4; the full-context control; the
suite) and refuted five things this note said ABOUT them. Every
correction below was recomputed by an independent path before adoption;
the v0.1 text is preserved beneath the rule, uncorrected, as the trace.

1. **The headline was not entitled to "every declared target."** Part II
   §5 (which I had not read — I worked from Part I's list) defines Q3 as
   the ordered list of (thread, request_id), Q4 as a *predictive* query
   (the thread directly woken by the first wake-causing transition in
   (t, t+W], completions included — a forward sum with an irreducible
   term even under exact state knowledge), and Q5 as a predicate over an
   ordered pair. v0.1 measured **Q1, Q2, statutory Q3 (under the label
   "Q3ids"), and three proxies**: thread-only in-flight ("Q3"), FIFO-head
   release wake ("Q4"), and the joint set of true Q5 pairs ("Q5"). The
   claim "every query has exactly zero full-context entropy" is false as
   written for statutory Q4 and is now: *every state-predicate query and
   proxy has exactly zero.* **Statutory Q4 is unimplemented.**
   `queries.py` is relabeled — Q3 (statutory, ids), Q3thr, Q4proxy,
   Q5[Tb,Tr] (statutory, per ordered pair, ADDED), Q5joint — and the
   raw JSONs of commit 0742d1d carry the v0.1 labels
   (Q3→Q3thr, Q3ids→Q3, Q4→Q4proxy, Q5→Q5joint). The (12,2,2) run is
   re-executed under the new labels with per-pair Q5 (values unchanged
   for the relabeled queries; the per-pair rows are new — see the v0.2
   results block at the end).
2. **The "~100:1" ratio was wrong and is withdrawn** — recomputed: at
   (12,2,2), ε=1, support gap 0.3166 vs entropy gap 0.001285 bits
   (quotient 246); ε=½, 0.3207 vs 0.0000429 (quotient 7,473). And a
   support count over bits is not a dimensionless quantity. The finding
   is stated as the two measured numbers: a visible mean-support
   separation corresponds to very little probability-weighted
   information, especially at ε=½.
3. **The P2 explanation was too tidy.** New script
   `scripts/c1_query_gap_decomposition.py` (splits attributed to the
   signature of differing kind.field pairs; asserted to sum to each
   query's table gap) reproduces the auditor's attribution exactly:
   Q4proxy[L0]'s r1→r2 gain is **78.0% ACQUIRE.obj** (not BLOCK.obj as
   I argued), its r2→r3 gain **94.9% BLOCK.related** although the owner
   does not appear in the proxy's answer; Q4proxy[L1]'s r1→r2 gain is
   100% BLOCK.obj; Q1[L0]/Q5joint owner-channel account holds (80% /
   99.5% BLOCK.related). Fields inform a query by reconstructing the
   trajectory, not only by disclosing its answer. Finding 3's field-to-
   query mapping is now a hypothesis *partially supported* by
   decomposition. Raw: `c1-query-gap-decomposition-12-2-2-raw-2026-08-15.json`.
4. **"Geometry over content" survives, narrower.** v0.1's 1.7-bit figure
   compared (12,2,2) with (14,4,2) — two horizons. Same-horizon pair,
   T_ep=14, B=2, r4: L=2→4 lowers H(S_T) by **1.9201** bits (ε=1) /
   1.5895 (ε=½); the whole content ladder at L=4 is worth 0.2492 /
   0.1209. A claim about C1 at these laws, not about window regimes or
   other worlds.
5. **Two overstatements in the companion design note** are narrowed
   there (v0.3): statutory Q3 is not thread-only, and "random ids ⇒
   r4 ≡ r3" holds only after request-id identity is quotiented out of
   both the state target and the query suite. The I5 argument itself
   was found sound; the day-six erratum is now written (that note's
   v0.4).

Ledger for the round: five corrections, all adopted after independent
recomputation; one new script; one statutory query added; one still
unimplemented and named as such.

---

**v0.1 — 2026-08-15 (day seven).** Drafted by the day-seven instance.
Status: **measured note, first query-level ceilings**; advances
instrument-status open thread 1 (M1-scale separation on the DECLARED
targets, not state support). Code: `src/yupi/queries.py` (world-side
query functions, TDD, `tests/test_queries.py`); script:
`scripts/c1_query_ceilings.py`. Predictions below were written and saved
BEFORE the first run; results are appended after, unedited above the line.

## Why

Every ceiling measured on days five and six is *mean state support* — a
combinatorial proxy that Part I D9 explicitly separates from
probability-weighted uncertainty, and that the M1 exit criteria do not
name. The criteria name Q1–Q5 (Part I) and predictive state. This note
computes, for each query instance, the exact posterior over its answers
under a WindowLaw, per rung, and reports the law-mass-weighted mean
entropy in bits: **the observation-gap ceiling for that query at that
interface.** Two-path: every distinct window's joint (U, S_T) is
recomputed through `window_filter` and must match the path aggregation
Fraction-for-Fraction before any query is pushed forward.

## Query definitions (decisions, recorded in `queries.py` docstring)

Q1[L] owner-or-None · Q2[T] status class · Q3[D] in-flight issuing
threads in queue order (thread-identified per I5) with Q3ids[D] as the
lineage diagnostic · Q4[L] FIFO-head release wake · Q5 the set of
(blocked, running) pairs where blocked waits on a lock owned by running.

## Predictions (pre-stated; law (12,2,2) and (14,4,2), both ε)

- **P1 (invariants, must hold):** for every query, mean entropy is
  non-increasing r1→r2→r3→r4; for every window, H(Q|w) ≤ H(S_T|w).
- **P2:** for Q1, Q4, Q5 the r2→r3 gap (owner channel via BLOCK.related /
  RELEASE.related) is the largest of the three adjacent gaps.
- **P3:** Q2 has an r1→r2 gap > 0 (BLOCK.obj disambiguates lock- vs
  queue-block); its r3→r4 gap is < 10% of its total r1→r4 drop.
- **P4 (the I5 prediction):** if any query moves r3→r4, Q3 does — the
  lineage rung's cargo is allocator state, and the in-flight set is Q3's
  subject. Q3ids − Q3 (the id-only surplus) is smaller at r4 than at r3.
- **P5 (control):** at a full-context law (L ≥ T_ep) every query has
  entropy exactly 0 at every rung — the injectivity theorem.

---

## Results — WindowLaw(12,2,2), both ε (raw: `c1-query-ceilings-12-2-2-raw-2026-08-15.json`)

Two-path: all 971 distinct windows matched Fraction-for-Fraction; P1
invariants held on every window and every rung (asserted in-script).
Wall clock 2m03s. Mean entropy in bits, law-mass weighted; adjacent gaps
r1→r2 | r2→r3 | r3→r4 (total r1→r4):

| ε | quantity | r1 | r4 | gaps | resolved mass r1→r4 |
|---|---|---|---|---|---|
| 1 | H(S_T) | 3.0598 | 2.7799 | 0.1333 \| 0.1452 \| **0.0013** | — |
| 1 | Q1[L0] | 0.6818 | 0.5212 | 0.0173 \| **0.1431** \| 0.0002 | 0.455→0.670 |
| 1 | Q1[L1] | 0.3850 | 0.2515 | **0.1221** \| 0.0115 \| 0.0000 | 0.398→0.554 |
| 1 | Q2[T0..T3] | 0.67/0.63/0.55/0.51 | 0.62/0.60/0.54/0.50 | all r3→r4 ≤ 0.0007 | ~0.50→0.52 |
| 1 | Q3[D0] | 0.2043 | 0.2013 | 0.0008 \| 0.0009 \| **0.0013** | 0.448→0.606 |
| 1 | Q3ids[D0] | 0.2043 | 0.2013 | identical to Q3 to float precision | identical |
| 1 | Q4[L0] | 0.6879 | 0.6043 | **0.0506** \| 0.0331 \| 0.0000 | 0.283→0.403 |
| 1 | Q4[L1] | 0.0203 | 0.0082 | 0.0120 \| 0.0001 \| 0.0000 | 0.919→0.947 |
| 1 | Q5 | 0.6150 | 0.5170 | 0.0203 \| **0.0777** \| 0.0000 | 0.435→0.476 |
| 1/2 | H(S_T) | 2.3040 | 2.1586 | 0.0775 \| 0.0679 \| **0.0000** | — |
| 1/2 | Q1[L0] | 0.5114 | 0.4382 | 0.0054 \| **0.0678** \| 0.0000 | 0.457→0.669 |
| 1/2 | Q1[L1] | 0.2494 | 0.1695 | **0.0746** \| 0.0053 \| 0.0000 | 0.451→0.557 |
| 1/2 | Q4[L0] | 0.6447 | 0.5697 | **0.0468** \| 0.0282 \| 0.0000 | 0.298→0.399 |
| 1/2 | Q5 | 0.5722 | 0.5166 | 0.0130 \| **0.0427** \| 0.0000 | 0.440→0.472 |

(Full per-query rows for both ε in the raw JSON; ε=1/2 rows omitted here
follow the same pattern with every level lower — the third law running.)

### Predictions scored

- **P1 held** (asserted). **P5** control run pending (slow: at L = T_ep
  every path is its own window; the theorem already has a tripwire test).
- **P2 half-refuted.** The r2→r3 owner channel dominates Q1[L0] (the
  contended lock) and Q5 — but NOT Q1[L1] (r1→r2 dominates: which lock is
  ACQUIRED, revealed by obj) and NOT Q4 at either lock (r1→r2 dominates).
  Retrospectively obvious and I got it wrong a priori: Q4 asks who is at
  the head of a wait queue; the *waiter* is the BLOCK's actor (r1) and
  *which* queue is BLOCK.obj (r2); `related` names the owner, which is
  Q1's business, not Q4's. The owner channel informs Q1 and Q5; the
  object channel informs Q4 and the uncontended lock's Q1. Field-level
  cargo, per query — T'aqaq's rule applied to my own prediction.
- **P3 held.** Q2's r1→r2 gap > 0 for every thread; r3→r4 ≤ 0.0007 bits
  (≤ 12% of Q2[T3]'s tiny total, < 2% for the others — the < 10% clause
  fails on T3 alone, whose total is 0.006 bits; noted, not argued).
- **P4 held, with a finding.** Q3 has the largest r3→r4 gap of any query
  (0.0013 at ε=1) — the lineage cargo is allocator state and it lands on
  Q3. But the second clause was wrong in an instructive way: Q3ids − Q3
  is **exactly 0.0 at every rung**, not "smaller at r4." Mechanism, found
  by enumeration: every lone id-1 request at horizon 12 arises from an
  IO_ISSUE at t=11 followed by another thread's IO_COMPLETE at t=12 —
  both always inside the L=2 window at T=12. The zero is
  **horizon-bounded, not structural**. Pre-stated for the (14,4,2) run
  (started before this paragraph was written): at T=12, L=4 the window
  is {9..12} and a pre-window issue at t≤8 with a competing completion at
  12 creates the id-0/id-1 twin, so **Q3ids − Q3 should be strictly
  positive at r1–r3 (tiny mass) and return to 0 at r4**.

### Findings (v0.1, one law, one horizon)

1. **The lineage rung is worth 0.0013 bits of state entropy at ε=1 and
   0.0000 at ε=1/2** — against r1→r2 = 0.133 and r2→r3 = 0.145. In mean
   *support* the same rung separated by 0.3166 (day six). D9's
   "support ≠ entropy" warning is now a measured 100:1 ratio: the r3/r4
   separation is a combinatorial fact about rare states, not an
   information fact about likely ones. **Every declared query moves
   ≤ 0.0013 bits across r3→r4.**
2. **The ladder is query-specific.** Q1[L0], Q5 live at r3; Q1[L1], Q4
   live at r2; Q2 is spread; Q3 is essentially flat across the ladder
   (0.003 bits total) — the in-flight set is an r1 question (IO_ISSUE /
   IO_COMPLETE with actor), and its residual 0.2 bits is pre-window
   history that no rung recovers. Interface content and window geometry
   are separate axes, and different queries load on different ones.
3. **Queries recover a fraction of state entropy.** H(S_T) ≈ 2.8 bits at
   r4; the largest single query ceiling is 0.60 (Q4[L0]) — most state
   uncertainty at this law is in fields no declared query asks about
   (pc, rr_cursor). This is the D1 rationale seen from the other side.

### Control — WindowLaw(12,12,2) (raw: `c1-query-ceilings-12-12-2-raw-2026-08-15.json`)

**P5 held.** 86,086 distinct windows at every rung (every path its own
window — injectivity at the record level), two-path matched on all of
them, and H(S_T) = H(Q) = 0.0000 for every query, every rung, both ε.
Wall clock 6m27s. The query layer reduces to the theorem where it must.

### The failed prediction, and its replacement (pre-stated before the (14,2,2) run)

**The (14,4,2) prediction FAILED**: Q3ids − Q3 = 0.0 exactly at every
rung, both ε. Diagnosis by exhaustive enumeration at horizon 14 (17
deep-completion signatures, matching the day-six census): the *second*
concurrent IO_ISSUE in C1 never occurs before t = 11 (first at 3/5/7/9 or
11, second at 11 or 13). The id-0/id-1 twin needs BOTH issues hidden
before the window; on (12,2,2) and (14,4,2) every endpoint's window
starts at ≤ 11, so the second issue is always visible and the survivor's
id is determined. My mechanism named the wrong hidden event (the
competing completion; it is the second issue). Corrected prediction, on
record before the run: at **(14,2,2)**, T = 14 gives window {13, 14},
issues (≤9, 11) are pre-window, deep completions at 13/14 are in-window,
discipline is stochastic — so **Q3ids − Q3 > 0 at r1–r3 and = 0 at r4**
(the completer's visible id reveals who was first). If this fails too,
the claim "the zero is horizon-bounded" is withdrawn as unsupported.

### Results — WindowLaw(14,4,2), both ε (raw: `c1-query-ceilings-14-4-2-raw-2026-08-15.json`)

Two-path matched on every window (3497/3922/4577/4698 windows at r1..r4);
P1 invariants held. Wall clock ≈ 25 min. Same columns as the (12,2,2) table.

| ε | quantity | r1 | r4 | r1→r2 \| r2→r3 \| r3→r4 | resolved r1→r4 |
|---|---|---|---|---|---|
| 1 | H(S_T) | 1.3436 | 1.0944 | 0.1300 \| 0.1174 \| **0.0017** | — |
| 1 | Q1[L0] | 0.2535 | 0.1150 | 0.0238 \| 0.1145 \| 0.0001 | 0.745→0.922 |
| 1 | Q1[L1] | 0.2202 | 0.0993 | 0.1128 \| 0.0081 \| 0.0000 | 0.692→0.841 |
| 1 | Q2[T0] | 0.2641 | 0.2167 | 0.0294 \| 0.0177 \| 0.0003 | 0.760→0.789 |
| 1 | Q2[T1] | 0.2334 | 0.2011 | 0.0083 \| 0.0239 \| 0.0001 | 0.766→0.800 |
| 1 | Q2[T2] | 0.1996 | 0.1850 | 0.0059 \| 0.0084 \| 0.0004 | 0.795→0.820 |
| 1 | Q2[T3] | 0.1498 | 0.1450 | 0.0010 \| 0.0025 \| 0.0013 | 0.848→0.855 |
| 1 | Q3[D0] | 0.0672 | 0.0646 | 0.0004 \| 0.0005 \| 0.0017 | 0.766→0.863 |
| 1 | Q4[L0] | 0.3423 | 0.2692 | 0.0423 \| 0.0307 \| 0.0001 | 0.639→0.723 |
| 1 | Q4[L1] | 0.0185 | 0.0028 | 0.0155 \| 0.0001 \| 0.0000 | 0.969→0.993 |
| 1 | Q5 | 0.2749 | 0.1932 | 0.0257 \| 0.0560 \| 0.0001 | 0.724→0.809 |
| 1/2 | H(S_T) | 0.7976 | 0.6767 | 0.0706 \| 0.0502 \| **0.0001** | — |
| 1/2 | Q1[L0] | 0.1437 | 0.0841 | 0.0096 \| 0.0499 \| 0.0000 | 0.739→0.921 |
| 1/2 | Q1[L1] | 0.1284 | 0.0609 | 0.0640 \| 0.0034 \| 0.0000 | 0.727→0.841 |
| 1/2 | Q2[T0] | 0.1119 | 0.0741 | 0.0273 \| 0.0105 \| 0.0000 | 0.856→0.879 |
| 1/2 | Q2[T1] | 0.1395 | 0.1201 | 0.0015 \| 0.0179 \| 0.0000 | 0.770→0.789 |
| 1/2 | Q2[T2] | 0.0786 | 0.0714 | 0.0032 \| 0.0040 \| 0.0000 | 0.873→0.903 |
| 1/2 | Q2[T3] | 0.0634 | 0.0616 | 0.0011 \| 0.0006 \| 0.0001 | 0.909→0.912 |
| 1/2 | Q3[D0] | 0.0417 | 0.0408 | 0.0006 \| 0.0002 \| 0.0001 | 0.832→0.906 |
| 1/2 | Q4[L0] | 0.2249 | 0.1716 | 0.0318 \| 0.0215 \| 0.0000 | 0.646→0.702 |
| 1/2 | Q4[L1] | 0.0085 | 0.0004 | 0.0081 \| 0.0000 \| 0.0000 | 0.976→0.997 |
| 1/2 | Q5 | 0.1674 | 0.1173 | 0.0176 \| 0.0325 \| 0.0000 | 0.729→0.819 |

Q3ids ≡ Q3 to float precision at every rung (see the failed prediction
above). Read against (12,2,2):

- **Window length vs. rung content.** L = 2 → 4 lowers H(S_T) at r4 from
  2.78 to 1.09 bits (ε=1); the entire r1→r4 ladder at L = 4 is worth 0.25.
  Geometry is the big axis, content the small one — for the queries too:
  Q1[L0] resolved on 67% of law mass at (12,2,2)/r4 and on 92% here.
- **The lineage rung, second law: 0.0017 bits** (ε=1), 0.0001 (ε=1/2);
  once more the largest r3→r4 mover is Q3 (0.0017) — allocator cargo,
  landing on the in-flight query, and worth nothing anywhere else
  (Q1/Q4/Q5 ≤ 0.0001).
- **P2's half-refutation replicates**: r2→r3 dominates Q1[L0] and Q5;
  r1→r2 dominates Q1[L1] and Q4[L0]/Q4[L1] — at both ε.
- **Third law running (ε=1/2 lower everywhere) holds** for every query
  at this law as at (12,2,2).


### Results — WindowLaw(14,2,2), both ε (raw: `c1-query-ceilings-14-2-2-raw-2026-08-15.json`)

Two-path matched on every window (223/250/359/406 windows at r1..r4);
P1 held. H(S_T) r1→r4: 3.3514→3.0145 (ε=1; gaps 0.1378 | 0.1953 |
0.0038), 2.4508→2.2662 (ε=1/2; 0.0792 | 0.1051 | 0.0003). Query rows in
the raw JSON; the pattern of the two prior laws holds throughout.

**The replacement prediction split.** Q3ids − Q3, in bits:

| ε | r1 | r2 | r3 | r4 |
|---|---|---|---|---|
| 1 | 1.439e-4 | 1.432e-4 | 1.432e-4 | 9.350e-5 |
| 1/2 | 4.712e-6 | 4.709e-6 | 4.709e-6 | 3.615e-6 |

- Clause 1 **held**: strictly positive at r1–r3. The id-0/id-1 twin
  exists once both concurrent issues are hidden; "the zero is
  horizon-bounded, not structural" stands, and the id surplus is
  1.4×10⁻⁴ bits at its first appearance.
- Clause 2 **failed**: r4 drops the surplus by ~35% (ε=1) / ~23% (ε=1/2)
  but not to zero. Cause, from the enumeration already in hand: deep
  completions at t = 12 exist (issues (3..9, 11)) and at T = 14 the
  {13,14} window does not contain them; a lone survivor whose id was
  fixed by a *pre-window* completion has no in-window evidence at any
  rung. I assumed the resolving completion was visible; only some are.
  Two predictions about this one number, each half right — the
  geometry each time correct, the hidden event each time misassigned.

## Findings (v0.1, three windowed laws + one full-context control, C1, ε ∈ {1, ½})

1. **Query ceilings exist and are two-path verified**: for every declared
   query, every rung, three laws — the observation-gap ceiling on the
   M1 targets is now a measured table, not a proxy. Full-context control
   is exactly zero everywhere (theorem).
2. **The lineage rung carries 0.0013 / 0.0017 / 0.0038 bits** of state
   entropy at (12,2,2) / (14,4,2) / (14,2,2), ε=1 (≤ 0.0003 at ε=1/2),
   against 0.13–0.20 for each of the other two rungs. Day six's r3/r4
   *support* gap of 0.32 at (12,2,2) is a ~100:1 support-to-bits ratio:
   D9's "support ≠ entropy" is a measured fact about this rung. What
   r4 carries lands on Q3 (in-flight) — allocator cargo — and on nothing
   else above 10⁻⁴ bits.
3. **The ladder is query-specific**: r2→r3 (owner via `related`) is the
   big rung for Q1 on the contended lock and Q5; r1→r2 (object) is the
   big rung for Q1 on the quiet lock and Q4; Q3 is nearly flat across the
   whole ladder. Predicting this a priori, I got Q4 wrong: field cargo
   must be read per query.
4. **Geometry over content**: L = 2 → 4 removes ~1.7 bits of state
   entropy at r4; the whole r1→r4 ladder removes ~0.25 at L = 4.
5. **Third law**: ε = ½ lowers every query ceiling at every rung and law.
6. **Q3ids − Q3 (what the identifier adds beyond thread identity under
   I5)**: exactly the id-0/id-1 twin, absent until both concurrent
   issues are hidden (first appears at (14,2,2): 1.4×10⁻⁴ bits), and not
   fully resolved even at r4 when the settling completion is pre-window.

## Caveats

1. Mean entropy in bits, law-mass weighted, from exact Fraction
   posteriors with float logs — sums are floats; "exactly 0.0" claims
   are float sums and should be read as "no window carries the
   distinction" (checkable directly, and checked for Q3ids at (12,2,2)
   by enumeration of the lone-id-1 habitat).
2. Q4 and Q5 are my operationalizations of Part I's wording (docstring in
   `queries.py`); the completion-side "next wake" is excluded as a
   predictive query. Predictive-state targets are not measured here.
3. One world, horizons ≤ 14, laws chosen for budget; the ε=1/2 branching
   makes (14,·,·) the practical ceiling for this script (~25 min).
4. Every prediction I made about the r4 behavior of the id surplus was
   at least half wrong. The geometry intuition was right three times;
   the hidden-event assignment was wrong three times. Read finding 6 as
   measured, not as understood.

---

## v0.2 results — statutory per-pair Q5[Tb,Tr], three laws (reruns under the v0.2 labels)

All three raw JSONs now carry the v0.2 labels; every relabeled query's
value is identical to its v0.1 run (checked at r4, both ε). Below: the
ordered pairs with nonzero ceiling (the other 4 of 12 are identically 0 —
pairs the programs never realize), mean bits r1→r4 with adjacent gaps.

**(12,2,2)**

| ε | pair | r1 | r4 | r1→r2 \| r2→r3 \| r3→r4 |
|---|---|---|---|---|
| 1 | Q5[T0,T1] | 0.2221 | 0.1901 | 0.0133 \| 0.0187 \| 0.0000 |
| 1 | Q5[T0,T2] | 0.0357 | 0.0161 | 0.0001 \| 0.0195 \| 0.0000 |
| 1 | Q5[T1,T0] | 0.2026 | 0.1819 | 0.0012 \| 0.0195 \| 0.0000 |
| 1 | Q5[T1,T2] | 0.0357 | 0.0161 | 0.0002 \| 0.0194 \| 0.0000 |
| 1 | Q5[T1,T3] | 0.0051 | 0.0022 | 0.0029 \| 0.0000 \| 0.0000 |
| 1 | Q5[T2,T0] | 0.0923 | 0.0693 | 0.0002 \| 0.0228 \| 0.0000 |
| 1 | Q5[T2,T1] | 0.0990 | 0.0714 | 0.0051 \| 0.0225 \| 0.0000 |
| 1 | Q5[T3,T1] | 0.0035 | 0.0035 | 0.0000 \| 0.0000 \| 0.0000 |
| 1/2 | Q5[T0,T1] | 0.1801 | 0.1555 | 0.0101 \| 0.0144 \| 0.0000 |
| 1/2 | Q5[T0,T2] | 0.0114 | 0.0039 | 0.0000 \| 0.0074 \| 0.0000 |
| 1/2 | Q5[T1,T0] | 0.3155 | 0.2998 | 0.0008 \| 0.0149 \| 0.0000 |
| 1/2 | Q5[T1,T2] | 0.0105 | 0.0035 | 0.0000 \| 0.0070 \| 0.0000 |
| 1/2 | Q5[T1,T3] | 0.0012 | 0.0002 | 0.0010 \| 0.0000 \| 0.0000 |
| 1/2 | Q5[T2,T0] | 0.0721 | 0.0524 | 0.0000 \| 0.0197 \| 0.0000 |
| 1/2 | Q5[T2,T1] | 0.0518 | 0.0348 | 0.0017 \| 0.0153 \| 0.0000 |
| 1/2 | Q5[T3,T1] | 0.0004 | 0.0004 | 0.0000 \| 0.0000 \| 0.0000 |

**(14,4,2)**

| ε | pair | r1 | r4 | r1→r2 \| r2→r3 \| r3→r4 |
|---|---|---|---|---|
| 1 | Q5[T0,T1] | 0.0981 | 0.0717 | 0.0114 \| 0.0151 \| 0.0000 |
| 1 | Q5[T0,T2] | 0.0165 | 0.0039 | 0.0014 \| 0.0112 \| 0.0000 |
| 1 | Q5[T1,T0] | 0.0842 | 0.0651 | 0.0035 \| 0.0155 \| 0.0000 |
| 1 | Q5[T1,T2] | 0.0179 | 0.0042 | 0.0015 \| 0.0122 \| 0.0000 |
| 1 | Q5[T1,T3] | 0.0078 | 0.0013 | 0.0065 \| 0.0000 \| 0.0000 |
| 1 | Q5[T2,T0] | 0.0496 | 0.0288 | 0.0015 \| 0.0193 \| 0.0000 |
| 1 | Q5[T2,T1] | 0.0582 | 0.0346 | 0.0030 \| 0.0207 \| 0.0000 |
| 1 | Q5[T3,T1] | 0.0030 | 0.0030 | 0.0000 \| 0.0000 \| 0.0000 |
| 1/2 | Q5[T0,T1] | 0.0493 | 0.0286 | 0.0104 \| 0.0103 \| 0.0000 |
| 1/2 | Q5[T0,T2] | 0.0056 | 0.0005 | 0.0010 \| 0.0040 \| 0.0000 |
| 1/2 | Q5[T1,T0] | 0.0821 | 0.0660 | 0.0016 \| 0.0145 \| 0.0000 |
| 1/2 | Q5[T1,T2] | 0.0059 | 0.0005 | 0.0010 \| 0.0044 \| 0.0000 |
| 1/2 | Q5[T1,T3] | 0.0038 | 0.0002 | 0.0036 \| 0.0000 \| 0.0000 |
| 1/2 | Q5[T2,T0] | 0.0332 | 0.0161 | 0.0004 \| 0.0166 \| 0.0000 |
| 1/2 | Q5[T2,T1] | 0.0254 | 0.0136 | 0.0010 \| 0.0108 \| 0.0000 |
| 1/2 | Q5[T3,T1] | 0.0005 | 0.0005 | 0.0000 \| 0.0000 \| 0.0000 |

**(14,2,2)**

| ε | pair | r1 | r4 | r1→r2 \| r2→r3 \| r3→r4 |
|---|---|---|---|---|
| 1 | Q5[T0,T1] | 0.2415 | 0.2088 | 0.0114 \| 0.0212 \| 0.0001 |
| 1 | Q5[T0,T2] | 0.0404 | 0.0216 | 0.0002 \| 0.0186 \| 0.0000 |
| 1 | Q5[T1,T0] | 0.2174 | 0.1907 | 0.0021 \| 0.0246 \| 0.0001 |
| 1 | Q5[T1,T2] | 0.0425 | 0.0224 | 0.0004 \| 0.0197 \| 0.0000 |
| 1 | Q5[T1,T3] | 0.0151 | 0.0087 | 0.0062 \| 0.0002 \| 0.0000 |
| 1 | Q5[T2,T0] | 0.1186 | 0.0915 | 0.0005 \| 0.0266 \| 0.0000 |
| 1 | Q5[T2,T1] | 0.1354 | 0.1055 | 0.0044 \| 0.0254 \| 0.0000 |
| 1 | Q5[T3,T1] | 0.0142 | 0.0140 | 0.0000 \| 0.0002 \| 0.0000 |
| 1/2 | Q5[T0,T1] | 0.1843 | 0.1563 | 0.0087 \| 0.0193 \| 0.0000 |
| 1/2 | Q5[T0,T2] | 0.0136 | 0.0057 | 0.0001 \| 0.0077 \| 0.0000 |
| 1/2 | Q5[T1,T0] | 0.3073 | 0.2837 | 0.0013 \| 0.0223 \| 0.0000 |
| 1/2 | Q5[T1,T2] | 0.0137 | 0.0056 | 0.0001 \| 0.0080 \| 0.0000 |
| 1/2 | Q5[T1,T3] | 0.0066 | 0.0029 | 0.0036 \| 0.0001 \| 0.0000 |
| 1/2 | Q5[T2,T0] | 0.1038 | 0.0785 | 0.0001 \| 0.0252 \| 0.0000 |
| 1/2 | Q5[T2,T1] | 0.0803 | 0.0578 | 0.0014 \| 0.0211 \| 0.0000 |
| 1/2 | Q5[T3,T1] | 0.0054 | 0.0053 | 0.0000 \| 0.0000 \| 0.0000 |

Reading: for every material pair at every law and ε, the r2→r3 owner rung
carries the bulk of the drop and r3→r4 is ≤ 0.0001 bits; the r1→r2 share
is largest for pairs whose blocked thread contends the quiet lock
(Q5[T1,T3]) — consistent with the (12,2,2) decomposition, and stated as
consistent, not as mechanism. The joint proxy's story holds pair by pair.
Q5[T1,T0] is the pair with the highest ceiling at ε=½ (0.28–0.30 bits at
r4): thread 1 blocked on the lock thread 0 holds while running is the
single most-hidden relational fact in this world at these laws.
Statutory Q4 remains unimplemented (v0.2 item 1).
