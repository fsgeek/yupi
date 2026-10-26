# A tighter prospective floor from the error distribution: declared before computing (2026-10-26)

> Owning instance. Follows `prospective-certification-result-2026-10-25.md`: the lemma floor L was valid in 44 of 44
> pairs but loose (two-step median gap 0.55), because it assumed every window's error equals the quantile bound B.

**Floor L2 (still worst-case in direction, no longer in size).**
- A pure window with error e is certified surely if e ≤ B and μ_c − e > B, that is if e < min(B, μ_c − B).
- With e drawn from the learner's val error distribution, independently of class:
  L2 = Σ_c m_c · P_val(e < min(B, μ_c − B)) / Σ_c m_c, summed over pure classes c with exact masses (RESET halved).
- Same 44 pairs and the same B (q = 0.95) as before.

## Predictions

- **V1 (still a floor).** Observed ≥ L2 − 0.03 in at least 42 of 44 pairs.
- **V2 (tighter).** The two-step median of (observed − L2) is ≤ 0.30, against 0.55 for L.
- **V3 (rank).** Within each step, Spearman(L2, observed) ≥ that of L (0.91 one step, 0.87 two).

**If V1 and V2 hold:** most of the floor's looseness was the size assumption, not direction. If V2 fails: direction
(whether errors point toward or away from withheld laws) carries the gap, and ledger item 3 is the next experiment.
