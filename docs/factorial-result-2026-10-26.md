# Prior × depth factorial: result (2026-10-26)

> Owning instance. Scores `factorial-declared-2026-10-26.md` (stamped at e606a34 before running). Script:
> `scripts/challenge_score.py` (PA2\* arm added). Raw: `factorial-2026-10-26.json`. NL1, PA1\* and NL2 reproduce the
> 10-25 challenge exactly.

| learner | NL1 | PA1\* | NL2 | PA2\* | PA2\* − max(PA1\*, NL2) |
|---|---|---|---|---|---|
| d128, 45 epochs | 0.990 | 0.997 | 0.998 | 0.998 | −0.000 |
| d128, 5 epochs | 0.990 | 0.994 | 0.994 | 0.994 | −0.000 |
| d256, 45 epochs | 0.979 | 0.998 | 0.997 | 0.999 | +0.000 |
| d128, lr 3e-4 | 0.983 | 0.992 | 0.994 | 0.994 | +0.000 |
| d256, 15 epochs | 0.980 | 0.995 | 0.997 | 0.999 | +0.001 |
| d64, 15 epochs | 0.976 | 0.993 | 0.992 | 0.994 | +0.001 |
| GRU 256×2 | 0.956 | 0.993 | 0.991 | 0.995 | +0.002 |
| d64, 5 epochs | 0.956 | 0.985 | 0.982 | 0.985 | −0.000 |
| d64, lr 3e-4 | 0.915 | 0.978 | 0.968 | 0.978 | +0.000 |
| d256, lr 1e-4 | 0.887 | 0.945 | 0.932 | 0.965 | **+0.020** |

(Covered balanced accuracy at 0.95 val coverage, on 8,836 fresh paired test windows.)

## Predictions

- **F1 (PA2\* ≥ PA1\* − 0.005 in ≥ 8 of 10): holds, 10 of 10.**
- **F2 (PA2\* − max(PA1\*, NL2) ≤ 0.005 in ≥ 8 of 10): holds, 9 of 10.** The exception is the worst learner, at +0.020.

## Reading

- **In the average case, a prior and a second question are substitutes.** Either one gets a nearest-law observer to
  about the same place, and having both adds at most 0.002 over the better of the two, except for the worst learner.
- **For the worst learner they are complements** (+0.020). The pattern is consistent with the learner-quality trend:
  the worse the learner, the more each kind of extra information is worth. It is one learner, though, so this is an
  observation, not a finding.
- **For an auditor without a prior** (the practical case), the second question recovers what the prior would have
  given, for every learner but the worst.
