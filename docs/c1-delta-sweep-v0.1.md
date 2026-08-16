# δ sweep — where a rung-collapse threshold would fall (Part II v0.2.4 §C, sweep 1 of 3)

**Working note v0.1 — 2026-08-15, committed 21:16 PDT (14484c7; the draft first said "~21:30", a guessed time — corrected from git). Exploratory read of stamped
artifacts; proposes a δ for the second stamped decision, does not enact one.**
Script: `scripts/c1_delta_sweep.py` → raw `docs/c1-delta-sweep-raw-2026-08-15.json`.
Inputs: `c1-query-ceilings-{12-2-2, 14-2-2, 14-4-2, 12-12-2}-raw-2026-08-15.json`
(Q1, Q2, Q3, Q5 per pair) and `c1-q4-ceilings-*-W{4,8}-raw-2026-08-15.json`
(Q4 statutory). No new filtering was run; the numbers below are differences of
the law-mass-weighted mean posterior entropies those artifacts already hold
(presentation floats of exact rationals — see caveat 1).

## 1. What is being swept

Part II §6: adjacent rungs $r, r'$ **collapse** at context $L$ if
$\max_{q \in Q}\,[H_r(q\mid L) - H_{r'}(q\mid L)] < \delta$ bits, $Q$ the
complete statutory set {Q1[l] ×2, Q2[i] ×4, Q3[dev] ×1, Q4 statutory (W), Q5[i_b,i_r] ×12}.
Diagnostics (Q3thr, Q4proxy, Q5joint; v0.1 labels Q3ids/Q4[l]/aggregate Q5 in the control
artifact) are printed by the script but excluded from the max. Rungs: r1 = kind+actor;
r2 = +object; r3 = +related; r4 = +lineage (`src/yupi/interfaces.py`).

The quantity δ is compared against is therefore **one number per (law, ε, rung pair)**:
the per-cell max. Eighteen windowed cells exist (3 laws × 2 ε × 3 pairs); the script
counts 30 windowed *entries* because Q4 exists at W=4 everywhere and also at W=8 for
two laws, and W never changes the max (§3) — plus six control entries, 36 in all.

## 2. The cells

Per-cell max statutory gap, bits, with the query attaining it. (Where both W=4 and
W=8 Q4 artifacts exist the max is identical — Q4 is never the argmax.)

| law (T_ep,L,B) | ε | r1→r2 | argmax | r2→r3 | argmax | r3→r4 | argmax |
|---|---|---|---|---|---|---|---|
| (12,2,2) | 1 | 0.122083 | Q1[L1] | 0.143061 | Q1[L0] | 0.001285 | Q3[D0] |
| (12,2,2) | ½ | 0.074623 | Q1[L1] | 0.067792 | Q1[L0] | 0.000043 | Q3[D0] |
| (14,2,2) | 1 | 0.113993 | Q1[L1] | 0.184571 | Q1[L0] | 0.003728 | Q3[D0] |
| (14,2,2) | ½ | 0.071079 | Q1[L1] | 0.102801 | Q1[L0] | 0.000346 | Q3[D0] |
| (14,4,2) | 1 | 0.112787 | Q1[L1] | 0.114536 | Q1[L0] | 0.001733 | Q3[D0] |
| (14,4,2) | ½ | 0.063998 | Q1[L1] | 0.049943 | Q1[L0] | 0.000146 | Q3[D0] |
| (12,12,2) control | 1, ½ | 0 | — | 0 | — | 0 | — |

Sorted, the eighteen windowed per-cell maxima are:

```
r3→r4:  0.000043  0.000146  0.000346  0.001285  0.001733  0.003728
        ---------- no cell max between 0.003728 and 0.049943 ----------
r2→r3 / r1→r2:
        0.049943  0.063998  0.067792  0.071079  0.074623  0.102801
        0.112787  0.113993  0.114536  0.122083  0.143061  0.184571
```

Coverage of the §6 criterion under a grid of candidate δ (from the script; "collapsed"
= max < δ; counts are over the 36 entries — W-duplicated cells count twice — of which
the 6 control entries collapse at any δ > 0):

| δ (bits) | collapsed | which |
|---|---|---|
| 1e-4 | 8/36 | control ×6; (12,2,2) ε=½ r3→r4 (both W) |
| 3e-4 | 10/36 | + (14,4,2) ε=½ r3→r4 |
| 1e-3 | 11/36 | + (14,2,2) ε=½ r3→r4 |
| 3e-3 | 15/36 | + (12,2,2) ε=1, (14,4,2) ε=1 r3→r4 |
| 1e-2 | 16/36 | **all r3→r4, no r1→r2 or r2→r3** |
| 3e-2 | 16/36 | same as 1e-2 |
| 1e-1 | 25/36 | + five ε=½ r1→r2/r2→r3 cells (nine entries with W duplicates): (12,2,2) both pairs, (14,2,2) r1→r2, (14,4,2) both pairs; **zero ε=1 cells**, and (14,2,2) ε=½ r2→r3 (0.102801) does not collapse |
| 3e-1 | 36/36 | everything |

Statutory per-query gaps, all cells, by decade (698 entries; the 198 "≤0" are
structural zeros — Q5 pairs that are zero at every rung, and the control law):
1e-11: 4, 1e-10: 6, 1e-9: 3, 1e-8: 17, 1e-7: 15, 1e-6: 35, 1e-5: 46, 1e-4: 69,
1e-3: 114, 1e-2: 130, 1e-1: 11. **Individual query gaps form a continuum with no
empty decade; only the per-cell max is bimodal.** The statute's criterion is the
max, so the bimodality is the thing that matters — but a per-query criterion would
not have found a band.

## 3. What the read shows (each sentence names its cells)

1. **A one-decade empty band.** No windowed cell max lies in (0.003728, 0.049943).
   Every δ in that open interval yields the same verdict on every measured cell:
   r3→r4 collapses in all six (law, ε) cells; r1→r2 and r2→r3 collapse in none.
   The log-midpoint of the band is 0.0136; the round number inside it is 0.01.
2. **The argmax is fixed per pair.** r1→r2 is Q1[L1] in 6/6 cells; r2→r3 is Q1[L0]
   in 6/6; r3→r4 is Q3[D0] in 6/6. Lock-owner queries carry the object and related
   rungs. Q3[D0] r3→r4 gaps: 0.001285, 0.000043, 0.003728, 0.000346, 0.001733,
   0.000146. Six r3→r4 per-query gaps exceed 1e-3 across all cells, in three
   cells, all ε=1: (12,2,2) Q3[D0] 0.001285; (14,2,2) Q3[D0] 0.003728, Q2[T3]
   0.001841, Q2[T0] 0.001218; (14,4,2) Q3[D0] 0.001733, Q2[T3] 0.001278. At ε=½
   no r3→r4 gap reaches 1e-3.
3. **W does not enter.** Q4stat gaps: r1→r2 0.0066–0.0331, r2→r3 0.0106–0.0344,
   r3→r4 0.000004–0.000529 across W∈{4,8}; Q4's gap is at most 0.34× the cell max
   (closest: (14,4,2) ε=½ r1→r2 at W=8, 0.021740 vs 0.063998; all 30 ratios in
   the raw JSON lie in 0.07–0.34). The Q4 irreducible term differs across rungs by ≤ 1.6e-15 in every cell
   (conservation, as previously reported).
4. **The r3→r4 max is not small everywhere in the same way.** At L=2, going
   T_ep 12→14: ε=1 0.001285→0.003728, ε=½ 0.000043→0.000346 (both increase).
   At T_ep=14, going L 2→4: ε=1 0.003728→0.001733, ε=½ 0.000346→0.000146 (both
   decrease). Two comparisons each; no monotone claim beyond them. The largest
   r3→r4 max (0.003728) is 2.7× below 0.01; a longer T_ep at L=2 could plausibly
   cross it. That is a falsifier for "r3/r4 collapse," not a reason to move δ.
5. **The band is a property of these three laws, not a theorem.** Only L∈{2,4}
   and T_ep∈{12,14} exist. The empty band could fill in at other laws; the
   freeze is a commitment made knowing that.

## 4. Proposal for the second stamped decision (δ only; not enacted here)

**δ = 0.01 bits.** Reasons, in order: it lies inside the empty band, so it is
decision-invariant over every cell that exists (any δ in (0.0037, 0.0499) gives
identical verdicts — the choice within the band is cosmetic and 0.01 is the
least arbitrary point in it); it is ~2.7× above the largest measured r3→r4 max
and ~5× below the smallest r1→r2/r2→r3 max, so a future cell that lands near δ is
a finding about that cell rather than a threshold artifact; it is far coarser
than float error in the inputs (caveat 1); and it is one significant figure, so
nobody can later read the freeze as tuned. **Consequence if adopted:** on all
measured laws the lineage rung collapses onto r3 under the §6 criterion, and the
statute would say so as a confirmatory statement only for measurements after the
second stamp.

Not proposed: δ_sync (needs an L sweep at fixed T_ep — sweep 2), δ_p and Δ_τ
(need the pairwise-TV distributions — sweep 3). This note discharges sweep 1
only. The second stamped decision should wait for all three unless Tony prefers
to freeze δ alone now; nothing in this note requires that.

## 5. Caveats

1. **Floats.** The artifacts store mean_bits as floats; the smallest non-zero
   gaps (1e-11 – 1e-8) are at or near roundoff of exact zeros. Nothing in §3–§4
   depends on any gap below 1e-5. If a δ near 1e-4 were ever proposed, the sweep
   would have to be redone from Fractions.
2. **Statutory set completeness.** Q4 statutory enters via its total (the split
   is available); Q3thr/Q4proxy/Q5joint are excluded per Part II §5. If a future
   Part II adds queries, the max can only rise, so the band can only narrow from
   above the r3→r4 cluster or fill in — never widen. A collapse verdict is
   therefore conservative in one direction only.
3. **Adjacent pairs only.** The criterion is adjacent-rung; r1→r3 or r2→r4
   spans are not computed here and are not part of the statute.
4. **Nothing here is a claim about transformers.** Every number is an exact
   Bayes ceiling difference. Whether a learner recovers r3's information at r4
   cost is a Milestone-3 question.

## 6. Ledger

Predictions before the run: (a) r3→r4 would be the small cluster (from the
day-seven "lineage rung ~0.002 bits" finding) — held; (b) I expected the r1→r2 vs
r2→r3 clusters to be separable — **not held**: they interleave (0.0499–0.0746
and 0.0500–0.1846 overlap; sorted list in §2 mixes them); (c) I did not predict
the fixed argmax per pair (§3.2) — found on printing. **Draft errors caught by
re-checking the JSON before commit, all sentences wider than their cells:** "Q4
never within a factor of 3 of the max" (closest ratio 0.34); "Q3[D0] is the only
query the lineage rung moves above 1e-3" (Q2[T3], Q2[T0] also do, in two cells);
the δ=0.1 coverage row ("six ε=½, three ε=1" — actually five ε=½, zero ε=1); and
"thirty windowed cells" (eighteen cells, thirty entries). Four in one draft.
The check that caught them was mechanical (a script over the JSON), not
attention.
