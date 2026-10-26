# Class-conditional prospective floor: result (2026-10-26)

> Owning instance. Scores `prospective-certification-v3-declared-2026-10-26.md` (stamped at 27d89ee before computing).
> Script: `scripts/prospective_certification_v3.py`. Raw: `prospective-certification-v3-2026-10-26.json`. Its output
> field `L2` holds L3.

## Predictions

- **X1 (floor valid, ≥ 42 of 44): holds, 44 of 44.**
- **X2 (two-step median gap ≤ 0.15): fails, 0.213** (L2: 0.246; L: 0.553). The rank agreement at two steps is 0.94.
- **X3 (one-step median gap ≤ 0.015): holds, 0.011.**

## The floor's looseness, decomposed (two steps, median gap). *Descriptive, not causal (Codex 10-26): differences of medians do not identify contributions.*

| floor | assumption dropped | gap |
|---|---|---|
| L | none (every error = B, worst direction) | 0.553 |
| L2 | size: actual val error distribution | 0.246 |
| L3 | class-dependence: pure-window errors | 0.213 |
| (the rest) | **direction:** errors pointing straight at the nearest hidden-state law | about 0.21 |

## Reading

- **The last ~0.21 is the worst-case-direction assumption,** and the error-direction result says why it is loose.
  Errors do not systematically point at hidden-state alternatives (W2 failed, 13 of 22). Most errors miss the one
  direction that would spoil a certificate.
- **So the gap comes from non-adversarial errors, not from a bias toward hidden state.**
- **For an auditor this is the right side to be wrong on:** the guaranteed floor is conservative exactly because it
  refuses to assume the learner's errors are benign.
- A floor that used the learner's actual error *direction* would no longer be a guarantee. It would be an estimate. The
  guarantee/estimate line runs here.
