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

---

## Correction (2026-10-23, the morning after): the reading above is an artefact of an existential statistic

The predictions are scored as declared, and those verdicts stand. **The reading ("content interfaces barely move the
margin"; "observe more does not work") is wrong.** It came from chasing the r0 oddity, at Tony's prompt.

μ(γ) as defined takes the nearest substantially withheld law of *any* mass. At r1–r4 that neighbour carries essentially
zero prior mass (it prints as 0.00000). Richer interfaces split histories into many rare classes: 5,864–23,603 laws with
G ≥ 0.1, against 1,515–1,648 at r0. One rare class near the coin is enough to set the margin. v3 §4.3 warned of this
("existential statistics: one rare neighbour suffices"), and this result did not apply the warning.

The coin's μ(0.1) when the neighbour must carry at least a given share of law mass:

| floor | 0 | 1e-6 | 1e-5 | 1e-4 | 1e-3 |
|---|---|---|---|---|---|
| r0, ε = 1 | 0.0268 | 0.0268 | 0.0268 | 0.0268 | 0.0268 |
| r1–r4, ε = 1 | 0.0153 | 0.0153 | 0.0233 | 0.108–0.152 | 0.310–0.667 |
| r0, ε = ½ | 0.0274 | 0.0274 | 0.0274 | 0.0284 | 0.0524 |
| r1–r4, ε = ½ | 0.0143–0.0151 | same | 0.0143–0.0172 | 0.160–0.205 | 0.517–0.667 |

**What this shows.**
- At any floor of 1e-4 or more, the content interfaces widen the coin's margin four- to sevenfold over r0.
- The coarse interface's neighbours of the coin are *heavy* mixtures. The rich interfaces' near neighbours are rare.
- So richer telemetry does make the dominant randomness more certifiable, *for an observer that weights by prior mass*,
  and makes it look less certifiable to one that does not.
- The floor is arbitrary, so the table is a curve, not a number. The object that removes the arbitrariness is a
  prior-aware monitor: one that weighs neighbours by mass, not by existence.

**Consequences.**
1. The operational kind monitor (nearest law, mass ignored except to break ties) and its post hoc variant are both
   mass-blind. The §4.3 look-alike statistic, which *is* mass-weighted, read "readable". The two disagree, and this is
   probably why. The next monitor to declare is prior-aware: the posterior over law groups given q, under a stated
   noise model for q.
2. The two-step query experiment should report mass-aware margins from the start.
