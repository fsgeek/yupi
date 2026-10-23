# Prior-aware kind monitor: declared before any run (2026-10-23)

> Owning instance. EXPLORATORY with declared predictions. Follows the correction in
> `certification-margin-interfaces-result-2026-10-22.md`: both earlier monitors were mass-blind, while the
> mass-weighted look-alike statistic read "readable". This monitor uses the prior, as a Bayes observer would.

**The observer sees:** the cell's exact family (laws, masses, splits) and one model output q. That is the same
restriction as before.

**Noise model (an assumption, stated):** L(q | g) ∝ exp(−TV(q, P_g) / τ). The scale τ is fitted per model as the mean
TV between the model's output and the true law on that model's **val** split. It is never fitted on test.

**Decision.** Over law groups g with kind pure (G < 1e-12, H\* > 1e-12) or withheld (G ≥ 0.1, class-mass-weighted):
π_pure(q) = Σ_{g pure} W_g L(q|g) / Σ_{g pure or withheld} W_g L(q|g).
- If π_pure ≥ 0.9, predict pure.
- If π_pure ≤ 0.1, predict withheld.
- Otherwise, abstain.

No-kind and deterministic groups are excluded from both sums. Their windows are reported, and they are not in the
headline.

**Scored on test**, with the same headline population and metrics as `kind-classifier-declared-2026-10-22.md`:
coverage; covered and conservative balanced accuracy; recalls. Sensitivity: τ × {0.5, 2}; the headline is τ × 1.

**Predictions (12 models, τ × 1).**
- **A1.** Covered balanced accuracy ≥ 0.90 and coverage ≥ 0.80 in at least 10 of 12 models.
- **A2.** Pure recall (covered) ≥ 0.85 in at least 10 of 12 models, the side the mass-blind monitors lost.
- **A3.** Its conservative balanced accuracy exceeds the post hoc mass-blind monitor's (m = 0.005) in at least 10 of 12
  models.

**If A1–A3 hold:** the kind is operationally recoverable from these learners' outputs by a prior-aware observer. The
earlier "cannot certify" came from ignoring the prior. **If they fail:** the asymmetry is real for Bayes observers too.
