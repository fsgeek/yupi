# Do learners err toward hidden state? Result (2026-10-26)

> Owning instance. Scores `error-direction-declared-2026-10-26.md` (stamped at e259536 before computing). Script:
> `scripts/error_direction.py`. Raw: `error-direction-2026-10-26.json`. 22 models, k = 6 test, pure-truth windows.

## Predictions

- **W1 (two steps, mean cos_W > 0 in ≥ 18 of 22): holds, exactly 18.** The negative models are r1 ε = ½ seeds 1 and 3,
  r3 ε = 1 seed 2, and r3 ε = ½ seed 1. Means are small: −0.06 to +0.21, typically about +0.1.
- **W2 (two steps, cos_W > cos_P in ≥ 18 of 22): fails, 13 of 22.** Errors do not point at hidden-state alternatives
  more than at other nearby pure laws.
- **W3 (one step, cos_W > 0 in ≥ 18 of 22): fails, 15 of 22.** At one step the sign varies by model, even between
  seeds (r3 ε = 1: +0.22, −0.57, +0.37). cos_W and cos_P are close at one step for most models, because the nearest
  withheld and nearest pure neighbours of the coin lie in similar directions.

## Reading

- **The PACMI-shaped hypothesis ("models over-attribute their uncertainty to what they cannot see") is not supported in
  this world.** *Correction 10-26 (Codex): this means a specific hidden-state bias is not established, not that it is absent. Euclidean cosine toward one neighbour is not a certificate-boundary test.* At two steps there is a weak lean toward mixtures, consistent with hedging. It is not specific to
  hidden state, and at one step the direction is idiosyncratic per model.
- **So direction does not explain the remaining floor gap. What does (post hoc, val):** learners are *more precise on
  pure-randomness windows*. The median two-step val error on pure windows is 0.029–0.069, against 0.037–0.109 over all
  windows (smaller in 20 of 22 models; ratio median 0.84). The L2 floor drew errors independently of class, from the
  all-window distribution, and so underestimated certification.
- **Points to:** a class-conditional floor (pure-window val errors). It is still computable before any monitor runs,
  because val labels come from the exact tables, so it remains prospective. To be declared and scored as such.
