The skeleton leaves out one finding, and one claim in its central lesson fails against the data. Neither the RQ5 exclusion nor the D3 deferral is written down anywhere. Several owed items are missing from §5, and the confirmatory record is incomplete. I found no finding with a not-supported verdict (`stipulated-prior-phantom-gap2`) and no withdrawn finding back in the body.

## A. A finding left out, and a claim the data contradicts

1. **`r4-outlier-basin` appears nowhere**, neither in the outline nor in the cut list. It is the only finding id in the input that the skeleton drops.
   - Source: docs/learner-first-results-40-8-2-2026-09-18.md §9.3, §10 reading 4 and §20 reading 2. Seed 1 of r4 at ε=½ scores 0.239 against a five-seed core of 0.078–0.106.
   - It belongs beside `r4-two-basins` in §6 of the skeleton.

2. **Lesson part (1), "the exact ceilings fall monotonically down the interface ladder", fails for the ceiling the learner is actually compared against.**
   - In docs/pattern-ceilings-40-8-2-k7-2026-09-18.json, the next-record entropy is higher at r4 than at r3:
     - ε=1: r3 1.291636, r4 1.291967 (+3.3e-4).
     - ε=½: r3 1.070013, r4 1.070119 (+1.1e-4).
   - Learner note §3 reading 4 calls them "the same to three decimals". That is a rounded summary sitting on a boundary. Checked at full precision, r4 is higher.
   - Only the canonical H(S|w) ladder is monotone.

3. **r4 against r3 is already a partial field-cost control, and the skeleton ignores it.**
   - In the corpora every request id is renamed, so the lineage field adds nothing to the pattern-level ceiling.
   - In the six-seed ε=1 data, the r4 low-basin seeds (0.054–0.066) sit at the r3 level (0.058–0.061).
   - This weighs against reading the r2 penalty as "any extra field costs the learner". The skeleton §5 item 4 calls ctrl-irr "the only experiment" that separates the two readings; that sentence should be qualified. The r4 field is not entropy-matched, which is why ctrl-irr is still needed.
   - Sources: learner note §3 reading 4, §14, §20; docs/request-id-design-question-v0.1.md v0.2–v0.3.

4. **The owner value-of-information comparison uses mismatched bases** (learner note §17.2).
   - 0.121 is the sum of per-lock mutual informations over the visible locks. It is not the joint information of the owner field.
   - It is averaged over the 25,508 of 30,000 eval windows that have a visible lock (H(next) = 1.596). The table-wide ceiling at r2 is 1.359.
   - The drop r3's field actually delivers on that subset is 0.076–0.077 bits (§17.2 reading 3), not 0.121.
   - "About 3×" uses the 3-seed gap from §13 (0.036). With the 6-seed r2 mean against the 3-seed r1 mean, the gap is 0.026, which makes it about 4.6×.
   - The abstract sentence and lesson part (2) need recomputing on one base.

5. **The r0→r1 step is overread.** Skeleton §3 says it "reflects attribution, not naming alone". The exit-clause note says otherwise:
   - The identity-residual check was run on C1 at horizon 14, not at (40,8,2).
   - The decomposition of the 1.08-bit step "remains open at every law".
   - Sources: docs/exit-clause-40-8-2-note-v0.1.md §5 and §11; docs/corpus-track-40-8-2-note-v0.1.md §3.1 [rv-11].
   - The identity-entropy decomposition is also not on the readiness list.

6. **"3.5–3.9×" holds at ε=1 only.** At ε=½ the ratio of corpus to canonical state entropy is 4.9–6.1× (1.4659/0.2963 through 1.0185/0.1658). Source: docs/corpus-track-40-8-2-note-v0.1.md §2.

## B. Charter RQs dropped without a recorded decision

7. **Proposal RQ5 and H7 (scale) are dropped without saying so.** Size is described as "a budget control", but the data-volume result (200k → 2M divides the excess by 4.5–5.8) is H7-shaped evidence. The decision needs a line that the project owner signs. Sources: docs/what-the-trace-surrenders-proposal-v0.2.md §4 and §9; learner note §9.

8. **The context axis of RQ1 has no within-world curve in a live world.**
   - At the frozen law only L=8 exists. The live-world L=4 ladder comes from a different world variant: (48,4,2) on unrolled C1′ (docs/c1-prime-live-census-v0.1.md).
   - The priced post-enactment control (48,6,2) is not on the readiness list. It is owed as a replication if the verdict is contested (docs/exit-clause-40-8-2-note-v0.1.md §10).
   - Proposal §6.2's condition "contexts that begin before or after causally important events" is not scoped either way.

9. **Half of the exit condition is missing.**
   - The exit condition reads "within tractable support bounds". This is E3 admission: frontier 1,964,919 against 2×10⁶ (a 1.8% margin), and peak memory 4.97 / 5.12 GB.
   - It is also founding design constraint (b).
   - The skeleton cuts `memory-refusal-and-exact-interning` and never reports the support bound.
   - Sources: docs/exit-clause-40-8-2-note-v0.1.md §1–2; docs/d4-budget-freeze-v0.1.md.

10. **Proposal items that are neither scoped in nor out:**
    - field-permutation controls (§7.3);
    - redundancy controls (Milestone 3);
    - splits across workload-program compositions and system configurations (§7.2);
    - the §8.7 generalization tests (longer episodes, changed entity counts);
    - §8.1 longer-horizon evaluation of the learner. Exact next-2-kinds, Q4 and P-next targets already exist at (40,8,2), but the learner is scored on the next record only.
    - §8.3 posterior calibration, beyond H2.

## C. Owed items not on the readiness list

11. **Belief geometry (skeleton §5 item 8) is missing several things:**
    - The §21 pairwise-distance geometry result (Spearman 0.86–0.90 at L1, 0.98–0.99 at L4) is proposal §8.2's alignment item and is absent from the RQ3 status.
    - docs/superpowers/specs/2026-09-24-belief-geometry-design.md promised things §21 never delivered: the per-window join of KL_out and KL_repr, the H*(kind) bins, and the prefix-only owner-state fold.
    - Deviations between design and execution to disclose: the λ grid was designed as {1e-4…1e-1} but run as {1e-6…1e-2}, which bears on the "grid-edge" remark; the geometry sample was designed at 2,000 windows and run at 1,000.
    - Follow-ups §21 names as inside the cut: the folded actor class as a second target, and the horizon-2 kind belief.
    - "Layerwise emergence during training" (proposal §8.2) cannot be done because checkpoints were not kept. It needs either re-runs that keep checkpoints or an explicit scope-out.
    - Probe capacity beyond λ: an MLP / tuned-probe sensitivity check (proposal §8.2; docs/literature-review-2026-08-11.md implication 4, arXiv:2502.16681).

12. **The H1 target proposed in the skeleton conflicts with the design note.**
    - A realized full-state tuple or per-field pc/owner target is entity-coordinated. The design note puts such targets out of scope because §16.1 showed pattern coordinates are not the model's own.
    - Any state tuple used must also exclude the ε=1 cursor. The corpus-track note (docs/corpus-track-40-8-2-note-v0.1.md §1) treats it as inert.

13. **Exposure-gap v0.2 (skeleton §5 item 2) omits:**
    - the 2026-09-04 addendum's constraint that G be indexed by the condition under which the output is produced, which gives the "floor" framing;
    - the §6 open problems.
    - Source: docs/exposure-gap-note-v0.1.md.

14. **Literature (skeleton §5 item 12 and §1) is missing:**
    - **Mason & Anand, arXiv:2603.20531**, the impossibility result Yupi is the constructive complement of. It is absent from §1.
    - Grid walkers, arXiv:2603.16689: architecture as the variable, which bears on the GRU baseline.
    - Shai et al., arXiv:2405.15943, and MetaOthello as contrast citations.
    - The disambiguation of "observability" that docs/literature-check-2026-09-18.md "What this changes" item 4 requires: Carmichael 2604.24801, ObserverBench 2609.03026, and the PACMI usage.
    - A full read of the nonergodic-composition blog post.
    - Grounding gap 2 in V-information (Xu et al., arXiv:2002.10689), per the literature review's implication 3.

15. **The provenance appendix (skeleton §5 item 14) is missing a disclosure.** The thirty (40,8,2) artifacts were produced before the freeze was enacted. The ordering of stamps is in docs/exit-clause-40-8-2-note-v0.1.md §10.

16. **The corpus gates don't cover the headline data.**
    - Gates 2–4 were checked only at (8,4,2), and none at (40,8,2) (docs/corpus-runs-40-8-2-2026-09-15.md).
    - I found no gate record for the 2M-window corpora that carry every headline learner number (learner note §9).

## D. The confirmatory record is incomplete

17. The skeleton quotes only the held-out Tier-1 score (1 pass / 3 fail / 1 ill-posed). Other preregistered scorecards also exist:
    - docs/w11-heldout-confirmation-v0.1.md: P1, P4 and P5 pass; P2, P3 and P6 fail.
    - docs/d8-attribution-c0b-note-v0.1.md and docs/d8-attribution-c1-note-v0.1.md: P1 and P1-mech pass, P2 fails (4 of 36 cells), P3a and P3b pass.
    - docs/d10-lineage-verdict-v0.1.md: the verdicts were corrected in v0.1.1.
    - The C0b note still says "truthsayer pass owed". The skeleton lists that, but the full scorecard belongs in the appendix.

## E. Low priority

18. Notes not represented and probably rightly left out: docs/founding-context-2026-08-21.md (a motivation choice for the introduction, if the owner wants it), docs/the-kingdom-small-enough-to-count.md (a narrative that could serve as an expository asset), and docs/relational-safety-research-seed-v0.1.md (non-governing).