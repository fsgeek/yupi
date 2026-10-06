# The three-arm intervention: pre-registration v0.3 (DRAFT, 2026-10-05)

> **Status: DRAFT, not stamped.** It supersedes the v0.2 draft (`docs/three-arm-prereg-v0.2.md`, rules 2.1), which
> three pre-stamp review rounds showed could not identify the mechanism ratio with these arms. **No confirmatory
> model (seeds 1–12) has been trained.** Everything in v0.2 §2 (models, corpus, seeds 1–12, recipe, GPU schedule)
> and §3 (statistics) stands. What changes is what is claimed.

## 1. Why v0.3: the ratio is not identified by these arms

v0.2's mechanism reading compared per-bit, self-copy-controlled gains: ρ' = decoy / relay. Round 3 (Claude)
showed this rests on an assumption the design cannot check. The self-copy's field has zero entropy, while the
relay's and the decoy's vary. Any cost or benefit of carrying a *variable* field that depends on the arm, and is
not information moved, lands in K'_R or K'_D and not in the control. Planted at ±0.0015, the size the severity run
itself uses, it gave wrong mechanism readings at 14–31 %. Readings conditioned on the P_R' gate are also biased
(selection on an overestimated relay gain). Fixing that would need a fourth field arm, *variable but
uninformative*, with its own exact side. That is a new study.

**What stays robust is direction.** A cost of field variability can only make the relay or the decoy look *worse*
against the zero-entropy self-copy. So "beats the self-copy where it moves information" is conservative under
exactly this confound. v0.3 confirms directions and reports the ratio descriptively.

## 2. Confirmatory claims (seeds 1–12, model-level one-sample t across seeds, one-sided, df 11)

| | claim | statistic | pass |
|---|---|---|---|
| **C1** | the relay's gain replicates on fresh data and models, against no field | K_R (r1 control) | t ≥ 3 |
| **C2** | the relay beats a zero-entropy field where it moves information | K'_R = K_R − KS_R | t ≥ 3 |
| **C3** | moving KIND information **without binding content** beats a zero-entropy field where it moves information | K'_D = K_D − KS_D | t ≥ 3 |

- **Each claim is scored independently.** At t ≥ 3 with df 11, the one-sided false-positive rate per claim is
  about 0.006 under a Gaussian null. The family of three is at most about 0.018.
- **If C3 passes:** moving information helps the learner *without* binding content, so H_move holds at least in
  part.
- **If C3 fails:** this is *not* evidence for H_bind. The test is conservative against the decoy, and a pure H_bind
  is not confirmable in this design.
- **If C2 fails while C1 passes:** the relay's gain over r1 is not distinguishable from carrying any field.

## 3. Descriptive (not scored, reported in full)

- ρ' with its bootstrap interval, and the v0.2 rules-2.1 reading, labelled descriptive, with the identification
  caveat of §1.
- Per-seed tables of K, KS, K' and F.
- The self-copy contrasts (t and TOST at ±0.002), and H_field (F, TOST at ±0.001).
- r1-baseline V summaries, for continuity with the relay verdict.

## 4. Severity for C1–C3 (PENDING, computed before stamping)

The C-family rates come from `scripts/three_arm_severity_v4.py` on v3's generative model. For each claim:
- the false-positive rate under its null, with the off-phase mixtures, arm-specific field effects δ of either sign
  on either arm's sets, and correlated off-phase across arms within a seed;
- the power at point and upper80 sds.

Bar: false-positive ≤ 0.05 in every scenario, including a positive arm-specific δ_D, which is C3's direct rival.
If a positive δ_D of plausible size breaks C3, the claim is restated, or C3 is demoted to descriptive.

## 5. Procedure

Unchanged from v0.2 §6: the scorer is frozen with this file, raws are committed unscored, a two-family recompute
precedes the verdict, and deviations go in a dated addendum.
