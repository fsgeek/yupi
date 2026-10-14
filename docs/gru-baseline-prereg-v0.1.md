# A recurrent baseline: pre-registration v0.1 (2026-10-13)

> **Status: PRE-REGISTRATION, DRAFT for two-family pre-stamp review.** It is committed and stamped before any GRU
> is trained beyond a 20-step CPU smoke test. Exploratory in scale: one seed per cell. Owning instance. Occasion:
> whole-draft review W28 (both families asked for a recurrent baseline).

## 1. The learner

`GRUNet` (`src/yupi/learner/model.py`): token embedding, a 2-layer GRU of width 256, LayerNorm and the transformer's
output head, 870,300 parameters (the transformer has 838,940). It is causal by construction, with the causality test
in `tests/test_learner_model.py`. The recipe is the transformer's 15-epoch recipe, unchanged: AdamW, lr 1e-3 → 1e-4
cosine, warmup 500, batch 256, clip 1.0, every position scored, `--arch gru --d-model 256 --n-layer 2`. We tune no
learning rate for the GRU, and we say so: an untuned baseline can understate a recurrent learner.

## 2. Runs

One seed (seed 1) in each of the 8 content cells, r1–r4 × ε ∈ {1, ½}, on the same corpora as the transformer ladder:

| cell | corpus |
|---|---|
| r1 ε1 | `c1prime-loop-40-8-2-r1-eps1/fd5da4c31e43d73d` |
| r2 ε1 | `c1prime-loop-40-8-2-r2-eps1/125f89ba98065599` |
| r3 ε1 | `c1prime-loop-40-8-2-r3-eps1/b32b8f15767eae2f` |
| r4 ε1 | `c1prime-loop-40-8-2-r4-eps1/ee9475787e67a1cc` |
| r1 ε½ | `c1prime-loop-40-8-2-r1-eps1_2/76939d7414401e8b` |
| r2 ε½ | `c1prime-loop-40-8-2-r2-eps1_2/aac405dd85f12bf6` |
| r3 ε½ | `c1prime-loop-40-8-2-r3-eps1_2/82fa177578b77b27` |
| r4 ε½ | `c1prime-loop-40-8-2-r4-eps1_2/21a34684aa833e0e` |

All eight train in parallel on the GPU under an ayllu-gpu lease (TTL 4 h). The wave stops if the trainer fails to
reproduce the 10-02 transformer r1 seed-1 step-1000 losses exactly; this is the same gate as the 2×2.

## 3. Predictions and readings, fixed now

Each GRU model is scored by the frozen census (k = 7, its own corpus) and by `b1_fe_coarse_robustness.one`, which
reproduces the frozen model's HC1 fit to 1e-9 before adding anything.

- **G1 (the within-cell association holds for a recurrent learner):** β_long > 0 with frozen-model HC1 t ≥ 3, in
  every one of the 8 GRU models. This is the D1 criterion, per model.
  - Reading: *met* (8/8), or *not met*, with the count reported.
- **G1R (robustness):** the same coefficient under the fixed effects (last kind × number of distinct actors) with
  coarse-cell clustering. We report how many of 8 keep t ≥ 3. No threshold is pre-registered.
- **G2 (descriptive):** each GRU model's KIND shortfall beside the transformer's three 15-epoch seeds and the count
  table, per cell. "The GRU is between" or "outside" is stated cell by cell, without a test.

ACTOR is reported alongside and not scored.

## 4. What paper 1 will say

- G1 met: "the KIND association also holds for a parameter-matched recurrent learner, one seed per cell".
- G1 not met: the count, and "it does not hold for every recurrent model", with no further reading.
- G2: in a table, without inference.

## 5. Gates

- `run.json` records arch gru, a clean revision, the corpus manifest, and steps 117,195.
- The census sha256 matches its JSONL.
- The trainer-reproduction gate (§2).
- The census reproduces 10-02 r1 seed 1 byte for byte after the `build_model` change: done before stamping,
  2026-10-13, sha256 prefix 7a0f6b570f01811c.
