# Fairer null for the direction lean: result (2026-10-26)

> Owning instance. Scores `direction-null-declared-2026-10-26.md` (stamped at 5771ec4 before running). Raw:
> `direction-null-family-2026-10-26.json` (`scripts/direction_intervention.py --null family`). The real and adversarial
> arms are identical to the 10-26 intervention.

## Predictions (two steps)

- **N1 (family-random < Dirichlet-random in ≥ 18 of 22): holds, 20 of 22.** The Dirichlet null was biased toward
  "safe" outputs, as suspected.
- **N2 (real < family-random in ≥ 14 of 22): fails, 12 of 22.** The median of real − family-random is −0.002. On the
  certification scale, the median lean toward adversarial is **0.02**, against 0.18 under the Dirichlet null.

## Reading

- **The "lean toward hidden state" in `direction-intervention-result-2026-10-26.md` was an artefact of the Dirichlet
  baseline.** Against a null that moves toward random laws the world actually produces (weighted by prior mass),
  learners' errors are indistinguishable from chance on the certificate boundary. **The 10-26 F11 revision is
  withdrawn.**
- **What remains identified:**
  - the worst-direction predictor equals adversarial errors (I3, 22 of 22);
  - real errors certify far more than adversarial ones (I1, 18 of 22);
  - real errors behave like random moves toward the world's own laws (this result).
- **The story this points to:** learners' errors are *world-shaped but not hidden-state-biased*. That is why
  certification beats the worst-case predictor: not because errors are benign by design, but because the world's laws
  mostly do not lie in the one direction that would spoil a certificate.
- **On the instruments:** two nulls gave opposite answers, and the bias of the first was predictable from how it was
  built. The null has to know the world's structure. That is pattern B (the observer is part of the measurement)
  again, this time in the baseline.
