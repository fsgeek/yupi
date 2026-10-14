# A recurrent baseline: pre-registration v0.1 (2026-10-13)

> **Status: PRE-REGISTRATION v0.1, revised after two-family pre-stamp review (Claude and Codex, both "stamp after
> fixes"; every fix adopted, §6).** It is committed and stamped before any GRU is trained beyond CPU smoke tests.
> Exploratory in scale: one seed per cell. Occasion: whole-draft review W28.

## 1. The learner

`GRUNet` (`src/yupi/learner/model.py`): token embedding (d = 256), a 2-layer GRU of width 256, LayerNorm and the
output head. It has 870,300 parameters, against the transformer's 838,940, so it is approximately parameter-matched
(+3.7 %).
- **Initialization:** embedding and head N(0, 0.02), head bias 0; the GRU weights and biases use PyTorch defaults
  (uniform ±1/16).
- **Weight decay:** 0.1 on every ≥ 2-D parameter, the transformer's rule.
- **Positions:** none are input. Recurrence from BOS gives position implicitly, and padding sits at the right, so a
  causal model never sees it. Causality is tested.
- **Not tuned:** the learning rate is the transformer recipe's 1e-3. An untuned baseline can understate a recurrent
  learner, and §4 says so.

## 2. Runs

**Command, per cell:**

```
learner_train.py --corpus-dir <cell corpus> --out ~/.cache/yupi-scratch/runs/gru/c1prime-loop-40-8-2-<cell>-2M-gru256x2-e15-s1
  --device cuda --epochs 15 --lr 1e-3 --warmup 500 --batch-size 256 --ckpt-every 2000 --val-every 1000
  --seed 1 --arch gru --d-model 256 --n-layer 2
```

This is driven by `scripts/gru_baseline_wave.sh`, with all 8 runs in parallel under an ayllu-gpu lease (TTL 4 h;
the runs resume exactly if the lease ends). The cells and corpora are the transformer ladder's:

| cell | corpus |
|---|---|
| r1-eps1 | `fd5da4c31e43d73d` |
| r2-eps1 | `125f89ba98065599` |
| r3-eps1 | `b32b8f15767eae2f` |
| r4-eps1 | `ee9475787e67a1cc` |
| r1-eps1_2 | `76939d7414401e8b` |
| r2-eps1_2 | `aac405dd85f12bf6` |
| r3-eps1_2 | `82fa177578b77b27` |
| r4-eps1_2 | `21a34684aa833e0e` |

**Census:** the frozen script at k = 7 on the full test split of each run's own corpus, giving
`docs/learner-window-census-gru-<cell>-2M-e15-seed1-2026-10-13.json`. These names do not match the B1 family globs,
which carry other dates. Driven by `scripts/gru_baseline_census.sh`.

**Scorer:** `scripts/gru_baseline_score.py`, committed with this pre-registration.

## 3. Readings, fixed now

All of these use ι_kind,4 (`m_long` = 4) and the model `full_plus_log2_class_mass`, with the fields `beta_long` and
`t`.

- **Quality floor, per model.** A GRU model is *informative* only if its mean KIND shortfall is below the count
  table's in that cell. A model under the floor is reported as *uninformative (under-trained)*, counted separately,
  and given no G1 reading. (A near-untrained GRU gives a strongly negative t, as the smoke run showed.)
- **G1, per informative model:** β_long > 0 with frozen-model HC1 t ≥ 3. This is the D1 criterion: within a model,
  t ≥ 3 only resolves the sign. The reading is *"the pre-registered criterion was met in X of Y informative GRU
  models"*. Among the misses, we count separately those with a nonpositive β and those with a positive β but
  t < 3. An undefined statistic is an analysis failure.
- **Robustness, reported with no threshold:** the same regression with class-clustered CR1 errors
  (`b1_clustered_refit.one`), and with the coarse-cell fixed effects (`b1_fe_coarse_robustness.one`). These are the
  transformer's two checks in §4a.
- **G2, descriptive:** per cell, the GRU's KIND shortfall beside the three transformer seeds and the count table,
  as values only, with no between/outside label.
- **ACTOR** means are reported alongside, unscored.

**Not inferable from this design:** anything about the population of GRU seeds, and any claim that one architecture
is superior to the other.

## 4. What paper 1 will say

- **If Y = 8 and X = 8:** "With an untuned learning rate, the KIND association also holds in each of eight
  parameter-matched GRU models, one per cell. A recurrent learner is itself locality-biased, so a shared direction
  does not separate locality from class rarity (§4a)."
- **Otherwise:** the counts (X of Y, the misses by kind, the models under the floor), with no further reading.
- **G2:** a table.

## 5. Gates (the scorer refuses if any fails)

- **R, the reference:** the regression code reproduces the *committed* 10-02 transformer r1 seed-1 fit
  (β_long 0.017472070944896154, se 0.0025730666784200334) to 1e-12. Checked before stamping: it passes.
- **Per model:**
  - `run.json` says arch gru, d 256, 2 layers, seed 1;
  - checkpoint step = census step = 117,195;
  - the census is k = 7 on the test split, with n equal to the transformer census of its cell;
  - the census sha256 matches its JSONL.
- **In the wave, before any GRU:** HEAD reproduces the 10-02 transformer r1 seed-1 step-1000 losses exactly, or
  the wave stops.
- **GRU GPU determinism, recorded and not a stop:** two identical 200-step GRU runs on the GPU. If they differ, the
  paper's reproducibility statement excludes the GRU.
- **The census reproduces 10-02 r1 seed 1 byte for byte after the `build_model` change:** done before stamping
  (7a0f6b570f01811c), and also confirmed by Codex.

## 6. Pre-stamp review record (2026-10-13)

- **Claude:**
  - a quality floor, because a failed GRU otherwise reads as a negative (blocking, adopted);
  - G1 pinned down (fields, paths, an arch gate);
  - the GRU GPU determinism check;
  - the §4 sentence narrowed (untuned learning rate; the rarity caveat);
  - class-clustered CR1 added;
  - the full command;
  - initialization and weight decay disclosed;
  - five older scripts still build `Decoder` directly (noted; they fail loudly on a GRU, and none is in this path).
- **Codex:**
  - completion bound to checkpoint and census step (blocking, adopted);
  - G1 failure wording;
  - the regression gate checked against committed history, not against itself;
  - class-clustered CR1;
  - the frozen command and initialization;
  - G2 endpoints (now values only).
