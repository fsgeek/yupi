# Certification margin across interfaces: result (2026-10-22)

> Owning instance. Scores `certification-margin-interfaces-declared-2026-10-22.md`. Script:
> `scripts/certification_margin_interfaces.py`. Raw: `certification-margin-interfaces-40-8-2-k7-2026-10-22.json`.

## Medians of μ(γ), pure-mass-weighted (r1 / r2 / r3 / r4)

| γ | ε = 1 | ε = ½ |
|---|---|---|
| 0.01 | 0.0009 / 0.0027 / 0.0027 / 0.0027 | 0.0010 / 0.0010 / 0.0010 / 0.0010 |
| 0.03 | 0.0030 / 0.0036 / 0.0036 / 0.0036 | 0.0038 / 0.0034 / 0.0034 / 0.0034 |
| 0.1 | 0.0153 at every interface | 0.0143 / 0.0151 / 0.0151 / 0.0151 |
| 0.3 | 0.0654 at every interface | 0.0555 at every interface |

r0 (KIND only, not scored): 0.0023 / 0.0049 / 0.0268 / 0.0586 at ε = 1, and 0.0039 / 0.0039 / 0.0274 / 0.0641 at ε = ½.

**Caveat on what these summarise.** The 10th percentile equals the median almost everywhere. The device coin carries
86–95 % of the pure mass (§4.2), so these statistics mostly describe the coin's neighbourhood, not pure randomness in
general.

## Predictions

- **I1 (non-decreasing r1 → r4, every γ, both ε): fails.** At ε = ½, γ = 0.03, the median falls from 0.0038 (r1) to
  0.0034 (r2). Every other series is non-decreasing, and most are flat.
- **I2 (non-decreasing in γ): holds.** It is a check by construction.
- **I3 (γ = 0.1 median within [0.01, 0.02] on r1–r4, both ε): holds,** at 0.0143–0.0153.

## Reading

The content interfaces barely move the margin. From r1 to r4, μ(0.1) and μ(0.3) are constant, or move by 0.0008, at
both ε. Showing more fields of each record makes more *knowable* (v3 §3: the withheld term falls from about half to
about a third). It does not make the dominant randomness more *certifiable*. The coin's nearest substantially withheld
neighbour sits at the same distance whatever the observer sees.

The coarsest interface, r0, has the *widest* margins at γ ≥ 0.1 (0.027 against 0.015). This is not scored, and it is
not explained yet. One candidate: with fewer distinguishable classes, fewer mixture laws exist near the coin. That is
not checked.

Of the two levers proposed for widening μ(γ), "observe more" does not work here, for this world's dominant mechanism.
"Ask more" (two-step queries) is the one left. That makes it the next experiment, and a sharper one: richer telemetry
fails to separate randomness from withheld state, so can a richer *query* do it?
