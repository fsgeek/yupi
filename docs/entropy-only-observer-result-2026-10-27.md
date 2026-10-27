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

### Why (post hoc, same day; not declared)

Split the joint entropy as H(K7, K8) = H(K7) + H(K8 | K7). In all 10 cells:

| cell | AUC H(K7) | AUC H(K8 \| K7) | mean H(K8\|K7) pure / withheld | P(K8 = DISPATCH) pure / withheld | AUC H(K7) − H(K8\|K7) |
|---|---|---|---|---|---|
| r0 ε=1 | 0.919 | 0.172 | 1.24 / 0.68 | 0.41 / 0.69 | 0.927 |
| r1 ε=½ | 0.894 | 0.146 | 1.14 / 0.53 | 0.40 / 0.72 | 0.947 |
| r3 ε=1 | 0.876 | 0.196 | 1.08 / 0.55 | 0.45 / 0.74 | 0.936 |
| all 10 | 0.872–0.919 | 0.146–0.216 | withheld about half of pure | 0.40–0.45 / 0.68–0.74 | 0.913–0.947 |

- **The candidate mechanism in the first draft of this section was wrong.** The second step does not carry noise
  common to both classes. It carries a strong signal **in the opposite direction**. After a hidden-state window's
  next event, the one after it is usually a DISPATCH (about 0.7) and nearly determined. After a pure window, it is
  spread out.
- **The joint entropy adds two strong signals of opposite sign, and they cancel.** Kept apart and differenced, the
  per-step entropies separate better than one step does (0.91–0.95 against 0.87–0.92).
- **Signature in this world:** hidden state looks like uncertainty that *resolves*. The entropy is high now and low
  next. Randomness looks like uncertainty that *persists*.

## What it points to

1. **What is exported matters as much as whether something is.** A summed (sequence-level) entropy cancels the
   signal. The per-step *profile* of entropy carries more than any single step. For Arm B, the question for real
   models is whether fabrication and open-ended answers have different entropy *trajectories*. A caution before
   declaring anything: "name a fruit" may also resolve after its first token, so the Yupana signature need not
   transfer. That is a prediction to state with care, not to assume.
2. **The one-step AUC (0.87–0.92) does not test the "name a fruit" worry.** Yupana's randomness comes from a few
   sources (scheduler ε, device completion). In this world, high randomness entropy is rare relative to hidden-state
   entropy. Whether that holds for LLM queries with many correct answers is exactly what Arm B measures. The closeness
   to ai-honesty's pooled 0.870 is a coincidence of numbers, not evidence.
3. **The fair entropy observer** reads entropy at learner precision: binned at the error bound B, or as the learners'
   own output entropy H(Q) from the existing val/test dumps. That replaces BA_H.
