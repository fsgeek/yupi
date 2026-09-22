# The learner's first results at the frozen law — ten cells, three seeds, k = 7 (v0.1, 2026-09-18)

> **Status: EXPLORATORY, interim.** The first model-versus-ceiling numbers
> in the project, from the sweep of 2026-09-18 (trainer spec
> `docs/superpowers/specs/2026-09-18-learner-trainer-design.md`; contract
> `learner-model-vs-ceiling-contract-v0.1.md` v0.1.2). Every number is a
> per-window mean over the cell's test split with its standard error, from
> a committed raw `docs/learner-eval-<cell>-seed<s>[-cpu]-2026-09-18.json`
> (33 raws: ten cells × three GPU seeds, plus three CPU seeds at r4 ε=1),
> against the prefix ceiling tables of `pattern-ceilings-40-8-2-k7-2026-09-18.json`
> (every gate exact). Two things are still running as this is written and
> will be appended in the ledger: the per-position curves (k = 1..7) and a
> 40-epoch convergence follow-up. Written by the instance of 2026-09-18.

## 1. Setup, in one paragraph

Decoder-only transformer, 838,940 parameters (d = 128, 4 layers, 4 heads,
MLP 512), trained from scratch for 10 epochs (7,820 steps of 256 windows)
on each of the ten (40, 8, 2) looping-C1′ corpora (200k training windows,
all four entity types renamed per episode), AdamW with warmup and cosine,
fp32, deterministic on both devices (`learner-gpu-determinism-2026-09-18.json`:
repeat and resume bit-identical on the 4090). Scored on the test split
(10⁵ windows) at the headline position k = 7 — seven records seen, the
eighth predicted — against the pattern observer's exact next-record
distribution $P^\star(\Pi r \mid \Pi w_{\le 7})$, by the realized-record,
field-chained estimator of the contract (v0.1.1 (a)): the **structural
excess** is the model's cost above the ceiling on the record's five
pattern values; the **naming excess** is its cost above uniform on fresh
entities' tokens; their sum is the token excess given continuation.
Windows with fewer than eight records (RESET windows with T < 8, 15 % of
the law) have no k = 7 position and are not in these means.

## 2. The headline table

Structural excess at k = 7, bits per record, mean over the cell's ~85,000
scored windows; the within-seed standard error is ≤ 0.006 everywhere and
is omitted; the pooled column is the mean of the three seeds with the
**between-seed** standard deviation.

| cell | seed 1 | seed 2 | seed 3 | pooled | between-seed sd | ceiling $H^\star$ |
|---|---|---|---|---|---|---|
| r0 ε=1 | 0.0140 | 0.0152 | 0.0153 | **0.015** | 0.0007 | 0.999 |
| r0 ε=½ | 0.0183 | 0.0176 | 0.0191 | **0.018** | 0.0008 | 0.938 |
| r1 ε=1 | 0.2621 | 0.2844 | 0.2625 | **0.270** | 0.013 | 1.377 |
| r1 ε=½ | 0.3187 | 0.3574 | 0.3167 | **0.331** | 0.023 | 1.169 |
| r2 ε=1 | 0.3750 | 0.3135 | 0.4162 | **0.368** | 0.052 | 1.359 |
| r2 ε=½ | 0.3742 | 0.5064 | 0.4176 | **0.433** | 0.067 | 1.131 |
| r3 ε=1 | 0.4752 | 0.3428 | 0.3121 | **0.377** | 0.087 | 1.292 |
| r3 ε=½ | 0.3956 | 0.3437 | 0.4163 | **0.385** | 0.037 | 1.070 |
| r4 ε=1 (GPU) | 0.2863 | 0.7203 | 0.4675 | **0.491** | 0.218 | 1.292 |
| r4 ε=1 (CPU, same seeds) | 0.3183 | 0.6768 | 0.3364 | **0.444** | 0.202 | 1.292 |
| r4 ε=½ | 0.6205 | 0.7220 | 0.9161 | **0.753** | 0.150 | 1.070 |

(Every per-seed number: `scripts/learner_summary.py docs/learner-eval-*.json`.)
Naming excess is 0.008–0.026 bits per record at every content rung (the
uniform-over-unused rule is learned); exactly 0 at r0, where no entity is
ever visible. The end-of-window process excess is ≤ 0.002 bits per window
everywhere: the model learned the ¼ / ⅓ / ½ endpoint rule.

## 3. What the table says

1. **At r0 the model is on the ceiling.** 0.015–0.018 bits above an
   exact ceiling of about a bit, tight across seeds. Kind-only traces are
   learned to within the resolution the contract asked for.
2. **At every content rung the model is far from the ceiling.** 0.27 to
   0.75 bits per record above ceilings of 1.07–1.38 bits — a fifth to
   two thirds of the irreducible entropy again in excess. The excess is
   concentrated in the KIND field's exact KL (0.08–0.22 bits) and the
   entity fields; the naming rule is essentially learned. This is the
   accessible-representation-plus-exposure gap of the proposal, and at
   this scale and budget it is large, not zero. The morning's concern that
   the world might be too easy for the learner was right for r0 and wrong
   for every rung where names enter: **the identity axis is where the
   learner fails.**
3. **The between-seed spread dwarfs the exact side's threshold.** The
   contract set δ/3 ≈ 0.003 bits as the resolution target for the
   learner-side ladder. Between-seed standard deviations at content rungs
   are 0.013–0.22 bits; the seed count that target implies runs from 15
   (r1 ε=1) to over 3,000 (r4 ε=1). Two facts locate the cause:
   - every run's validation loss is still falling at the last step
     (r2 ε=1: 0.8030 → 0.8003 nats per token over the last thousand
     steps); these are undertrained runs, not converged solutions;
   - the same seed on CPU and GPU — the same initialization and data
     order, different floating-point paths — lands in the same basin
     (r4 ε=1: seed 2 is the worst seed on both, 0.72 and 0.68; seed 1 the
     best, 0.29 and 0.32) but 0.03–0.13 bits apart. At this budget the
     excess is sensitive to the arithmetic, not only the seed.
   The learner-side ladder r1 → r2 → r3 (0.27 → 0.37 → 0.38 at ε=1) is
   therefore **unresolved** with three seeds: the pooled standard errors
   (0.007, 0.030, 0.050) overlap. The contract's rule applies as written —
   a difference smaller than the sum of the standard errors is reported
   as unresolved, not as zero — and the remedy is not more seeds of the
   same run but runs that converge (§5).
4. **r4 is worse than r3 for the learner although their ceilings are
   identical.** The pattern observer's $H^\star$ is the same at r3 and r4 to
   three decimals at every k and both ε (`pattern-ceilings-40-8-2-k*`):
   lineage adds nothing a naming-blind observer can use. The model at r4
   pays 0.44–0.75 bits against 0.38 at r3. Part of this is arithmetic —
   at r4 the lineage field is a fifth pattern value to predict (bound or
   fresh request id) where at r3 it is MASKED and free — and the per-field
   split that would separate that from a genuine cost of the extra field
   is owed (§5). Part is the seed spread.
5. **ε = ½ costs the learner more than ε = 1** at every content rung
   (0.33 vs 0.27 at r1; 0.75 vs 0.49 at r4) while its ceilings are lower
   (the live cursor makes the trace more predictable). The model recovers
   less of a more structured trace. Not resolved beyond r1 with three seeds.

## 4. What this does not say

Nothing here is a claim about the canonical (structurally informed)
observer, whose ladder is 0.07 / 0.12 / 0.015 bits and is the exact side's
result. Nothing is a claim about scale (one size, one data volume, one
training budget) or about probes. The r1 → r2 → r3 ordering of the pooled
means is suggestive and unresolved. The r4 excess is confounded with the
extra field until the per-field split exists.

## 5. What follows, in order

1. **Per-position curves** (k = 1..7) for all 33 runs — running as this
   is written; appended below when done.
2. **Convergence follow-up** — r1 ε=1 and r2 ε=1, seeds 1–3, 40 epochs on
   the same data (GPU, running): does the excess fall, and does the
   between-seed spread close, when the runs converge? If it does, the
   sweep is rerun at the converged budget and the seed count is set from
   the converged spread. If it does not, the spread is a property of the
   learner at this scale and is reported as such.
3. **Per-field decomposition** in the evaluator (kind / actor / object /
   related / lineage), so the r3-versus-r4 question and the "where does
   the model fail" question have exact answers instead of a KIND KL and a
   remainder.
4. Then the scale and data-volume axes (RQ5), and the probes (sub-project 3).

## 6. Ledger

- 2026-09-18 13:23 PDT (from `date`): written after the 33 k = 7 raws
  landed; curves and the 40-epoch follow-up running.
- 2026-09-18 13:24 PDT (from `date`): the r2 ε=½ row's seed-2 and seed-3 cells were
  first written from memory (0.4224 / 0.5015) and were wrong; corrected
  from the raws (0.5064 / 0.4176) before commit. The pooled mean and sd
  were right. Every other cell re-checked against the summary table.

- 2026-09-18 13:43 PDT (from `date`), **the convergence follow-up (§5.2) is
  answered and stopped after one run.** r1 ε=1 seed 1 at 40 epochs on the
  same 200k windows: validation loss reaches its minimum 0.6233 at
  step 10000 and rises to 0.6693 by step 31280 — the
  model **overfits** the 200k-window corpus. Its k = 7 structural excess is
  0.8945 ± 0.0081 bits (0.262 at 10 epochs), naming
  excess 0.2623 (0.013), and the per-field split
  (`structural_by_field`, added this afternoon) puts 0.736 of it
  in the ACTOR field and 0.158 in KIND: the failure is *which
  named thread acts next*. §3.3's diagnosis ("undertrained runs") was
  wrong: the 10-epoch runs sit near their validation minimum, and the
  between-seed spread is a spread among solutions of comparable
  validation loss on too little data. The remedy is **data, not steps**
  (the corpus is free: 164 s per 2M windows). Running: r1 ε=1 and r4 ε=1
  on 2M-window corpora (new run keys; same ceiling tables — pattern classes
  do not depend on the key), seeds 1–3, 5 epochs, GPU. The remaining
  40-epoch runs were stopped by SIGTERM (checkpointed, lease released).
  Raw: `learner-eval-r1-eps1-e40-seed1-2026-09-18.json`.

## 7. The per-position curves (appended 2026-09-18 13:51 PDT)

Structural excess (bits per record) at every prefix length k, pooled over
the three GPU seeds per cell; raws `learner-eval-*-2026-09-18.json` (all
33 now carry k = 1..7 and the per-field split). The exact ceiling
$H^\star$ *falls* with k at every content rung (`pattern-ceilings-40-8-2-k*`,
e.g. r1 ε=1: 1.83 → 2.18 → 1.84 → 1.79 → 1.63 → 1.48 → 1.38 bits); the
learner's excess **rises**:

| cell | k=1 | k=2 | k=3 | k=4 | k=5 | k=6 | k=7 | k=7 / k=1 |
|---|---|---|---|---|---|---|---|---|
| r0 ε=1 | 0.001 | 0.002 | 0.002 | 0.004 | 0.005 | 0.008 | 0.015 | 19 |
| r0 ε=½ | 0.001 | 0.002 | 0.002 | 0.004 | 0.006 | 0.011 | 0.018 | 26 |
| r1 ε=1 | 0.010 | 0.023 | 0.037 | 0.070 | 0.118 | 0.180 | 0.270 | 27 |
| r1 ε=½ | 0.012 | 0.027 | 0.047 | 0.093 | 0.146 | 0.232 | 0.331 | 28 |
| r2 ε=1 | 0.012 | 0.030 | 0.055 | 0.112 | 0.180 | 0.246 | 0.368 | 32 |
| r2 ε=½ | 0.013 | 0.033 | 0.065 | 0.147 | 0.226 | 0.323 | 0.433 | 33 |
| r3 ε=1 | 0.020 | 0.044 | 0.080 | 0.135 | 0.202 | 0.257 | 0.377 | 19 |
| r3 ε=½ | 0.022 | 0.057 | 0.099 | 0.172 | 0.223 | 0.307 | 0.385 | 18 |
| r4 ε=1 | 0.025 | 0.074 | 0.129 | 0.199 | 0.288 | 0.344 | 0.491 | 20 |
| r4 ε=½ | 0.032 | 0.147 | 0.246 | 0.361 | 0.477 | 0.576 | 0.753 | 24 |

Every one of the 27 content-rung runs is strictly increasing in k (the
two exceptions are r0 runs whose k = 2 → 3 step is within 0.0005 of
zero). Three readings, in decreasing confidence:

1. **After one record the learner is near Bayes everywhere** (0.001–0.03
   bits); after seven it is 20–30× further from the ceiling. The exact
   posterior sharpens with evidence; the learner's excess compounds with
   it. This is the proposal's "context as epistemic access" axis measured
   inside one window, and the sign is the interesting part: more evidence
   makes the exact observer more certain and the learner relatively worse.
2. **The growth ratio is similar at every rung, r0 included** (19–33×), so
   part of the mechanism is generic to position — a ~0.85M model trained on
   200k windows integrates longer contexts less well whatever they
   contain — and the *magnitude* is what the interface sets: content rungs
   sit 20–50× above r0 at every k. Whether the ratio survives more data,
   more parameters, or a different positional scheme is the next
   question, and the 2M-window runs will answer the first part.
3. The r3 → r4 comparison at fixed k stays confounded by the fifth field
   (§3.4); the per-field split now in every raw is the tool for it and is
   read in the next note, not here.

- 2026-09-18 13:57 PDT (from `date`), **the first 2M-window run (r1 ε=1, seed 1,
  5 epochs = 39,060 steps).** Validation loss falls throughout (0.6243 at
  step 6000 → 0.6119 at 39065; no overfitting) and ends below any
  200k-window run's minimum. At k = 7, against the same ceiling table:
  structural excess **0.0641 ± 0.0013** bits (200k, same
  seed: 0.2621); naming 0.0028 (0.0127); KIND field
  0.0244 (0.1008); ACTOR field
  0.0397 (0.1612). Ten times the data
  divides the excess by 4.1 in every field alike, and leaves it at
  about 5 % of the ceiling's 1.377 bits. The gap at this model
  size is data-limited and not zero. The other five 2M runs (r1 seeds 2–3,
  r4 seeds 1–3) are running; their curves and per-field splits go in the
  next note. Raw: `learner-eval-r1-eps1-2M-seed1-2026-09-18.json` (its test
  split is the 2M corpus's own, 100k windows under the new key).

## 8. Where the excess sits: the per-field split (appended 2026-09-18 13:58 PDT, from `date`)

Structural excess at k = 7 by field, bits per record, pooled over the three
GPU seeds per cell (200k-window runs; every raw now carries
`structural_by_field`):

| cell | KIND | ACTOR | OBJECT | RELATED | LINEAGE | total |
|---|---|---|---|---|---|---|
| r0 ε=1 | 0.015 | — | — | — | — | 0.015 |
| r0 ε=½ | 0.018 | — | — | — | — | 0.018 |
| r1 ε=1 | 0.105 | 0.165 | — | — | — | 0.270 |
| r1 ε=½ | 0.143 | 0.188 | — | — | — | 0.331 |
| r2 ε=1 | 0.118 | 0.192 | 0.058 | — | — | 0.368 |
| r2 ε=½ | 0.165 | 0.209 | 0.059 | — | — | 0.433 |
| r3 ε=1 | 0.111 | 0.154 | 0.073 | 0.039 | — | 0.377 |
| r3 ε=½ | 0.139 | 0.158 | 0.059 | 0.030 | — | 0.385 |
| r4 ε=1 | 0.128 | 0.216 | 0.064 | 0.073 | 0.010 | 0.491 |
| r4 ε=½ | 0.214 | 0.282 | 0.138 | 0.102 | 0.017 | 0.753 |

(A MASKED field contributes exactly 0 for any model and is shown as —.)

- **ACTOR is the largest term at every content rung** (0.15–0.28 bits),
  KIND the second (0.10–0.21). *Which named thread acts next* is what the
  learner cannot do, before anything about locks, waiters or requests.
- **The r3 → r4 question of §3.4 is answered as far as three seeds allow:**
  the LINEAGE field itself costs the learner only 0.010–0.017 bits. The
  rest of r4's larger excess (0.11 bits over r3 at ε=1, 0.37 at ε=½) is
  paid on KIND, ACTOR and RELATED — fields the r3 model also predicts —
  so an exposed lineage field makes the *other* predictions worse, not
  better, for this learner, although it adds nothing to the exact
  observer. With r4 ε=1's between-seed sd of 0.22 the ε=1 difference is
  unresolved; the ε=½ difference (0.37 against sds 0.04 / 0.15) is not.
- The uniform-over-unused naming rule aside, the learner's failure is a
  binding failure in the sense of Part I D3: it is the entity fields, and
  the kind of the next event given who holds what, that carry the excess.

## 9. The data-volume axis: 2M windows (appended 2026-09-18 14:58 PDT, from `date`)

r1 ε=1 and r4 ε=1 retrained on 2M-window corpora (new run keys; the same
ceiling tables), seeds 1–3, 5 epochs (39,060 steps), validation loss still
falling at the end in every run. Structural excess at k = 7, bits per
record (raws `learner-eval-*-2M-seed*-2026-09-18.json`):

| cell | 200k, seeds 1 / 2 / 3 | pooled (sd) | 2M, seeds 1 / 2 / 3 | pooled (sd) | ÷ |
|---|---|---|---|---|---|
| r1 ε=1 | 0.262 / 0.284 / 0.263 | 0.270 (0.013) | 0.064 / 0.063 / 0.052 | **0.060** (0.007) | 4.5 |
| r4 ε=1 | 0.286 / 0.720 / 0.468 | 0.491 (0.218) | 0.056 / 0.133 / 0.066 | **0.085** (0.042) | 5.8 |

Per-position curves at 2M, pooled (k = 1 → 7): r1 0.006 → 0.010 → 0.012 →
0.017 → 0.024 → 0.037 → 0.060; r4 0.013 → 0.027 → 0.039 → 0.042 → 0.053 →
0.061 → 0.085. Naming excess 0.002–0.005. KIND field's exact KL 0.016–0.043.

Readings:

1. **Ten times the data divides the excess by 4.5–5.8 and halves to
   fifths the between-seed spread.** With 2M windows, r1 ε=1 needs 5 seeds
   for the contract's δ/3 resolution — attainable — and the learner sits at
   about 4 % of the ceiling's entropy. The gap is data-limited at this
   size, and still not zero.
2. **The r4 penalty of §3.4/§8 was a data artifact.** For seeds 1 and 3,
   r4 costs the learner no more than r1 (0.056 / 0.066 vs 0.064 / 0.052).
   With enough data the extra visible fields are absorbed; the exact
   observer's verdict (r3 ≡ r4) and the learner's now agree.
3. **Seed 2 at r4 is the outlier at both volumes** (0.720 at 200k, 0.133 at
   2M, against ~0.06 for the others). The basin is set by initialization
   and data order, and more data does not lift it out. Whether it is a
   basin of the 0.84M architecture or of this seed is a question for the
   size axis and for more seeds — both are the next runs.
4. **The growth with k persists but flattens**: ×10–15 from k = 1 to 7 at
   2M against ×20–30 at 200k. More data buys more at long prefixes than at
   short ones, as it should if the failure is integrating many bound names.

Consequence for the protocol: the ten-cell sweep is repeated at 2M
windows (launched now, GPU, ~11 h), and the model-size axis (d = 64, 256)
at r1 ε=1 follows it. The 200k sweep stands as the low-data row of the
data axis, not as the ladder.

## 10. The ten-cell sweep at 2M windows (appended 2026-09-19 07:34 PDT, from `date`)

Overnight (2026-09-18 15:00 → 20:01, GPU through the lease, babysat; all 30
runs evaluated by 20:13; raws `learner-eval-<cell>-2M-seed<s>-2026-09-18.json`,
manifests `c1prime-loop-40-8-2-*-<run id>.json` with train = 2,000,000).
Structural excess at k = 7, bits per record, with the per-field split
pooled over seeds and the 200k-window pooled value beside:

| cell | seeds 1 / 2 / 3 | pooled | between-seed sd | KIND | ACTOR | OBJECT | RELATED | LINEAGE | 200k pooled |
|---|---|---|---|---|---|---|---|---|---|
| r0 ε=1 | 0.005 / 0.005 / 0.005 | **0.005** | 0.000 | 0.005 | — | — | — | — | 0.015 |
| r0 ε=1/2 | 0.006 / 0.005 / 0.005 | **0.005** | 0.001 | 0.005 | — | — | — | — | 0.018 |
| r1 ε=1 | 0.064 / 0.063 / 0.052 | **0.060** | 0.007 | 0.021 | 0.038 | — | — | — | 0.270 |
| r1 ε=1/2 | 0.079 / 0.099 / 0.090 | **0.089** | 0.010 | 0.034 | 0.056 | — | — | — | 0.331 |
| r2 ε=1 | 0.079 / 0.089 / 0.120 | **0.096** | 0.021 | 0.028 | 0.051 | 0.017 | — | — | 0.368 |
| r2 ε=1/2 | 0.140 / 0.097 / 0.132 | **0.123** | 0.023 | 0.039 | 0.067 | 0.017 | — | — | 0.433 |
| r3 ε=1 | 0.059 / 0.061 / 0.058 | **0.059** | 0.001 | 0.019 | 0.027 | 0.007 | 0.005 | — | 0.377 |
| r3 ε=1/2 | 0.088 / 0.094 / 0.095 | **0.092** | 0.003 | 0.030 | 0.046 | 0.010 | 0.007 | 0.000 | 0.385 |
| r4 ε=1 | 0.056 / 0.133 / 0.065 | **0.085** | 0.042 | 0.026 | 0.038 | 0.010 | 0.011 | 0.001 | 0.491 |
| r4 ε=1/2 | 0.239 / 0.101 / 0.096 | **0.145** | 0.081 | 0.040 | 0.050 | 0.038 | 0.017 | 0.001 | 0.753 |

Per-position curves, pooled:

| cell | k=1 | k=2 | k=3 | k=4 | k=5 | k=6 | k=7 | k=7 / k=1 |
|---|---|---|---|---|---|---|---|---|
| r0 ε=1 | 0.000 | 0.001 | 0.001 | 0.001 | 0.002 | 0.003 | 0.005 | 10 |
| r0 ε=1/2 | 0.001 | 0.001 | 0.001 | 0.002 | 0.002 | 0.003 | 0.005 | 9 |
| r1 ε=1 | 0.006 | 0.010 | 0.012 | 0.017 | 0.024 | 0.037 | 0.060 | 11 |
| r1 ε=1/2 | 0.008 | 0.015 | 0.019 | 0.025 | 0.037 | 0.061 | 0.089 | 11 |
| r2 ε=1 | 0.009 | 0.015 | 0.020 | 0.030 | 0.045 | 0.065 | 0.096 | 11 |
| r2 ε=1/2 | 0.009 | 0.018 | 0.024 | 0.037 | 0.060 | 0.092 | 0.123 | 14 |
| r3 ε=1 | 0.013 | 0.018 | 0.024 | 0.028 | 0.036 | 0.044 | 0.059 | 5 |
| r3 ε=1/2 | 0.014 | 0.025 | 0.031 | 0.040 | 0.055 | 0.073 | 0.092 | 6 |
| r4 ε=1 | 0.013 | 0.027 | 0.039 | 0.042 | 0.053 | 0.061 | 0.085 | 6 |
| r4 ε=1/2 | 0.016 | 0.057 | 0.080 | 0.077 | 0.103 | 0.113 | 0.145 | 9 |

Readings, in decreasing confidence:

1. **The learner-side ladder at 2M is not the exact side's ladder.** At
   ε = 1: r0 0.005 < r1 0.060 ≈ r3 0.059 < r4 0.085 < r2 0.096. r3 costs the
   learner no more than r1 (sd 0.001 and 0.007 — resolved); r2 costs more
   than either (sd 0.021; pooled se 0.012 — resolved against r1 and r3 at
   two standard errors, not three). Exposing the OBJECT field (r1 → r2)
   makes the learner *worse*; exposing RELATED on top of it (r2 → r3)
   makes it *better* again, back to r1's level. The exact observer's
   ceilings fall monotonically down the same ladder. The interface that
   helps the Bayesian observer most per bit is not the one the learner
   handles best.
2. **Where the excess sits is stable across data volume**: ACTOR is the
   largest field at every content rung, KIND second, and the OBJECT
   field's own term at r2 (≈ 0.02) does not account for r2's extra cost —
   it is paid on KIND and ACTOR. Seeing the lock makes the learner worse
   at predicting who acts and what happens.
3. **ε = ½ costs the learner more than ε = 1 at every content rung**
   (0.089 vs 0.060 at r1; 0.092 vs 0.059 at r3), resolved at r1 and r3
   (sds ≤ 0.010); equal at r0 (0.005 both); unresolved at r2 and r4. The
   live cursor lowers every ceiling and, where resolved, raises the
   learner's excess.
4. **The two cells with large between-seed spread are r4 ε=1 and r4 ε=½,
   both carried by one outlier seed** (§9.3). r4's pooled value is not a
   property of the rung until more seeds separate the basin question from
   the interface question.
5. Growth with k persists at 2M in every cell, ×5–14 from k = 1 to 7
   against ×18–33 at 200k — and it is the rungs with more visible fields
   (r3, r4: ×5–6) that grow least, r1 and r2 (×11–14) most. §7.2's
   reading stands with that refinement.

The 200k sweep (§2) is the low-data row of the data axis; this table is
the one the interface question is read from, at this model size.

## 11. The model-size axis at 2M windows, r1 ε=1 (appended 2026-09-19 07:40 PDT, from `date`)

Same corpus, same recipe (AdamW, lr 1e-3 peak, warmup 500, cosine to 1e-4, batch 256, 5 epochs),
4 layers and 4 heads throughout; only the width changes. Raws `learner-eval-r1-eps1-2M-d{64,256}-seed*-2026-09-18.json`
(d = 128 is §9's row).

| width | parameters | seeds 1 / 2 / 3 | pooled | sd | KIND | ACTOR | naming | final val loss (nats/token) | curve k = 1..7 |
|---|---|---|---|---|---|---|---|---|---|
| d = 64 | 222,940 | 0.155 / 0.121 / 0.120 | **0.132** | 0.020 | 0.048 | 0.085 | 0.0033 | 0.6166 | 0.011 / 0.018 / 0.024 / 0.036 / 0.057 / 0.086 / 0.132 |
| d = 128 | 838,940 | 0.064 / 0.063 / 0.052 | **0.060** | 0.007 | 0.021 | 0.038 | 0.0026 | 0.6119 | 0.006 / 0.010 / 0.012 / 0.017 / 0.024 / 0.037 / 0.060 |
| d = 256 | 3,250,588 | 0.155 / 0.156 / 0.094 | **0.135** | 0.036 | 0.091 | 0.044 | 0.0042 | 0.6173 | 0.005 / 0.027 / 0.033 / 0.052 / 0.070 / 0.083 / 0.135 |

Readings:

1. **Not monotone in size at a fixed recipe.** d = 64 (223k) sits at 0.132,
   d = 128 (839k) at 0.060, d = 256 (3.25M) back at 0.135 — with its
   validation loss the worst of the three and its excess moved into the
   KIND field (0.091 against 0.021 at d = 128). A four-fold wider model
   trained with the same learning rate and schedule is not the same
   experiment at a different point on the axis; it is an untuned model.
   The size axis is **not read** from this table. It is owed a
   learning-rate sweep per width (and, at d = 256, more steps) before any
   capacity claim is made; until then §9–10's numbers are a statement about
   one architecture, not about scale.
2. What survives the confound: at every width the curve rises with k
   (×12, ×11, ×27), the naming rule is learned (≤ 0.005), and ACTOR or KIND
   is the field that carries the excess.

## 12. State at handoff (2026-09-19 07:40 PDT)

Everything above is committed and stamped; the GPU is free; no job is
running. The learner-side questions open for the next instance, in the
order I would take them: (a) the headline — the non-monotone
learner-side ladder of §10 or the growth with context of §7/§10, and
whether either needs more seeds at r2 and r4 first; (b) the size axis
done properly (lr sweep per width) before RQ5 is touched; (c) the probes
(sub-project 3) against the full-window tables. The 200k sweep (§2) is
the low-data row of the data axis, not the ladder.

## 13. The window census: what the k = 7 mean hides (appended 2026-09-21 12:20 PDT, from `date`, by the instance of 2026-09-21)

The question was frivolous on its face — *which single window does the
model get most wrong, and what is in it?* — and its literal answer is
null, which is the finding. One evaluator pass per run at k = 7 over the
test split (`scripts/learner_window_census.py`, the evaluator's new
`on_window` callback; per-window rows under `~/.cache/yupi-scratch/census/`,
sha256 in the raws `learner-window-census-<cell>-2M-seed<s>-2026-09-21.json`;
the cuts in `learner-window-census-cuts-2026-09-21.json` from
`scripts/learner_census_cuts.py`), for the ε = 1 ladder cells r1, r2, r3 at
all three seeds. Every census mean reproduces its §10 aggregate to four
decimals.

**13.1 The per-window distribution is realization noise, not a tail of hard
situations.** Per window, the structural excess is the realized-record
estimate log₂ P*(ρ) − log₂ P̃_M(ρ) for the one record that occurred; it is
negative on 40–43 % of windows in every cell, its median is 0.01–0.04 bits
against means of 0.05–0.12, its 99th percentile is 1.1–1.9 bits, and the
top 1 % of windows carry 24–36 % of the total. That looks like a tail of
hard cases. It is not: the one-way variance split by ceiling-table class
(25,005 / 28,722 / 32,584 classes at r1 / r2 / r3, of which 13–15 k hold two
or more windows) puts only 15–26 % of the per-window variance between
classes; 74–85 % is within-class, i.e. the spread of the realized record
under P* plus whatever the model does with the names. The worst windows
(6–15 bits) are windows where a low-P* record happened and the model had
put even less on it. A "hardest window" is not a property of the model at
this grain. (The class grain is too fine to read directly: ~3 windows per
class.)

**13.2 At the grain of the predicted record's kind, the r2 penalty sits on
lock contention.** Attributing each cell's total to the kind of the record
being predicted (a signed decomposition of the estimator's sum — shares add
to one, but a kind's mean conditions on the outcome and is not a KL, so it
may be negative, as IO_COMPLETE is at r2 seed 2):

| cell | seed | n | mean | classes | between share (ANOVA) | BLOCK+ACQUIRE share | share by predicted kind: DISPATCH / RELEASE / BLOCK / ACQUIRE / IO_ISSUE / IO_COMPLETE / STEP |
|---|---|---|---|---|---|---|---|
| r1 ε=1 | 1 | 84949 | 0.064 | 25005 | 0.17 | **0.29** | 0.23 / 0.09 / 0.17 / 0.12 / 0.14 / 0.09 / 0.17 |
| r1 ε=1 | 2 | 84949 | 0.063 | 25005 | 0.20 | **0.35** | 0.21 / 0.10 / 0.18 / 0.17 / 0.19 / 0.07 / 0.08 |
| r1 ε=1 | 3 | 84949 | 0.052 | 25005 | 0.15 | **0.45** | 0.22 / 0.21 / 0.31 / 0.14 / 0.03 / 0.09 / -0.00 |
| r2 ε=1 | 1 | 84987 | 0.079 | 28722 | 0.18 | **0.47** | 0.14 / 0.11 / 0.36 / 0.11 / 0.09 / 0.15 / 0.05 |
| r2 ε=1 | 2 | 84987 | 0.089 | 28722 | 0.16 | **0.44** | 0.24 / 0.18 / 0.25 / 0.19 / 0.11 / -0.04 / 0.07 |
| r2 ε=1 | 3 | 84987 | 0.120 | 28722 | 0.24 | **0.49** | 0.21 / 0.16 / 0.29 / 0.20 / 0.06 / 0.03 / 0.05 |
| r3 ε=1 | 1 | 84955 | 0.059 | 32584 | 0.19 | **0.30** | 0.11 / 0.34 / 0.17 / 0.14 / 0.17 / 0.07 / 0.01 |
| r3 ε=1 | 2 | 84955 | 0.061 | 32584 | 0.26 | **0.50** | 0.09 / 0.16 / 0.32 / 0.18 / 0.11 / 0.11 / 0.03 |
| r3 ε=1 | 3 | 84955 | 0.058 | 32584 | 0.24 | **0.41** | 0.15 / 0.19 / 0.31 / 0.10 / 0.09 / 0.06 / 0.10 |


Mean excess on the lock-contention records (BLOCK: a thread blocks on a
held lock; ACQUIRE: it takes a free one), with the field split, beside
RELEASE and DISPATCH:

|---|---|---|---|---|---|---|
| r1 ε=1 | 1 | 0.086 (0.02 / 0.06 / 0.00) | 0.071 (0.02 / 0.05 / 0.00) | 0.031 | 0.036 | 0.19 (0.14) |
| r1 ε=1 | 2 | 0.092 (0.03 / 0.06 / 0.00) | 0.099 (0.04 / 0.05 / 0.00) | 0.033 | 0.034 | 0.23 (0.14) |
| r1 ε=1 | 3 | 0.128 (0.07 / 0.06 / 0.00) | 0.067 (0.03 / 0.04 / 0.00) | 0.058 | 0.028 | 0.19 (0.14) |
| r2 ε=1 | 1 | 0.224 (0.10 / 0.07 / 0.06) | 0.083 (0.01 / 0.05 / 0.03) | 0.047 | 0.027 | 0.13 (0.14) |
| r2 ε=1 | 2 | 0.175 (0.03 / 0.07 / 0.07) | 0.160 (0.07 / 0.06 / 0.03) | 0.088 | 0.055 | 0.22 (0.14) |
| r2 ε=1 | 3 | 0.272 (0.07 / 0.10 / 0.10) | 0.227 (0.12 / 0.07 / 0.04) | 0.103 | 0.064 | 0.15 (0.14) |
| r3 ε=1 | 1 | 0.077 (-0.01 / 0.05 / 0.03) | 0.076 (0.02 / 0.04 / 0.02) | 0.108 | 0.016 | 0.12 (0.14) |
| r3 ε=1 | 2 | 0.154 (0.05 / 0.05 / 0.04) | 0.104 (0.05 / 0.04 / 0.02) | 0.053 | 0.014 | 0.19 (0.14) |
| r3 ε=1 | 3 | 0.145 (0.05 / 0.05 / 0.03) | 0.055 (-0.00 / 0.04 / 0.02) | 0.060 | 0.023 | 0.27 (0.14) |


The seed-to-seed swing in shares is large (the totals are small and the
per-kind sums signed), so the reading is taken from the *gap* between rungs:
each kind's contribution frac_kind × (mean_r2 − mean_other) to the r2 − r1
and r2 − r3 differences in total excess, per seed and pooled (mean ± sd
over seeds; contributions sum to the gap):

|---|---|---|---|---|---|---|---|---|
| r2-r1 eps=1 | +0.036 (+0.015, +0.026, +0.068) | +0.006 ± 0.009 | +0.007 ± 0.004 | +0.015 ± 0.004 | +0.008 ± 0.008 | +0.000 ± 0.004 | -0.001 ± 0.007 | +0.001 ± 0.007 |
| r2-r3 eps=1 | +0.037 (+0.020, +0.029, +0.062) | +0.012 ± 0.007 | +0.001 ± 0.011 | +0.012 ± 0.009 | +0.008 ± 0.009 | +0.001 ± 0.003 | -0.001 ± 0.009 | +0.003 ± 0.002 |

Readings, in decreasing confidence:

1. **BLOCK is the one kind whose contribution to the r2 − r1 gap is
   resolved across seeds**: +0.015 ± 0.004 of +0.036, with BLOCK's mean
   excess at r2 (0.18–0.27) above r1 (0.09–0.13) at every seed and the
   excess spread over the kind, actor and object fields. BLOCK and ACQUIRE
   together carry about two-thirds of the r2 − r1 gap. The remaining third
   is diffuse and mostly the outlier seed 3, whose extra 0.04–0.05 bits sit
   on every kind — the seed question of §10 reading 4 is still open and
   still owed more seeds.
2. Against r3 the picture is less resolved (BLOCK +0.012 ± 0.009,
   DISPATCH +0.012 ± 0.007); BLOCK's mean at r3 (0.08–0.15) is below r2 at
   every seed and the two ranges do not overlap; the pooled sd comes from the other kinds.
3. **Mechanism, as a hypothesis for the probes, not a claim.** At r2 the
   surface names the lock but not its owner; to predict a BLOCK (and on
   whom, and on which lock) the model must have tracked ownership from
   earlier ACQUIRE / RELEASE records. At r3 the RELATED field prints the
   owner on every BLOCK and the woken thread on every RELEASE, and the
   BLOCK excess falls even though the model now predicts one field more.
   That is consistent with the learner paying not for bits of interface
   but for state it must compute unassisted — inferred ownership is what
   it fails at; given ownership it handles. The probe that tests this is
   the one already planned (sub-project 3): is lock ownership linearly
   present in the residual stream at r2, and is it less present than at
   r3? A cheaper first check is exact: split the r2 BLOCK windows by
   whether the observer's posterior on the blocked lock's owner is
   concentrated or spread, and see whether the model's BLOCK excess
   tracks that.
4. Fresh-actor records (14 % of windows) carry 12–27 % of each cell's
   total — modestly over their share, not consistently across seeds; not a
   headline.

What this does not say: nothing about r4 or ε = ½ (not censused), nothing
about the canonical observer, and the per-kind means are attributions of
a realized-record sum, not per-kind KLs. §10 reading 2 ("the OBJECT
field's own term does not account for r2's extra cost — it is paid on KIND
and ACTOR") stands, with the refinement that the KIND and ACTOR excess is
paid on the lock-contention records.

## 14. Six seeds at r2 and r4, ε = 1 (appended 2026-09-22 10:16 PDT, from `date`, by the instance of 2026-09-21)

Seeds 4–6 at r2 ε=1 and r4 ε=1, same corpora and recipe as seeds 1–3
(2M windows, 5 epochs, d = 128), trained 2026-09-21 12:33–14:02 PDT through
the lease (12–13 min per run on the 4090), evaluated k = 1..7; raws
`learner-eval-{r2,r4}-eps1-2M-seed{4,5,6}-2026-09-21.json`. Tables from
`scripts/learner_summary.py` over the six raws of each cell:

| cell | seed | step | n | structural (bits) ± se | naming ± se | kind KL | end | token |
|---|---|---|---|---|---|---|---|---|
| r2 eps=1 | 1 | 39065 | 84987 | 0.0790 ± 0.0014 | 0.0030 ± 0.0003 | 0.0226 | 0.0000 | 0.0820 |
| r2 eps=1 | 2 | 39065 | 84987 | 0.0894 ± 0.0015 | 0.0037 ± 0.0004 | 0.0269 | 0.0001 | 0.0931 |
| r2 eps=1 | 3 | 39065 | 84987 | 0.1201 ± 0.0017 | 0.0041 ± 0.0004 | 0.0322 | 0.0000 | 0.1242 |
| r2 eps=1 | 4 | 39065 | 84987 | 0.0804 ± 0.0014 | 0.0034 ± 0.0004 | 0.0224 | 0.0001 | 0.0838 |
| r2 eps=1 | 5 | 39065 | 84987 | 0.0758 ± 0.0014 | 0.0031 ± 0.0004 | 0.0230 | 0.0000 | 0.0789 |
| r2 eps=1 | 6 | 39065 | 84987 | 0.0740 ± 0.0014 | 0.0035 ± 0.0003 | 0.0204 | 0.0001 | 0.0775 |

| cell | seeds | structural mean | between-seed sd | pooled se | within-seed se | seeds for se ≤ δ/3 | naming mean | kind KL | end |
|---|---|---|---|---|---|---|---|---|---|
| r2 eps=1 | 6 | 0.0864 | 0.0173 | 0.0071 | 0.0015 | 27 | 0.0035 | 0.0246 | 0.0001 |


| cell | seed | k=1 | k=2 | k=3 | k=4 | k=5 | k=6 | k=7 |
|---|---|---|---|---|---|---|---|---|
| r2 eps=1 | 1 | 0.0080 | 0.0144 | 0.0185 | 0.0264 | 0.0381 | 0.0532 | 0.0790 |
| r2 eps=1 | 2 | 0.0083 | 0.0150 | 0.0192 | 0.0260 | 0.0403 | 0.0608 | 0.0894 |
| r2 eps=1 | 3 | 0.0096 | 0.0167 | 0.0231 | 0.0362 | 0.0564 | 0.0811 | 0.1201 |
| r2 eps=1 | 4 | 0.0094 | 0.0138 | 0.0187 | 0.0258 | 0.0386 | 0.0534 | 0.0804 |
| r2 eps=1 | 5 | 0.0092 | 0.0141 | 0.0192 | 0.0250 | 0.0370 | 0.0521 | 0.0758 |
| r2 eps=1 | 6 | 0.0086 | 0.0129 | 0.0173 | 0.0239 | 0.0338 | 0.0466 | 0.0740 |


| cell | seed | step | n | structural (bits) ± se | naming ± se | kind KL | end | token |
|---|---|---|---|---|---|---|---|---|
| r4 eps=1 | 1 | 39065 | 84972 | 0.0563 ± 0.0012 | 0.0038 ± 0.0003 | 0.0151 | 0.0000 | 0.0601 |
| r4 eps=1 | 2 | 39065 | 84972 | 0.1331 ± 0.0018 | 0.0046 ± 0.0004 | 0.0425 | 0.0001 | 0.1377 |
| r4 eps=1 | 3 | 39065 | 84972 | 0.0655 ± 0.0013 | 0.0037 ± 0.0004 | 0.0179 | 0.0001 | 0.0692 |
| r4 eps=1 | 4 | 39065 | 84972 | 0.0537 ± 0.0011 | 0.0028 ± 0.0003 | 0.0163 | 0.0001 | 0.0565 |
| r4 eps=1 | 5 | 39065 | 84972 | 0.0862 ± 0.0014 | 0.0037 ± 0.0004 | 0.0253 | 0.0000 | 0.0899 |
| r4 eps=1 | 6 | 39065 | 84972 | 0.0599 ± 0.0012 | 0.0036 ± 0.0003 | 0.0171 | 0.0000 | 0.0634 |

| cell | seeds | structural mean | between-seed sd | pooled se | within-seed se | seeds for se ≤ δ/3 | naming mean | kind KL | end |
|---|---|---|---|---|---|---|---|---|---|
| r4 eps=1 | 6 | 0.0758 | 0.0304 | 0.0124 | 0.0013 | 84 | 0.0037 | 0.0224 | 0.0001 |


| cell | seed | k=1 | k=2 | k=3 | k=4 | k=5 | k=6 | k=7 |
|---|---|---|---|---|---|---|---|---|
| r4 eps=1 | 1 | 0.0128 | 0.0196 | 0.0256 | 0.0287 | 0.0364 | 0.0406 | 0.0563 |
| r4 eps=1 | 2 | 0.0139 | 0.0430 | 0.0647 | 0.0663 | 0.0844 | 0.0964 | 0.1331 |
| r4 eps=1 | 3 | 0.0136 | 0.0184 | 0.0266 | 0.0303 | 0.0395 | 0.0467 | 0.0655 |
| r4 eps=1 | 4 | 0.0126 | 0.0182 | 0.0237 | 0.0260 | 0.0326 | 0.0413 | 0.0537 |
| r4 eps=1 | 5 | 0.0138 | 0.0202 | 0.0319 | 0.0375 | 0.0515 | 0.0624 | 0.0862 |
| r4 eps=1 | 6 | 0.0130 | 0.0185 | 0.0253 | 0.0288 | 0.0394 | 0.0447 | 0.0599 |


Readings, in decreasing confidence:

1. **r2 > r1 ≈ r3 is resolved without the outlier.** Five of the six r2
   seeds lie in 0.074–0.089 (mean 0.080, sd 0.006 with seed 3 dropped;
   0.086 ± 0.017 with it); the lowest r2 seed (0.074) is above the highest
   r1 seed (0.064) and the highest r3 seed (0.061). Exposing the OBJECT
   field costs this learner about 0.02 bits per record at k = 7 relative
   to r1, and §13 locates most of that on BLOCK and ACQUIRE records. The
   §10 reading 1 ladder stands: r0 0.005 < r1 0.060 ≈ r3 0.059 < r2.
2. **r4 is not a one-basin cell.** Four of six seeds land at 0.054–0.066,
   inside the r1 / r3 range; two land high (seed 2 at 0.133, seed 5 at
   0.086), and their per-position curves are elevated from k = 2–3 onward,
   not late — a different solution from early training, not a late
   divergence. r4's pooled value (0.076 ± 0.030) is therefore a mixture,
   and its place on the ladder is "r1's level, with a worse basin the
   optimizer finds one time in three." Where r4 sits relative to r2 is
   not a question with a single answer at this recipe.
3. The between-seed sd at r2 (0.006 without seed 3) and at r1 / r3
   (0.001–0.007) is now the binding resolution for ladder claims between
   those rungs; r4's (0.013 without its top seed) is not.

What this does not say: nothing about ε = ½ (three seeds), nothing about
whether the r4 basins are a property of the rung or of the recipe (a
learning-rate or warmup change could remove or multiply them), and nothing
about why seed 3 at r2 is high — its census (§13) put its extra cost on
every kind.
