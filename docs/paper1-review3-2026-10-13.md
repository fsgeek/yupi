# Third whole-draft review of paper 1 (2026-10-13, night): record

> Reviewed: v0.3 of every section, Appendix A, Figure 4a. Claude and Codex ran in parallel; **both returned READY
> AFTER FIXES.** Owning instance.

**Blocking, raised by both and reproduced by the owner.** The v0.3 abstract and §1 claimed that identifiability and
predictive value *rank fields differently*. Table 3.0 shows the opposite. Both measures rank RELATED > OBJECT >
LINEAGE at both ε, and differ in scale by a nearly constant 3.1–4.7×, a scale bounded by I(next; S | w) ≤ H(S | w).
**Corrected** (commit 9913445) to "most state uncertainty is irrelevant to the next event; the two measures agree on
ranking". This claim was the owner's, promoted the same evening without checking the per-field deltas. That is the
recurring failure: a summary sentence written before the finest-grain check.

**Also blocking (both reviewers): observer, position and target were not separated.** Table 3.0 is the structural
observer at the last record over all windows. The rest is the pattern observer at k = 7 over 0.85 of mass. Fixed:
§2.3 exempts Table 3.0, §3.0 carries a reconciliation note, Log20 is described as "a quantity of this kind", and
§1 qualifies the observer.

**Should-fix, all adopted:**
- "converged" removed everywhere, including the Figure 4a legend;
- the experiment table gains GRU and d = 256 rows;
- internal provenance taken out of body text, and the four-state argument reproduced;
- relay *recipe* distinguished from the copy itself;
- the GRU's floor applied to d = 256, whose models pass it;
- d = 256 "under-trained" softened;
- class counts labelled;
- numeric slips corrected (2.312; 0.80 and 0.59; 82–91; the memory figures);
- the GRU post hoc sentence removed and the G2 table added with ACTOR;
- actual paired p-values and the resolution rule;
- "none of C1–C3 resolves on ACTOR";
- the §7 KL/entropy-gap wording and the order-m convention;
- the scoring-denominator sentence;
- appendix normalisation and the qualified provenance claim;
- the Futrell venue;
- a reference list drafted.

**Not adopted, with reasons.** The ladder validation-curve plot promised under W12: the numeric diagnostic is given
instead, and the plot is withdrawn as unnecessary at workshop scope. A pattern-observer state entropy at k = 7, the
reviewers' route to an aligned Table 3.0, is deferred and named as a limit.

**Remaining before submission:**
- the venue and its length;
- ARIES wording from the paper itself;
- 2512.22471 and 2605.20824 read beyond their abstracts;
- author lists marked [check] in the references;
- body text cleared of status brackets and file names.
