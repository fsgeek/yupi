# Paper 1 skeleton (proposal for the project owner)

**Status of this draft.** This is structure only. Every number below comes from a verified finding, and where a correction was needed I use the corrected value. Where the evidence is thin I say so in the text rather than dropping the claim silently. Finding ids are in `code`, and evidence paths are relative to `/home/tony/projects/yupi/`.

**The judgment behind this skeleton.** The novelty verdicts class almost every exact-side finding as *expected* or *project-internal*. Most learner findings come out *expected* too. Only six are rated *novel-as-instrument-demo*:

- `exit-clause-canonical-ladder-distinct-40-8-2`
- `deliverable5-divergent-classes`
- `d8-c0b-allocator-eraser`
- `r0-on-ceiling`
- `owner-value-of-information`
- `ladder-eps1-six-seeds`

Paper 1 is therefore an instrument paper carrying one learner-side lesson. That lesson has two parts. (1) The exact ceilings fall monotonically down the interface ladder, but the learner's excess over them does not. (2) An exposed field can shift the observer's ceiling by roughly as much as the learner's whole shortfall, so raw losses compared across interfaces mix the observation gap with the learner gap. The lesson is currently **fragile**. It was measured at a 5-epoch recipe that §22.1 shows is under-converged. Without the converged re-run and the decoy control described in §5 it would not pass external review. I would not send the paper out before those two exist.

---

## 1. Working title and abstract draft

**Working title:** *What the Trace Surrenders, I: Exact Per-Interface Ceilings for a Small Transformer on a Finite Scheduler World*

**Alternative (use only if the converged ladder re-run holds):** *More Telemetry, Worse Learner: Exact Observability Ceilings Separate What a Trace Carries from What a Transformer Uses*

**Abstract draft.** Words in [brackets] depend on owed runs.

> We build Yupana, a finite operating-system-like stochastic world (threads, CPUs, locks, an asynchronous device) whose exact Bayesian posterior over hidden state is computable for every observed window. We vary the observation interface over a fixed generator through a five-rung ladder, from kind-only (r0) to request lineage (r4).
>
> From reset at full context, every content rung (r1–r4) yields a point-mass posterior (a structural-injectivity argument). Interface value therefore exists only where the observation window hides history. At a frozen mid-episode window law on a non-terminating world, every adjacent content-rung pair separates by more than δ = 0.01 bits at both scheduler settings. The exact state entropy falls from 0.60 to 0.39 bits across r1–r4 at ε = 1. The lineage step is thin (1.13–1.42 δ). Every window posterior was cross-checked by two computation paths (8,542,940 posteriors, zero mismatches).
>
> We compare a from-scratch 0.84M-parameter transformer against the exact pattern-level ceiling that a learner on name-randomized corpora actually faces. On kind-only traces the model is within 0.005 bits per record of that ceiling. On content rungs its excess does not follow the ceiling ladder: [at ε = 1, all six r2 seeds lie above all r1 and r3 seeds, and the OBJECT-exposing rung costs about 0.02 bits per record relative to r1]. For comparison, the owner field that r3 adds would be worth 0.121 bits per window to the exact observer at r2, about three times the r2–r1 learner gap.
>
> Affine probes recover the exact next-kind belief almost completely at the last layer (OIR 0.97–0.99). After one block, the fraction recovered falls monotonically with interface richness (seed-resolved), while the absolute information extracted stays flat at about 1.2 bits. [All learner results are at a training budget that later runs show to be under-converged; the converged re-run is reported in §X.]

---

## 2. Research questions

### RQ1 — Observability: where does the interface carry information about latent state, and how does context gate it?

- **Hypothesis.** Rung differences among r1–r4 are exactly zero at full context from reset. They are nonzero only under truncation or mid-episode windows. At the frozen law (40,8,2), every adjacent r1–r4 pair exceeds δ on the statutory query set at both ε, and immediate-agree/later-diverge history classes exist at every rung.
- **Falsification experiment.**
  - Compute exact ceilings at every rung and both ε at the frozen law and gate them with two computation paths. Any adjacent pair at or below δ would falsify the separation claim.
  - Check that r1–r4 posteriors are point masses at full context. A single non-point-mass posterior would falsify the injectivity claim.
  - Search for divergent classes. An empty class would falsify the second exit condition.
- **Status: answered on the canonical track. Partly answered on the corpus track.**
  - `exit-clause-canonical-ladder-distinct-40-8-2`: adjacent maxima at ε=1 are 0.0477 / 0.1100 / 0.0142 and at ε=½ are 0.0366 / 0.0523 / 0.0113. The lineage step's effect on lock owners is at most 0.0002 bits, not zero. Sources: docs/exit-clause-40-8-2-note-v0.1.md, docs/exit-clause-tables-40-8-2-2026-09-11.md.
  - `two-path-gate-8.5M-windows`: 8,542,940 posteriors. This cross-checks the recursion but not the kernel.
  - `full-context-injectivity` (corrected): theorem sketch on the structural quotient with σ = σ₀, r1–r4 only. The corrected-kernel support is the (12,12,2) control (86,134 windows, H exactly 0). The exhaustive checks on worlds A/B/C are owed a rerun.
  - `deliverable5-divergent-classes`: pair_prob < 1% at content rungs, yet 0.61–0.76 of law mass. Caveat: these figures are the δ_p = 0 corner with Δ_τ → 0+, i.e. upper bounds for Δ_τ = 0.01.
  - `ladder-collapse-was-from-reset` and `from-reset-vs-mid-episode-reversal` explain why the frozen law is mid-episode. That comparison is confounded, because the programs also changed.
  - Corpus track: `corpus-track-binding-and-ladder` gives H(S|Πw) 2.0965 → 1.5065 against canonical 0.6008 → 0.3898. These are thread-naming lower bounds only (v0.2.9 Clause 3 still owed).
  - The "synchronization/snapshot markers" part of the proposal's RQ1 is **owed**: TIME_CLASS is unbuilt and no snapshot mechanism exists. Recommend narrowing RQ1 explicitly.

### RQ2 — Learner vs. ceiling across interfaces: does a small transformer's excess over the exact ceiling follow the ceiling's ladder?

- **Hypothesis H3-learner (null form).** Excess over each rung's own corpus-track prefix ceiling at k = L−1 is flat or monotone in the same direction as the ceilings. The alternative observed so far is that it is non-monotone, with r2 worst.
- **Falsification experiment.**
  - Train r0–r4 × ε∈{1,½} at a converged budget with at least six seeds per cell. Report per-seed excess under the pattern-projection contract.
  - Add an entropy-matched irrelevant-field control (ctrl-irr, preserving P(field | EVENT_KIND)). If the r1+decoy cell pays the same learner cost as r2, then the r2 penalty is the cost of exposing *any* field, not the lock.
  - Compare against the exact value-of-information of the fields a rung adds.
- **Status: partly answered, and fragile.**
  - `ladder-eps1-six-seeds` and `learner-ladder-nonmonotone-2M` (corrected): at ε=1, d=128, 5 epochs, r2 = 0.086 ± 0.017 over 6 seeds (0.080, sd 0.006 without seed 3). r1 = 0.060 and r3 = 0.059, each over 3 seeds. The lowest r2 seed (0.074) is above the highest r1 seed (0.064) and the highest r3 seed (0.061).
  - `r4-two-basins`: r4 is a mixture (0.076 ± 0.030) and has no single place on the ladder.
  - `ladder-eps-half-mean-only`: at ε=½ the order holds only in the mean. min r2 exceeds max r3 by about 1e-4 on 3 r3 seeds, which is too thin to call separation.
  - `r0-on-ceiling`: positive control, 0.005 at 2M.
  - `owner-value-of-information`: I(next; owner) = 0.121 bits per window at r2 (identity share 0.0735; held/free 0.048). This is exactly 0 at r3/r4 by construction.
  - `object-exposure-cost-on-kind-actor` (weakened): OBJECT's own term carries about half (3 seeds) to two-thirds (5 non-outlier seeds) of the r2–r1 gap. The spillover onto ACTOR (about +0.004) is barely resolved, and the spillover onto KIND is not resolved.
  - `eps-half-costs-learner-more`: every content cell is worse at ε=½ in the mean, even though the ceilings are lower.
  - **Owed:** the converged-budget re-run, the decoy control and baselines (see §5).

### RQ3 — Belief geometry (the M5 slice): is the exact belief linearly accessible, at which layers, and does the interface order it?

- **Hypotheses.**
  - H1: activations align better with the exact belief than with implementation state.
  - H2: the model preserves posterior uncertainty rather than collapsing.
  - H-order: accessibility is ordered by interface.
- **Falsification experiments.**
  - H1: affine probes to the exact belief versus to an implementation-state target at matched probe capacity, on held-out windows. Implementation-state fits equal to or better than belief fits would falsify H1.
  - H2: calibration of probe-decoded beliefs on windows where the exact posterior is non-degenerate. Near-one-hot decodes on ambiguous windows would falsify H2.
  - H-order: per-layer OIR and absolute extracted bits with seed ranges.
- **Status: partly answered. H1 is untested.**
  - `belief-kind-linear-and-exposed` (corrected): at k=7, OIR is 0.77–0.84 at L1 and 0.97–0.99 at L4. Class-disjoint drops are 0.006–0.018 at L4 and up to 0.054 at L1. The chosen λ sits at the grid edge, so all OIRs are lower bounds.
  - `layer1-interface-ordering` (reframed): L1 OIR at k=7 is r1 0.834–0.843 > r2 0.810–0.817 > r3 0.799–0.801 > r4 0.772–0.787, and the ordering is seed-resolved. But absolute extraction H(Z̄) − CE is flat at about 1.2 bits. The ordering therefore means the first block does not take up the extra information richer rungs provide; it does not mean fields degrade integration. By L3 the rungs are level (0.938–0.943).
  - `repr-gap-grows-with-context`: at k=1, OIR ≥ 0.9997 (a boundary value, reported with KL_repr 0.0001–0.0002). All-seed k=7 ranges are wider than seed-1 ranges.
  - H2 partial: `identity-hedging-exact-kl` shows over-dispersion rather than collapse (r2 near-determined H̃ 0.076 / 0.074 / 0.151 against H* ≈ 0.025).
  - H1 **owed**: the probe target is next-kind predictive belief, not the hidden-state posterior vector of proposal §8.2.

### RQ4 — Context: how does learner excess move against a ceiling that falls with prefix length? (Supporting; fold into RQ2 if space is short.)

- **Hypothesis.** Excess grows with k while the ceiling falls from k=2 onward. The growth is rung-specific rather than generic.
- **Falsification experiment.** Per-k curves (k=1..7) across rungs, with r0 as a rung-agnostic control, repeated at the converged budget.
- **Status: answered descriptively, but the growth is largely generic.** `excess-grows-with-context` (corrected):
  - H* rises from k=1 to k=2 in every cell and falls on net afterwards.
  - Strictly increasing in all 27 content-rung 200k runs.
  - ×5–14 at 2M, not monotone in every run.
  - r0 grows by a similar factor, and growth depends on budget and width.
  
  I would state this as a property of the recipe, not a result about context. The proposal's cross-L context axis (32/128/512) is **not measured** in the learner: context enters only as k inside L=8.

*Out of cut, stated once in the introduction:* RQ3 (factorization/coupling, paper 2) and RQ4 (exposure/causal use, paper 3). Size scaling (M4) is used only as a budget control; see §5 item 3.

---

## 3. Section outline

| § | Section | Findings carried | The one thing it teaches |
|---|---|---|---|
| 1 | Introduction and positioning | (prior art); `exposure-gap-query-class` for one framing sentence only | Novelty is the conjunction: interface as a variable over a fixed generator, exact per-interface ceilings, a learner comparison against the ceiling the learner actually faces, all in a structured systems world. No one of these alone is a contribution (wind tunnels; Dalla Riva; Siems et al.; Ray/Riechers/Shai). |
| 2 | The instrument | `corpus-generator-windows-are-the-corpus`, `naming-bridge-lemma-and-withdrawn-table`, `window-process-enumerator`, `two-path-gate-8.5M-windows`, `frozen-law-40-8-2-choice`, `lineage-rung-cargo-allocator-not-matching` (label r4 as allocator-leaking lineage), `full-context-injectivity` (as a lemma), `eps-is-world-entropy-P2-inversion` (ε is scheduler randomness, not coverage) | Exact ceilings are exact for a stated observer. The canonical track (σ₀) and the corpus track (the pattern observer, which is what a learner on renamed corpora faces) differ by 3.5–3.9× in state entropy, and the paper compares the learner to the corpus track. |
| 3 | Exact observability | `exit-clause-canonical-ladder-distinct-40-8-2`, `r0-naming-step-beside-ladder`, `deliverable5-divergent-classes`, `corpus-track-binding-and-ladder`, `from-reset-vs-mid-episode-reversal` (one paragraph), `d8-c0b-allocator-eraser` (worked decomposition) | Interface value lives only where the window hides history. At the frozen law the content ladder yields four distinct regimes with a thin top rung. The actor field (r0→r1: 1.0769 bits max statutory gap, 7.5× the whole content range at ε=1) dominates, and it reflects attribution, not naming alone. The instrument can attribute a gap exactly to one named coordinate (C0b order erasure = 100% allocator REQ at full context and T_ep−L ≤ 3). |
| 4 | Learner vs. ceiling | `trainer-evaluator-design`, `naming-entropy-dominates-token-loss`, `headline-position-k-L-minus-1`, `r0-on-ceiling`, `ladder-eps1-six-seeds`, `learner-ladder-nonmonotone-2M`, `r4-two-basins`, `ladder-eps-half-mean-only`, `owner-value-of-information`, `object-exposure-cost-on-kind-actor`, `actor-field-carries-excess` (qualified), `held-lock-less-accessible-r2`, `eps-half-costs-learner-more`, `excess-grows-with-context` | The learner's ladder is not the ceiling's ladder. An exposed field can move the observer's ceiling by as much as the learner's whole shortfall, so cross-interface comparisons need the exact ceiling. (Contingent on the converged re-run and the decoy control.) |
| 5 | Belief geometry | `belief-kind-linear-and-exposed`, `layer1-interface-ordering` (with absolute bits), `repr-gap-grows-with-context`, `entity-ids-not-at-boundary-v01-withdrawn` (why the targets are coordinate-free), `identity-hedging-exact-kl` (as output-excess localization, not "exposure") | The first block extracts a fixed amount of next-kind information whatever the interface. Richer rungs' extra information is taken up only by later blocks. The final layer matches the output, which is expected because the logits read that layer affinely (a Q_logit point, not gap 3). |
| 6 | Limitations and threats | `direct-handoff-kernel-defect`, `audit-open-scope-limits`, `r4-two-basins`, `seed-spread-vs-resolution`, `size-axis-budget-not-rate` | Two-path agreement validates filtering relative to a shared kernel, not the kernel itself. The corpus track is a thread-naming lower bound. All learner numbers are conditional on the stated budget and seeds. |
| A | Appendices | `part2-thresholds-and-truncation-conditional`, `delta-sweep-empty-band`, `tv-sweep-delta-p-axis`, `heldout-tier1-confirmation`, `d8-p2-fail-generalization`, `d8-c1-cursor-and-wq`, `data-volume-divides-excess`, `size-axis-budget-not-rate`, `support-measurement-sampling-bias` (corrected table only), `d8-process-integrity`, `endpoint-pooling-bug-and-localization` | Thresholds were frozen before the looping world existed. The confirmatory record is mixed and reported (1 pass / 3 fail / 1 ill-posed). Deviations are disclosed. |

---

## 4. Cut list (findings kept in the notes only)

| Finding | Reason |
|---|---|
| `partition-identity-u-le-2`, `partition-identity-no-split` | Project-internal. At most a methods footnote (a structural zero, n₁ = n₄). |
| `q4-first-nonzero-full-context-ceiling` | Expected: the tower-property decomposition. The "float-identical" wording is false at the finest grain. |
| `geometry-over-content` | Expected. Some of the drop is clock entropy. Buggy-kernel figures. |
| `offset-is-function-of-state` | Project-internal. At most a footnote justifying L. |
| `ladder-collapse-synchronization` | Project-internal. Its generalization was superseded (it holds from reset only). |
| `r0-kind-only-rung` (C1 census) | Expected. Superseded by the r0 row at the frozen law. The permutation mechanism was withdrawn. |
| `lineage-rung-allocator-leakage` | Project-internal. Survives only as the r4 label in §2. |
| `ladder-is-query-specific` | Expected. Also contains a false "largest ceiling" claim. |
| `support-not-entropy` | Expected: Hartley versus Shannon entropy. |
| `rung-separation-is-geometry` | Project-internal. Buggy kernel, rerun pending, a 29.6% figure appears only in stdout. |
| `divergent-history-class` (C1 version) | Expected. Superseded by the version at the frozen law. |
| `observer-monotonicity-not-theorem` | Project-internal (elementary mixture fact). |
| `exposure-gap-query-class` | Paper 3. One framing sentence in §1. v0.2 (Wen et al.) is owed. |
| `divergent-grid-two-forces` | Expected. Its design value belongs to paper 3. |
| `d1-partB-collapse-horizons-frozen-delta`, `full-context-injectivity-d1-partA` | Project-internal. Superseded by the frozen law. The (b) "REFUTED" wording is itself superseded. |
| `sync-horizons-measure-b`, `f1-horizon-16`, `lineage-rung-informative-collapsed` | Expected or project-internal. From-reset horizons. |
| `w11-predictive-rung-kappa` | Project-internal. Only 10⁻⁸–10⁻⁶ of law mass. |
| `d10-lineage-witnesses-c0b` | Expected (redundancy under truncation). |
| `c1prime-live-ladder-range`, `c1prime-pilot-horizon-blocker` | Project-internal. Superseded by the frozen law. |
| `p3b-allocator-reappears-in-c1` | Project-internal (1.38e-4 bits, collapsed). |
| `d8-premise-v0.1-withdrawn`, `clock-dominance-withdrawn` | Withdrawn. |
| `stipulated-prior-phantom-gap2` | **Not supported.** The world-A residue was a buggy-kernel artifact. Do not cite it as justification for Part II §2(a). |
| `offset-term-structure` | Expected. The full-context half is zero by construction. |
| `window-process-interning`, `memory-refusal-and-exact-interning` | Project-internal (engineering). |
| `pc-and-cursor-role-channels` | Project-internal. Conditional contributions, not a decomposition. |
| `undertrained-diagnosis-withdrawn` | Withdrawn. |
| `r4-penalty-data-artifact` | Superseded by `r4-two-basins`. |
| `arithmetic-sensitivity-cpu-gpu` | Expected. Reproducibility footnote only. |
| `naming-and-endpoint-rules-learned` | Expected. One methods sentence, and only after the endpoint estimator is fixed (see §5). |
| `depth-of-formation-tracks-seed-quality` | Expected and weak: pooled ρ −0.65 falls to about −0.43 without three runs, positive within r3, and does not separate r4's basins at k=7. |
| `s18-owner-split-withdrawn` | Withdrawn. Keep as the worked example of the prefix-only rule in the notes. |
| `census-realization-noise-and-block` | Expected. It motivated the probes; that is not a result. |
| `probe-excess-link-posthoc` | Expected, and at risk: the subset is chosen by the outcome, the same pattern for which §18 was withdrawn. |
| `size-axis-not-read` | Superseded by `size-axis-budget-not-rate` (appendix). |

---

## 5. Readiness checklist (ordered by what blocks the most)

1. **Scope decisions by the project owner** (these block the section structure).
   - Headline: the interface ladder, with r0 reported beside it, rather than the identity axis. This settles the open question in contract §3.
   - Defer the D3 binding-split and lexical-split evaluation to M4 and record that decision; today it is recorded nowhere.
   - Size appears only as a budget control, not as an RQ5 claim.
   - Adopt the label "allocator-leaking lineage" for r4.
   - Record that the synchronization/snapshot part of RQ1/H5 is out of paper 1.
2. **Write exposure-gap note v0.2 before any model-versus-ceiling number leaves the repository.** This is the precondition from the literature check, and it is currently undischarged.
   - Cite Wen et al. 2609.11132.
   - State the sign and nesting conditions for G(Q).
   - Label every KL_repr / KL_out pair as a Q_logit (N=0) point.
3. **Converged-budget ladder re-run** (the core blocker for §4).
   - Wait for the running size follow-up: seeds 2–3 at 15 epochs for d=64/128/256, and d=256 at 45 epochs (commit a981d72). Use it to fix the training budget (and width) at which the ladder is measured.
   - Then re-train r0–r4 × ε∈{1,½} at that budget with at least 6 seeds per cell. r1 and r3 are at 3 seeds today.
   - Seed counts implied by the 5-epoch spreads for se ≤ δ/3 are 27 (r2) and 84 (r4). Re-derive these from the converged spreads before committing GPU time.
   - Report per-seed strip plots, not pooled means, for r4.
   - OTS-stamp ordering predictions before the run (confirmatory tests).
4. **ctrl-irr decoy (witness 4).**
   - Add an entropy-matched irrelevant field that preserves P(field | EVENT_KIND).
   - Verify an exact zero change on every ceiling.
   - Train r1+decoy (and optionally r2 with OBJECT replaced by the decoy) at the step-3 budget and seeds.
   - This is the only experiment that separates "the lock costs the learner" from "any exposed field costs the learner". It is also half of H3's falsifier.
5. **Baselines** (proposal §7.3). At minimum:
   - n-gram / fixed-order Markov excess per rung;
   - a GRU at matched parameter count on r1 and r2;
   - untrained-transformer activations as the probe control for every §5 OIR;
   - a shuffled-history control.
   None of these exist today.
6. **Ceiling normalization recompute.** The §2 "ceiling" column is a law-mass mean over k=7 tables whose total mass is 0.85, because T<8 windows are excluded. This was verified for r0: 0.999 → 1.176 bits (ε=1) and 0.938 → 1.104 bits (ε=½) on the continuing-window base.
   - Recompute all ten cells on the base the excess uses.
   - Fix every "% of the ceiling" statement.
   - Disclose that k=7 scoring conditions on continuation.
7. **Estimator fixes.**
   - Endpoint claim: use `end_total_bits` (0.001–0.0034 across the 200k sweep), not the per-k `end_bits`, which is one branch of the outcome, is selected by continuation, and can be negative.
   - Per-kind attributions: separate the KIND-field part, which is outcome-selected, from the chained fields.
   - Either redo §17.3 with a prefix-only weight P*(next on lock l) and exact KL, or drop it.
   - Extend the §19 exact-KL treatment to ACQUIRE and r1 before citing "§19 confirms §18's pooled rows".
8. **Belief-geometry completions.**
   - Extend the λ grid below 1e-6 and above 1e-2, since the optimum sits at the grid edge.
   - H1: add an implementation-state target (for example the realized full state tuple, or per-field pc/owner) at matched probe capacity, compared layer by layer against the exact posterior.
   - H2: calibration on windows where the posterior is non-degenerate.
   - Run r0 and ε=½ probes.
   - Run all seeds at k = 2..6, currently seed 1 only.
   - Report absolute extracted bits next to OIR.
   - Commit the raw data for the §16.1 bilinear control, which is currently uncommitted and not regenerable (diag2.py's p0 loop is empty).
9. **Corpus-track completion** (v0.2.9 Clause 3): lock, device and request naming for the (40,8,2) state and binding entropies (the learner's P* already uses Π_all); pattern forms for Q1/Q3/Q4/Q5; several distinct unseen tokens. Until these land, label every corpus-track number as a thread-naming lower bound.
10. **Exact-side reruns and fixes** that §2–§3 rely on.
    - Rerun the exhaustive injectivity checks (worlds A/B/C) on the corrected kernel.
    - Report divergent classes at (40,8,2) at Δ_τ = 0.01 along the full δ_p axis. Current figures are the δ_p = 0, Δ_τ → 0+ corner.
    - Land the statute erratum for Part II §3.2a (72 → 58 states).
    - Add a D8 C0b truthsayer pass, and correct note §3's "every L ≥ 2B / single-bucket only" statement.
    - Rerun rung-separation-geometry, or confirm that nothing in the paper cites it.
11. **M1 deliverable gaps.** Decide which ones paper 1 needs:
    - D6 hazard-audit status (needed so gap 2 does not absorb an expressivity term);
    - D7 consistency check;
    - witness executables 1/2/4/8/9/10;
    - shuffled gates on C0a/C0c.
12. **Literature.**
    - Read in full: 2512.22471, 2607.19379, 2607.17060, 2605.20824, 2602.14814, 2604.05469, 2609.11132, 2609.17376.
    - Confirm the D3 attribution to 2607.19379.
    - Differentiate explicitly from Ray/Riechers/Shai (nonergodic composition) on the interface axis.
    - Re-run the priority review immediately before submission.
13. **Figures.**
    - F1: exact ladder at (40,8,2), canonical and corpus tracks, with the r0 row beside.
    - F2: per-seed learner excess per rung, next to that rung's ceiling (both ε).
    - F3: per-k excess curves with r0 as control.
    - F4: layer × rung OIR with absolute bits.
    - F5: owner value-of-information decomposition (held versus identity), set against learner gaps.
    - F6: D8 C0b allocator attribution (chain, Shapley and envelope).
14. **Provenance and deviations appendix.**
    - The kernel defect and relabeling (d69fa87, 87ed0a7).
    - The Gate 6 deviation.
    - Commits a51613a and 94699fd.
    - Held-out Tier-1 score.
    - Endpoint pooling erratum.
    - The observer choice ("across rungs = r1–r4") as the researcher's decision, not statute.

---

## 6. Risks: where a reviewer attacks

- **"Everything here is expected."** Exact ceilings in finite worlds (wind tunnels), richer channels meaning less entropy (data processing), first-layer shallowness (Piotrowski et al.) are all known. *Defense:* only the conjunction together with the learner/ceiling mismatch is claimed. If the converged re-run flattens the learner ladder, the paper becomes a pure instrument paper and should say so.
- **Under-training.** Every learner number is at d=128, 5 epochs. §22.1 shows 15 epochs moves r1 seed 1 from 0.064 to 0.047. The ladder has already reshaped once, between 200k (monotone the other way) and 2M. It has never been measured at a converged budget. This is the most fragile point in the paper.
- **Seed spread and basins.**
  - r4 is a mixture (four seeds at 0.054–0.066; two high at 0.086 and 0.133).
  - r1 and r3 have only 3 seeds.
  - At ε=½ the separation holds in the mean only.
  - r2 versus r3 at ε=½ is separated by about 1e-4.
  - Whether the basins come from the rung or from the recipe is untested.
- **The r2 penalty may be "one more field to predict".** OBJECT's own term carries half to two-thirds of the r2–r1 gap. The "exposing the lock hurts who-acts" story is weakly resolved at best. Without the decoy (§5 item 4) a reviewer is entitled to this reading.
- **The layer-1 ordering is partly mechanical.** OIR's denominator grows with the rung while absolute extraction is flat. Present absolute bits, or the ordering will be read as an artifact.
- **Estimator bias.** Outcome-selected subsets (§17.3 at risk; §18 already withdrawn), the KIND-field per-kind attribution, the one-branch `end_bits`, and the 0.85-mass ceiling normalization.
- **Scope of the ceilings.**
  - The corpus track is a thread-naming lower bound.
  - The injectivity argument is a proof sketch on the structural quotient.
  - The two-path gate shares the kernel, as the direct-handoff defect demonstrated.
  - r3→r4 clears δ by only 1.13–1.42×; δ = 0.015 would collapse it.
  - Excluding r0 from the exit clause is a researcher's decision.
- **Missing controls and hypotheses.** No ctrl-irr, no baselines, no untrained-model probe control. H1 untested. H5's second clause untested (TIME_CLASS unbuilt). Context enters the learner only as k inside L=8. The model has 0.84M parameters, below the proposal's 1M–50M range.
- **Confirmatory record.**
  - Held-out Tier-1: 1 pass (on a wrong mechanism), 3 fail, 1 ill-posed.
  - δ was placed in a band observed after the sweep. The corrected band is (0.003728, 0.046568); the buggy-kernel band (0.003728, 0.049943) must not be quoted.
  - The honest framing is an exploration instrument with stamped provenance, not preregistered confirmation. The §5 item 3 re-run is the place to add real confirmatory tests.
- **Paper-3 creep.** "No gap 3 at L4" is near-tautological. The §17–§19 exposure-style analyses must be labelled as field-level output excess or Q_logit points, or moved out entirely.