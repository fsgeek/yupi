# Observer vs learner across real quality differences: result (2026-10-25)

> Owning instance. Scores `learner-quality-declared-2026-10-25.md` (stamped at 169930a before test). Raw:
> `learner-quality-scores-r1-eps1-k6-2026-10-25.json` (scorer) and `learner-quality-observer-grid-2026-10-25.json`
> (32 observers × 10 learners). 10,000 test windows per learner. Learners are ordered by val one-step mean TV.

## R and the decision rule

The observer range (12 reasonable observers, within a learner, averaged) is **0.067**. The learner range (10 learners,
at a fixed observer, averaged) is **0.092**. **R = 0.73: comparable** (½ < R < 2).

## Per learner (conservative balanced accuracy)

| learner (val one-step mean TV) | best observer | worst reasonable | prior-free, one step → two steps |
|---|---|---|---|
| d128, 45 epochs (0.023) | 0.981 | 0.940 | 0.943 → 0.966 |
| d128, 5 epochs (0.026) | 0.981 | 0.940 | 0.942 → 0.965 |
| d256, 45 epochs (0.029) | 0.980 | 0.931 | 0.901 → 0.956 |
| d128, lr 3e-4 (0.030) | 0.969 | 0.934 | 0.899 → 0.961 |
| d256, 15 epochs (0.031) | 0.971 | 0.898 | 0.741 → 0.946 |
| d64, 15 epochs (0.033) | 0.966 | 0.906 | 0.795 → 0.942 |
| GRU 256×2 (0.040) | 0.954 | 0.894 | 0.735 → 0.924 |
| d64, 5 epochs (0.042) | 0.962 | 0.912 | 0.774 → 0.943 |
| d64, lr 3e-4 (0.061) | 0.943 | 0.831 | 0.544 → 0.883 |
| d256, lr 1e-4 (0.077) | 0.899 | 0.749 | 0.518 → 0.892 |

The best observer is the same for every learner: one step, c = ¼, β = 2.

## Predictions

- **Q1 (R < 1): holds.** R = 0.73.
- **Q2 (the named best observer is within 0.01 of best for ≥ 8 of 10): holds, 10 of 10.** It is *the* best for all ten.
- **Q3 (the prior-free two-step gain shrinks as two-step error grows): fails, reversed.** Spearman = +0.85. The worse
  the learner, the more the second step helps a prior-free observer. Gains run from 0.02 for the best learners to
  0.34–0.37 for the two worst.
- **Q4 (the best observer's accuracy tracks quality, Spearman ≤ −0.6): holds,** at −0.98.

## Reading

- **Pattern B, revised.**
  - At fixed quality (seeds), the observer moved verdicts 3–6× more than the learner did.
  - Across a 3.4× quality ladder, the two are comparable (R = 0.73).
  - "The observer dominates" was a fixed-quality effect. "The observer matters as much as the learner" survives.
- **But the observer question has a stable answer.** One observer design is best for every learner, transformer or
  GRU, well or badly trained, and its verdict ranks learners by true quality almost perfectly (−0.98). The observer's
  influence is large, and it is not arbitrary.
- **Why Q3 reversed** (an inference; not checked mechanistically):
  - I reasoned that worse learners compound error at the second step, and they do (two-step TV 0.049 → 0.133).
  - But a prior-free one-step observer of a poor learner is trapped by the rare near-pure neighbours of F2/F5. Its
    accuracy collapses to about 0.52.
  - The two-step margin is about eight times wider (one-step 0.015 against two-step 0.12 at k = 7; 2.4–6.2× at k = 6),
    which is enough to escape the trap even with compounded error.
  - The second step is worth most exactly where the learner is worst.

## For the story

The defensible core, in one world:
1. Certifying "randomness, not hidden state" from a model's outputs needs a prior or a richer query.
2. A good observer exists, is the same for every learner tried, and its verdict tracks learner quality.
3. Without a prior, a richer query rescues the worst learners most.
4. An exact world makes each of these measurable, including the cases where the reasoning that motivated them was
   wrong.
