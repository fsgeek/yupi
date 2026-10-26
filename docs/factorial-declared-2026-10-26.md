# Prior × depth factorial: declared before running (2026-10-26)

> Owning instance. Codex 10-26, finding 6: the challenge had no two-step prior-aware arm, so substitution was not
> tested. This adds **PA2\*** (prior-aware, two steps; best β ∈ {1, 2} and c ∈ {1/16, 1/8, ¼} on val; threshold at 0.95
> val coverage) to the challenge's NL1, NL2 and PA1\* (the challenge's PA\*), with the same ten learners, the same
> fresh paired test windows and the same frozen-on-val protocol.

**Cells:** no prior / prior × one step / two steps = NL1, PA1\*, NL2, PA2\*. Metric: covered balanced accuracy at
frozen thresholds.

## Predictions

- **F1.** PA2\* ≥ PA1\* − 0.005 in at least 8 of 10. Adding the second step does not hurt a prior-aware observer once
  its noise scale is calibrated.
- **F2 (substitution).** PA2\* − max(PA1\*, NL2) ≤ 0.005 in at least 8 of 10: having both adds little over the better of
  the two.

If F2 fails (PA2\* clearly beats both), the prior and the second step are *complements*. That is a different and
arguably larger claim: the auditor should use both.
