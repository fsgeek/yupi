# What an entropy-only observer can see: result (2026-10-27)

> Declared in `entropy-only-observer-declared-2026-10-27.md` (stamped 815e138 before running). Script
> `scripts/entropy_only_observer.py`; numbers in `entropy-only-observer-2026-10-27.json`.
>
> **Correction, same day.** The first version of this result (commit a120b58) was produced by a bug. The AUC
> denominator used sorted weights with unsorted labels. A brute-force check found it (the old code gave 1.009 for a
> perfect ranking). Its headline claims are withdrawn: "median AUC 0.62" and "entropy reverses at two steps in
> 10/10". The numbers below are from the fixed code, which matches brute force to 1e-15 and gives exactly 1.0 and 0.0
> for perfect and inverted rankings.

## Scores

| cell (k = 6) | AUC_H one | AUC_H two | BA_H one | BA_P one |
|---|---|---|---|---|
| r0 ε=1 | 0.919 | 0.652 | 1.000 | 1.000 |
| r0 ε=½ | 0.910 | 0.620 | 1.000 | 1.000 |
| r1 ε=1 | 0.903 | 0.530 | 0.995 | 1.000 |
| r1 ε=½ | 0.894 | 0.446 | 1.000 | 1.000 |
| r2 ε=1 | 0.875 | 0.510 | 0.994 | 1.000 |
| r2 ε=½ | 0.872 | 0.438 | 1.000 | 1.000 |
| r3 ε=1 | 0.876 | 0.518 | 0.994 | 1.000 |
| r3 ε=½ | 0.875 | 0.467 | 1.000 | 1.000 |
| r4 ε=1 | 0.876 | 0.518 | 0.994 | 1.000 |
| r4 ε=½ | 0.875 | 0.467 | 1.000 | 1.000 |

- **E1 held (10/10).** At one step, hidden state raises entropy on average in every cell.
- **E2 failed.** The median one-step AUC_H is 0.876, above the declared 0.85. A threshold on next-KIND entropy
  separates randomness from substantial hidden state fairly well in this world. The richer interfaces separate
  slightly worse (0.92 at r0, 0.87–0.88 at r2–r4).
- **E3 and E4 failed (0/10), and they are uninformative.** BA_H is about 1.0 because exact entropy is a fingerprint:
  in r3 ε = 1, 4,383 distinct laws have 4,272 distinct entropies (to 1e-9). An observer with infinitely precise
  entropy can look up the law. That was my measure-design error. No monitor reads entropy to nine digits.

## Not predicted

**Entropy over the next two KINDs loses the signal (AUC_H 0.44–0.65; below 0.5 in 4 of 10 cells).** The second
question widens the full-distribution margin about 8×, but it washes out the joint-entropy signal. The mechanism is
not checked. One candidate: the second record's conditional entropy is dominated by ε-randomness, which is common to
both classes and swamps the hidden-state contribution.

## What it points to

1. **A scalar summary is not neutral to query depth.** The extra query that helps an observer who sees the whole
   distribution erases most of what a joint-entropy observer could see. For Arm B, that suggests a testable contrast
   on real models. Per-token entropy at the first answer token may separate the two cases. Sequence-level entropy
   aggregates may not.
2. **The one-step AUC (0.87–0.92) does not test the "name a fruit" worry.** Yupana's randomness comes from a few
   sources (scheduler ε, device completion). In this world, high randomness entropy is rare relative to hidden-state
   entropy. Whether that holds for LLM queries with many correct answers is exactly what Arm B measures. The closeness
   to ai-honesty's pooled 0.870 is a coincidence of numbers, not evidence.
3. **The fair entropy observer** reads entropy at learner precision: binned at the error bound B, or as the learners'
   own output entropy H(Q) from the existing val/test dumps. That replaces BA_H.
