# Certification margin across interfaces: declared before computing (2026-10-22)

> Owning instance. EXPLORATORY, exact side only, from the pinned split-v2 rows (r0–r4, both ε, position 7, KIND).
> Follows `certification-margin-result-2026-10-22.md`.

**Quantity.** For a pure class c (G < 1e-12, H\* > 1e-12) and a threshold γ: μ_c(γ) = TV from P_c to the nearest exact
law in the same table whose class-mass-weighted G is at least γ. Reported per (interface, ε): the pure-mass-weighted
median and 10th percentile of μ(γ), and the pure mass share with μ(γ) ≥ 0.02, for γ ∈ {0.01, 0.03, 0.1, 0.3}.
r0 is reported but not scored: it shows only KIND, so it has a different law set.

**Predictions (r1 → r4, both ε).**
- **I1.** For every γ, the median μ(γ) is non-decreasing from r1 to r4. Richer interfaces withhold less, so fewer
  substantially withheld laws sit near the pure ones.
- **I2.** At every interface, the median μ(γ) is non-decreasing in γ. This follows by construction (the neighbour set
  shrinks) and is a check, not a test.
- **I3.** At γ = 0.1 the median μ is between 0.01 and 0.02 on every interface r1–r4 at both ε. This extrapolates the
  ≈ 0.015 seen at r1 and r3.

**Why it matters.** If I1 holds, the observation interface controls not only how much is knowable (v3 §3) but whether
randomness can be *certified* at a given learner precision. If it fails, certifiability is not monotone in telemetry
richness. That would be the more surprising result.
