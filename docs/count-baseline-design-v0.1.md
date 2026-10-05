# The canonicalize-and-count baseline: design v0.1 (2026-10-04)

> **Status: DESIGN.** Paper-1 skeleton v0.2 §3 item 1 (v0.1 item 2). It answers the simulated reviewer's
> objection 1: is gap 2 a statement about transformers at all, or would any learner trained on the same 2M
> windows fall short in the same way? Written by the owner, the instance of 2026-10-02/04.

## 1. The learner

The learner reads no model weights. It counts.
- **Canonicalize.** A prefix of k records becomes its pattern class (reset flag, Π_all(records[:k])). That is
  exactly the key the ceiling tables use, so entity names are replaced in first-appearance order.
- **Count.** For every train window and every k, the learner counts the KIND of record k + 1 under the prefix's
  full class. It also counts under backoff classes: the pattern of the last m records alone, for m = k−1, …, 1,
  plus an unconditional KIND count.
- **Predict.** The prediction is an interpolated (Witten–Bell) estimate down the backoff chain: from the full class
  to order k−1, …, order 1, then unigram. The interpolation has no free parameter beyond the chain itself. A
  second variant, plain add-α on the full class with backoff only for unseen classes, is selected on the **val**
  split, never on test.

With unlimited data and the full class, this learner converges to P*(KIND | class). That is the ceiling, so its
excess is exactly the finite-data cost of counting.

## 2. The evaluator contract (unchanged)

`evaluate()` and the census take `logprobs_fn(inputs[N, seq_len]) -> [N, seq_len, 156]`. Position `off + 5k`
predicts record k + 1's KIND. `window_excess` renormalizes that row over non-PAD and reads only KIND tokens for
`by_field.kind` and `kind_kl_bits`. The baseline fills that row with log-probabilities from the counts on the
KIND tokens, and gives a large negative value to non-KIND, non-PAD tokens. Every other position is uniform.
**Only `by_field.kind` and `kind_kl_bits` are meaningful for this learner.** The other fields' numbers are written
but must not be read, and the raw says so. This is paper 1's common target (D3), so nothing is lost.

## 3. Gates (tests before any number)

1. **Exactness gate.** Fill the counts from a k-table's exact law (counts ∝ mass × P*). The evaluator must then
   give KIND excess = 0 on every window whose class is in the table, to float tolerance. That checks the
   canonicalization, the position plumbing and the renormalization in one test.
2. **Name invariance.** Permuting entity names within a window leaves the predicted KIND row unchanged.
3. **Valid rows.** Every filled row log-sum-exps to 0 over non-PAD tokens.
4. **No test leakage.** Counts come from `train` only. Hyperparameters, where any exist, come from `val`.

## 4. Runs and outputs

All ten cells of the sweep (r0–r4 × ε ∈ {1, ½}), each on its 2M corpus: `scripts/count_baseline.py --corpus
<dir> --raw docs/count-baseline-eval-<cell>-2026-10-0x.json` (k = 1..7), plus the k = 7 census via the
existing census machinery with a `--learner count` path, writing per-window files as usual. CPU only.

Reported beside each cell's transformer numbers (converged d = 128 seeds 1–3):
- the mean KIND excess at k = 7;
- the share of k = 7 windows whose full class was unseen in train;
- **exploratory:** the binned ι4 profile (the plateau check) on the count learner's per-window excess, with the
  same bins as `docs/review-2026-10-04/`.

## 5. What a result means

- **Count ≈ ceiling** (KIND excess well below the transformer's): gap 2 is a statement about transformers at this
  scale. §4 opens with that.
- **Count ≥ transformer:** the transformer does at least as well as counting the data. Gap 2 is mostly a
  finite-data cost, and §4 must say the learner side measures data efficiency, not architecture.
- **The plateau check.** If the count learner shows the same plateau over ι4, the plateau comes from data
  sparsity: classes with long-range dependence are rarer and more fragmented. If it doesn't, the plateau is the
  transformer's. Either answer changes how §4 reads the plateau.

This is exploratory, not a prereg. If a result here is to carry a claim in the paper, it is re-run on held-out
data or seeds, and stamped first.
