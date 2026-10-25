# Observer vs learner across real quality differences: declared before test (2026-10-25)

> Owning instance. Decides whether the ledger's pattern B ("the observer dominates the observed") survives learners
> that genuinely differ, or was an artefact of comparing near-identical seeds (`observer-space-result-2026-10-24.md`).
> Ten learners on one corpus (r1, ε = 1, corpus fd5da4c31e43d73d; hashes in
> `learner-quality-ladder-checkpoints-2026-10-25.json`).
>
> Val was used only for quality, τ and η. No monitor was scored on val. Settings are as frozen in
> `learner-two-step-declared-2026-10-23.md`: 10,000 test windows per learner, the same seed, memory caps.

## Quality on val (2,000 windows; mean TV to the exact law)

| learner | one step | two steps |
|---|---|---|
| d128, 45 epochs | 0.023 | 0.049 |
| d128, 5 epochs | 0.026 | 0.057 |
| d256, 45 epochs | 0.029 | 0.061 |
| d128, lr 3e-4 | 0.030 | 0.067 |
| d256, 15 epochs | 0.031 | 0.063 |
| d64, 15 epochs | 0.033 | 0.068 |
| GRU 256×2 | 0.040 | 0.081 |
| d64, 5 epochs | 0.042 | 0.090 |
| d64, lr 3e-4 | 0.061 | 0.133 |
| d256, lr 1e-4 | 0.077 | 0.124 |

Spread: 3.4× at one step, 2.7× at two steps. For comparison, the earlier 3-seed comparison spread about 1.3×.

## The test

- **Observers:** the 12 *reasonable* observers of the 10-24 grid (β ∈ {½, 1, 2}, c ∈ {¼, ½}, one or two steps).
- **Metric:** conservative balanced accuracy.
- **Observer range:** max − min over the 12, within a learner, averaged over learners.
- **Learner range:** max − min over the 10 learners, at a fixed observer, averaged over observers.
- **R** = observer range ÷ learner range.

**Decision rule:**
- R ≥ 2: the observer dominates. Pattern B survives real quality differences.
- R ≤ ½: the learner dominates. Pattern B was a fixed-quality effect.
- Otherwise: comparable.

**Owner's lean, recorded so it can be wrong:** R < 1.

## Predictions

- **Q1.** R < 1.
- **Q2.** The overall-best observer of 10-24 (one step, c = ¼, β = 2) is best, or within 0.01 of best, for at least 8
  of 10 learners. Observer rankings are stable across quality.
- **Q3.** For prior-free observers (β = 0, best c), the gain from the second step shrinks as two-step error grows:
  Spearman(gain, val two-step mean TV) < 0 across the 10 learners.
- **Q4.** The best observer's accuracy tracks quality: Spearman(best accuracy, val one-step mean TV) ≤ −0.6.
