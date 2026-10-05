# The canonicalize-and-count baseline: results v0.1 (2026-10-04)

> **Status: EXPLORATORY.** Design: `docs/count-baseline-design-v0.1.md`, committed first. Code:
> `src/yupi/learner/count_baseline.py` and `tests/test_count_baseline.py`. Four gates pass, and the exactness gate
> was mutation-checked: it fails when the KIND position is shifted by one token. Per-cell raws are
> `docs/count-baseline-<cell>-2026-10-04.json`. Comparison: `scripts/count_plateau.py` (committed before it ran)
> → `docs/count-baseline-comparison-2026-10-04.json` and `.log`. The counts come from `train` only. Witten–Bell
> was the mode chosen on `val` in every cell. The comparison uses the same k = 7 test windows as the converged
> transformer censuses (d = 128, 15 epochs, seed-mean of seeds 1–3).

## 1. The transformer beats counting, by a lot, wherever entities exist

KIND excess at k = 7 (bits per window):

| cell | count | transformer | count / transformer | classes unseen in train |
|---|---|---|---|---|
| r0 ε=1 | 0.0042 | 0.0038 | 1.1 | 21 / 3,678 |
| r1 ε=1 | 0.0422 | 0.0154 | 2.7 | 628 / 25,005 |
| r2 ε=1 | 0.0540 | 0.0189 | 2.9 | 841 / 28,722 |
| r3 ε=1 | 0.0635 | 0.0134 | 4.7 | 1,133 / 32,584 |
| r4 ε=1 | 0.0622 | 0.0133 | 4.7 | 1,091 / 32,755 |
| r0 ε=½ | 0.0039 | 0.0049 | 0.8 | 15 / 3,486 |
| r1 ε=½ | 0.0386 | 0.0213 | 1.8 | 581 / 20,248 |
| r2 ε=½ | 0.0438 | 0.0293 | 1.5 | 790 / 23,062 |
| r3 ε=½ | 0.0470 | 0.0218 | 2.2 | 1,053 / 25,522 |
| r4 ε=½ | 0.0439 | 0.0230 | 1.9 | 1,023 / 25,690 |

The count standard errors are 0.0005–0.0019.

**Reviewer objection 1 is answered for this baseline.** Gap 2 is not what any learner gets from counting these 2M
windows. Where the world has entities (r1–r4), the transformer's KIND excess is 1.5–4.7 times smaller than an
interpolated count table over the ceiling's own classes. On r0, which has few classes and no entities, the two
coincide. The count learner's excess also grows with the number of classes (r1 < r2 < r3 ≈ r4 at ε = 1), and the
transformer's does not. The transformer generalizes across histories that the table keeps apart. This is a weak
baseline, a smoothed n-gram over pattern classes. A stronger non-neural or recurrent learner (v0.1's GRU) could
narrow the gap, and nothing here rules that out.

## 2. The step at ι4 > 0 appears in the count learner too

Binned effects relative to ι4 = 0 (the model and bins of `docs/review-2026-10-04/`) show the same qualitative
shape for both learners. The excess is higher in every class with *any* long-range information, and it rises
in the top bin (> 0.6 bits). For the transformer this holds in all 8 r1–r4 cells, with every bin at t ≥ 3.4. For
the count learner it is clear at ε = 1 (low bins t 3.0–7.4). At ε = ½ it is weaker: in r3, r4 and r2 several low
bins have t < 2, and only the top bin is strong in every cell (t 7.4–11.8). For the count learner the low bins are larger and noisier
(e.g. r1 ε=1: +0.073, +0.048, +0.030 … +0.082, against the transformer's +0.013, +0.012, +0.010 … +0.027).

**Reading (exploratory; a hypothesis, not a finding).** A count table has no attention and no notion of distance,
yet it shows the step. That makes it unlikely the step is a transformer mechanism. One account fits both learners:
**a learner that shares statistical strength across histories pays wherever the far history matters at all.**
Witten–Bell does this by construction, mixing in the order-m suffix estimates, which are wrong exactly when
ι_m > 0. How much it pays is set by how much the learner smooths, which depends on data sparsity, not on how many
bits ι carries. The transformer, which generalizes better, pays a smaller step of the same shape. This account is
consistent with the plateau and with the relay result. The relay helps only where ι4 > 0, so making the binding
fact explicit would reduce the cost of sharing strength there. It has not been tested.

What it does not explain: the count learner's largest low-bin effect sits at ι4 ≤ 0.001, where backoff
contamination should be small. The fit controls log2 class mass linearly, so some sparsity confound may remain.

## 3. Consequences for skeleton v0.2

- §4 can say: the transformer is far better than counting the same data where entities exist. The learner gap is
  a property of a learner that generalizes, measured against an exact ceiling, not a finite-data artefact of the
  corpus.
- The plateau gets a candidate account that does not involve distance. A confirmatory test (v0.2 §3 item 2)
  should include the count learner as a second learner, run on the fresh seeds' corpora. The prediction would be
  that both show the step and that the transformer's step is smaller.
