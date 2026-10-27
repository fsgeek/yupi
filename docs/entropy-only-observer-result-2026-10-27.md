# What an entropy-only observer can see: result (2026-10-27)

> Declared in `entropy-only-observer-declared-2026-10-27.md` (stamped 815e138 before running). Script
> `scripts/entropy_only_observer.py`; numbers in `entropy-only-observer-2026-10-27.json`.

## Scores

| cell (k = 6) | AUC_H one | AUC_H two | BA_H one | BA_P one |
|---|---|---|---|---|
| r0 ε=1 | 0.474 | 0.396 | 1.000 | 1.000 |
| r0 ε=½ | 0.502 | 0.340 | 1.000 | 1.000 |
| r1 ε=1 | 0.613 | 0.352 | 0.995 | 1.000 |
| r1 ε=½ | 0.593 | 0.305 | 1.000 | 1.000 |
| r2 ε=1 | 0.617 | 0.365 | 0.994 | 1.000 |
| r2 ε=½ | 0.654 | 0.317 | 1.000 | 1.000 |
| r3 ε=1 | 0.644 | 0.387 | 0.994 | 1.000 |
| r3 ε=½ | 0.673 | 0.373 | 1.000 | 1.000 |
| r4 ε=1 | 0.630 | 0.380 | 0.994 | 1.000 |
| r4 ε=½ | 0.638 | 0.349 | 1.000 | 1.000 |

- **E1 failed (9/10).** At r0 ε = 1, entropy ranks hidden state *below* randomness (0.474).
- **E2 held.** The median one-step AUC_H is 0.62. A threshold on entropy barely separates randomness from hidden state
  of at least 0.1 bits, even with no learner error at all.
- **E3 and E4 failed (0/10), and they are uninformative.** BA_H is about 1.0 because exact entropy is a fingerprint:
  in r3 ε = 1, 4,383 distinct laws have 4,272 distinct entropies (to 1e-9). An observer with an infinitely precise
  entropy can look up the law. That was my measure-design error. It is the sixth observer artefact in this project,
  and the first of this steward's. No monitor reads entropy to nine digits.

## Not predicted

**At two steps, entropy reverses (AUC_H 0.31–0.40 in all 10 cells).** Over the next two KINDs, hidden-state windows
have *lower* joint entropy than pure-randomness windows. A threshold monitor that reads high entropy as "doesn't know"
would be wrong more often than right on the second question. The second question, which widens the full-distribution
margin about 8×, inverts the entropy signal. The mechanism is not checked. One candidate: hidden state that resolves
on record 7 makes record 8 nearly determined, while ε-randomness keeps spreading.

## What it points to

1. **For Arm B (real models):** the scalar the escape hatch exports ranks poorly at one step (0.47–0.67). It ranks
   backwards over a two-token horizon. Prediction to declare: on determined-but-open queries, per-token entropy flags
   them as unknowable. Multi-token entropy aggregates may behave differently from first-token entropy.
2. **The fair entropy observer** reads entropy at learner precision: binned at the error bound B, or as the learners'
   own output entropy H(Q) from the existing val/test dumps. That replaces BA_H. Declare before computing.
3. **The two-step reversal is the most interesting fact here.** It says that *which* scalar is exported matters as
   much as whether one is.
