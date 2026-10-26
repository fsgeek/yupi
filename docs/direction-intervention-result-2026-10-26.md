# Matched-error direction intervention: result (2026-10-26)

> Owning instance. Scores `direction-intervention-declared-2026-10-26.md` (stamped at bd767d5 before running). Script:
> `scripts/direction_intervention.py`. Raw: `direction-intervention-2026-10-26.json`. 22 models, pure-truth windows.
> The real arm reproduces `certified_bound.py` exactly.

## Predictions (two steps, q = 0.95)

- **I1 (real − adversarial ≥ 0.10 in ≥ 18 of 22): holds, exactly 18.** The four exceptions are r3 ε = 1 seeds 1 and 3
  (0.087, 0.077), where adversarial errors still certify well because the two-step margin is wide, and the two worst
  learners (0.012, 0.025), where almost nothing certifies.
- **I2 (|real − random| ≤ 0.05 in ≥ 16 of 22): fails, 11 of 22.** In a consistent direction: **real < random in 19 of
  22.** On the certification scale, real errors sit a median **0.18** of the way from a random direction toward the
  adversarial one (range −0.74 to 0.33 over the 20 models where random and adversarial differ by more than 0.05).
- **I3 (adversarial within 0.05 of the L3 predictor in ≥ 16 of 22): holds, 22 of 22.** The predictor is validated as a
  worst-direction model.

## Reading

- **The excess of certification over the predictor is identified, mostly, as errors being far from worst-case**
  (I1, I3). The predictor is exactly as pessimistic as an adversarial learner.
- **But real errors are not random either. They lean toward hidden state relative to chance:** modestly (about a
  fifth of the way to adversarial), and consistently (19 of 22).
  - This **revises ledger F11.** The cosine test there (W2) found no hidden-state-*specific* lean. The reviewer had
    noted that a Euclidean cosine toward one neighbour does not test certificate-boundary crossing.
  - Measured where it matters, at the certificate boundary, the lean is there.
- **Strongest at one step at r3 ε = 1** (post hoc, from the raw): real 0.264 / 0.178 against random 0.608 / 0.628 for
  seeds 1 and 3. Seed 2, the precise one, is at par (0.745 against 0.754).
- **Caveat:** the random baseline is Dirichlet(1) directions, which is one choice. A baseline drawn from other learners'
  error directions would be a fairer null and should be tried before this is called a bias.

**For PACMI:** "models over-attribute their uncertainty to what they cannot see" has measured support in a weak form.
Relative to chance, learners' errors on genuinely random events lean toward looking like hidden state, by about a fifth
of the way to the worst case. That costs an auditor certificates.
