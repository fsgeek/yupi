# What the observer's world knowledge is worth: declared before computing (2026-10-27)

> `scalar-vs-distribution-result-2026-10-27.md`: the full-distribution score M beats the entropy profile S3 by a
> median 0.059 AUC at two steps. But M knows every exact law of the world. This arm takes that knowledge away
> gradually.

**Observer with partial support.** The M2 observer of `scripts/scalar_vs_distribution.py` sees only a subset of the
two-step law groups. Within the subset it keeps each group's label (pure or withheld). Two ways to choose the subset,
each at fractions f ∈ {0.5, 0.25, 0.1, 0.05, 0.01} of the groups:
- **mass:** the f most massive groups, as an auditor who knows the common cases would have;
- **random:** a uniform-random f of the groups (seed 20261027), as an auditor with arbitrary knowledge would have.
Each subset keeps at least one pure and one withheld group. The learners, windows and AUC are as before (22
learners).

## Predictions

- **P1.** Mass, f = 0.1: AUC(M2) ≥ AUC(S3) in at least 20 of 22. Mass is concentrated, so the common laws suffice.
- **P2.** Random, f = 0.1: AUC(M2) < AUC(S3) in at least 12 of 22. Arbitrary partial knowledge is worth less than
  a world-free scalar.
- **Estimand:** for each mode, the smallest f at which the median AUC(M2) still exceeds the median AUC(S3). That is
  the crossover, the amount of world knowledge an export of the full distribution needs before it beats the entropy
  profile.

If P2 fails (random 10 % still beats the profile), the distribution's advantage is mostly the export, not the
knowledge. That would favour exporting distributions even to auditors who know little.
