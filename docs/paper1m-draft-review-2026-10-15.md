# Methods-paper draft v0.1: whole-draft review record (2026-10-15)

> Both families: **SUBMITTABLE AFTER FIXES**, independently. Owning instance. Codex's first run stopped silently and
> its first waiter fired on an `exit 0` line in its own transcript; a duplicate run was killed and the original
> completed (process-ID waiter). Reviewer scripts used by the owner are archived under `scripts/review/`.

## Converged
1. **§4.3 over-reads the monitor statistic** (Claude #1, Codex #1). a_w uses the true class's TV as its radius and
   prior weights: an oracle-calibrated look-alike share, not a monitor error rate. s4:72–73 ("would mostly read …
   correctly") breaks the declared BETWEEN rule. Claude adds: "kind" switched meaning between §4.2 (G = 0 vs
   withheld) and §4.3 (R pinned). **Adopted**: sentence deleted; a_w renamed; a declared G-kind measurement is running
   (`learner-precision-monitor-check-2026-10-15.md`, second declaration, e3b81ac).
2. **δ vs 2δ** (Codex #2; Claude v0.8 #4): define δ as pairwise separation between exact laws. **Adopted.**
3. **Abstract relay claim** (Claude #2, Codex #6). **Adopted**: "the training target contributes; whether the copy adds
   anything is unresolved at three seeds."
4. **3–5× scope** (Claude #3, Codex #4): ACTOR's ratio is 11.5 / 9.3 and changes the target; **reproduced by the
   owner**. Restricted to OBJECT/RELATED/LINEAGE on r1–r4.
5. **Graded support** (Claude #5, Codex #3): owner's 17–22 / 36–43 % used bins with ≥ 0.5 % mass and ≥ 5 classes;
   without that restriction 19–24 / 38–44 %. **Adopted**: convention stated, both reported; script committed.
6. **Abstract scoping** (Claude #6, Codex #6): R's invariance by construction and in the mean; r3 = r4 on KIND.
7. **Contribution statement** (Claude #8, Codex #10): credit ChatGPT's co-design of the founding proposal and Codex's
   substantive contributions (the thesis sentence; the r3 collision); "every commit" → "a timestamped Git history";
   local caches distinguished from committed summaries. **Adopted.**
8. **Provenance** (Claude #4, Codex #11): split-v2 rows now pinned (`split-v2-rows-sha256-2026-10-15.txt`); reviewer
   scripts archived. A per-interface support table with both matched sides is owed (Codex #11).
9. **Positioning** (Claude #9, Codex #8–#9): Ahdritz §5.1 verified by both (a type bit in the question; one-step
   predictions near 50/50 in both conditions; the kind shows in contextual updating) — the closest precedent;
   Vafa 2025 not "automaton worlds"; Vafa 2024 adds Mullainathan [check]; Agarwal et al. sample transition and
   emission matrices, so say what *our* comparison fixes; Someya: m-local entropy conditions on m − 1 symbols, and
   their entropy-preserving interventions and exact-PFSA excess loss are close to §3.4–§5; Bergna's decomposition is
   additive variance, related to but not identical with ours; Li et al. compare representations with the board, not
   with Bayes quantities. **Adopted.**
10. **Stale references and author-facing text** (Claude #11, #16; Codex #12): "§4 learner analysis" → §5; Figure 4a
    absent; headers and provenance stripped for submission; "ayllu" explained once.

## Single reviewer
- Codex #5: the audit was run retrospectively (2026-10-15), after the learner studies; §1 must not say "before
  training". **Adopted.**
- Codex #7: restore definitions dropped in compression (shortfall normalisation vs the monitor's KIND-only
  renormalisation; the unscored loss-denominator change; which pending request completes is uniform; the structural
  predictive gap is a second exception to the pattern-observer default). **Adopted.**
- Codex #13: r3 and r4 effectively tied at lags 1–3; bins rise monotonically above ι₄ = 0.001. **Adopted.**
- Claude #10: "GPU-days" and "under a minute" need sources. **Adopted**: replaced with measured figures or cut.
- Claude #13–#14: report the TV tail; collision share is of position-7 mass. **Adopted.**

## Final read of v0.2 (both families: SUBMITTABLE AFTER FIXES), applied in v0.3 (7fdfb95)

- **Abstract's twelve-model sentence** (both, BLOCKING): now carries the oracle-calibrated definition and the 10 %
  threshold for both senses.
- **Two senses of kind** (Claude #2–#3, Codex #1): kind defined as §4.2's two sides with an unclassified middle; an
  **exact kind sweep** added (`scripts/support_audit_table.py`, run by the owner, reproducing Claude's values): kind
  differs on 0.1–1.7 % at δ = 0.01, 14–19 % at 0.02, 16–23 % at 0.05; R on 1.8–2.4 % at 0.02 and 43–44 % at 0.05. The
  monitor's dilution (deterministic as pure; unclassified windows score 0) and its group-mean approximation
  (Codex #5) are disclosed, and the conditional shares bounded (< 2.3 % mean, < 6.4 % of windows).
- **δ/2δ** (both): restated as "two laws within η of one prediction are within 2η of each other".
- **r3 vs r4** (Codex #3): "agrees to within 10⁻⁵ bits", not equality.
- **Support table** (both): both matched sides, eligible high-gap mass, bin rule, device-coin rule; all pure mass is
  matched, in three shared bins; script committed (`support-audit-table-40-8-2-k7-2026-10-15.json`).
- **Declaration order** (Claude #5): stated in §4.3.
- **§6** (both): 0.79 over paired test windows; exploratory with a declared reading; one cell, reviewer-added FE.
- **Rounding, scope, timings** (both): 0.5–1.4 %; R and swaps r1/r3 only, swaps ≥ 0.05 each; timings reduced to the
  one with a recorded source.
- **Relay on KIND only; thesis-sentence credit** (Claude #10–#11): adopted.

**Owner's judgement:** both final reads found nothing that changes a result; every remaining item was scope or
wording. The review loop for content stops here. Next: one manuscript file in a venue format, author-facing text and
provenance moved to a supplement, and a last mechanical check of numbers against `support-audit-table-*.json` and the
monitor raws.
