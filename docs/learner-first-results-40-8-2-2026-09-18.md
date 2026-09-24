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

## 15. The r4 basins by kind (appended 2026-09-22 10:22 PDT, from `date` in the writing command, by the instance of 2026-09-21)

Census (§13's instrument) of all six r4 ε=1 seeds at k = 7; raws
`learner-window-census-r4-eps1-2M-seed{1..6}-2026-09-22.json`, cuts and
the seed-group contrast in `learner-window-census-cuts-r4-2026-09-22.json`
(`scripts/learner_census_cuts.py --contrast "high=2,5 low=1,3,4,6"`).

| cell | seed | n | mean | classes | between share (ANOVA) | BLOCK+ACQUIRE share | share by predicted kind: DISPATCH / RELEASE / BLOCK / ACQUIRE / IO_ISSUE / IO_COMPLETE / STEP |
|---|---|---|---|---|---|---|---|
| r4 ε=1 | 1 | 84972 | 0.056 | 32755 | 0.20 | **0.34** | 0.19 / 0.25 / 0.19 / 0.15 / 0.10 / -0.01 / 0.13 |
| r4 ε=1 | 2 | 84972 | 0.133 | 32755 | 0.32 | **0.48** | 0.18 / 0.24 / 0.31 / 0.17 / 0.06 / -0.02 / 0.06 |
| r4 ε=1 | 3 | 84972 | 0.065 | 32755 | 0.21 | **0.51** | 0.12 / 0.21 / 0.35 / 0.16 / 0.06 / 0.08 / 0.02 |
| r4 ε=1 | 4 | 84972 | 0.054 | 32755 | 0.18 | **0.32** | 0.13 / 0.39 / 0.19 / 0.13 / 0.03 / 0.09 / 0.04 |
| r4 ε=1 | 5 | 84972 | 0.086 | 32755 | 0.27 | **0.40** | 0.20 / 0.12 / 0.24 / 0.16 / 0.19 / 0.06 / 0.03 |
| r4 ε=1 | 6 | 84972 | 0.060 | 32755 | 0.23 | **0.45** | 0.14 / 0.04 / 0.25 / 0.20 / 0.25 / 0.13 / -0.02 |

| cell | seed | mean on BLOCK (kind / actor / obj) | mean on ACQUIRE (kind / actor / obj) | mean on RELEASE | mean on DISPATCH | fresh-actor share (frac of windows) |

| r4 ε=1 | 1 | 0.088 (-0.00 / 0.05 / 0.03) | 0.081 (0.02 / 0.04 / 0.02) | 0.074 | 0.027 | 0.20 (0.14) |
| r4 ε=1 | 2 | 0.331 (0.08 / 0.09 / 0.08) | 0.213 (0.10 / 0.09 / 0.03) | 0.174 | 0.060 | 0.17 (0.14) |
| r4 ε=1 | 3 | 0.187 (0.08 / 0.06 / 0.03) | 0.097 (0.02 / 0.06 / 0.02) | 0.075 | 0.019 | 0.18 (0.14) |
| r4 ε=1 | 4 | 0.083 (0.01 / 0.04 / 0.03) | 0.066 (0.01 / 0.04 / 0.02) | 0.112 | 0.018 | 0.15 (0.14) |
| r4 ε=1 | 5 | 0.167 (0.03 / 0.07 / 0.05) | 0.133 (0.04 / 0.07 / 0.02) | 0.054 | 0.043 | 0.15 (0.14) |
| r4 ε=1 | 6 | 0.121 (0.03 / 0.05 / 0.03) | 0.116 (0.06 / 0.04 / 0.02) | 0.013 | 0.021 | 0.26 (0.14) |

| gap | total gap (per seed) | DISPATCH | RELEASE | BLOCK | ACQUIRE | IO_ISSUE | IO_COMPLETE | STEP |

| frac × Δmean by predicted kind | +0.051 | +0.012 | +0.009 | +0.016 | +0.009 | +0.005 | -0.003 | +0.003 |

Readings:

1. **The high basin is a general degradation with lock contention
   over-represented, not a lock-only failure.** Of the +0.051 bits between
   the two high seeds and the four low ones, BLOCK carries +0.016 (31 % of
   the gap on 13 % of windows) and ACQUIRE +0.009; DISPATCH (+0.012) and
   RELEASE (+0.009) carry nearly as much between them. Seed 2's BLOCK mean
   (0.331) is the largest per-kind excess in any cell censused so far, and
   its excess on BLOCK is spread over kind, actor and object alike.
2. This is consistent with §13's ownership hypothesis and does not confirm
   it: the high basin pays most on the records that need lock state, but
   it also pays on DISPATCH and RELEASE, where ownership is not what is
   being predicted. A basin that had failed only at ownership tracking
   would not look like this. The probe question stands as the test.
3. Between-class variance share is higher in the high seeds (0.32, 0.27)
   than the low ones (0.18–0.23): a worse model is more class-dependent,
   as it should be — the classes it fails on become visible above the
   realization noise.
4. Within the low group, seed 3 has an r2-like BLOCK mean (0.187) at an
   r1-like total (0.065): the per-kind composition varies between seeds
   even when the total does not.

## 16. Probe v0.1–v0.3: lock ownership in the residual stream (appended 2026-09-23 13:39 PDT, from `date` in the writing command, by the instance of 2026-09-21)

Sub-project 3's first target, motivated by §13–15. Design and amendments:
`docs/superpowers/specs/2026-09-23-probe-lock-owner-design.md`. Exact
owner posteriors P*(Z | prefix) for every lock visible after k = 7 records
(`yupi.learner.probe.owner_posterior` over the pattern filter's joint
belief on (state, binding); `scripts/learner_probe_labels.py`; val split
for fitting, first 30k test windows for evaluation), probes fit per layer
from the residual stream at the record-boundary position p0 (the state
after k records), scored by OIR = (H(Z) − CE) / (H(Z) − H(Z | h)) (proposal
§8.3), λ chosen on a held-out fifth of the fit split. Raws
`learner-probe-owner-<cell>-seed<s>[-<target>]-2026-09-23.json`; tables
from `scripts/learner_probe_summary.py` (lock index 0; lock 1 agrees).

**16.1 Two dead ends, and what each showed.** (a) The v0.1 probe, an
affine map to the pattern observer's classes {none, t0..t3, unseen}, scores
0.36 / 0.43 / 0.39 at r2 / r3 / r4 (table below) — but a control with the
same family on Z′ = pattern index of the actor of record k, a fact the model
has just read, scores 0.15 (r2 seed 1, layers 3–4). First-appearance
indices are not the model's coordinates; v0.1's owner numbers do not
measure ownership. (b) The v0.2 readout decodes the owner as a thread
*token* through the model's own embedding matrix (bilinear, learned
directions for none / unseen). Thread embeddings are not collapsed
(pairwise cosine ≈ 0.05; nearest-embedding decode of E_t + pos_p 88 %),
and at the actor token's own input position the readout recovers the actor
with held-out CE 0.002 at layers 0 and 3. At p0, three positions later, it
recovers nothing on the same control (held-out CE at baseline for every λ;
train CE falls, so it memorizes). **Entity identities are fetched by
attention when needed, not held in the stream at the record boundary.** A
single-position probe cannot read "which thread owns lock l" at any rung.
(An off-by-three in the first diagnostic — window index p0 − 4 is the
actor, its *input* position is p0 − 3 — was caught before it was read.)

**16.2 The fact in coordinate-free form.** Folding the owner posterior into
Z = held (is lock l owned by anyone) and Z = owner-is-actor (is its owner
the thread that just acted), linear readout at p0, best layer of 1–4:

| cell | target | readout | seeds | best-layer OIR per seed | pooled OIR ± sd | layer(s) | CE determined subset | H(Z|h) | acc |
|---|---|---|---|---|---|---|---|---|---|
| r2-eps1 | held | linear | 3 | 0.56 / 0.58 / 0.56 | **0.57** ± 0.01 | 3,3,4 | 0.268 (0.260–0.272) | 0.100 | 0.88 |
| r3-eps1 | held | linear | 3 | 0.76 / 0.82 / 0.78 | **0.79** ± 0.03 | 3,2,2 | 0.168 (0.145–0.187) | 0.000 | 0.95 |
| r4-eps1 | held | linear | 6 | 0.74 / 0.72 / 0.74 / 0.73 / 0.73 / 0.75 | **0.73** ± 0.01 | 2,2,3,3,2,3 | 0.210 (0.196–0.221) | 0.000 | 0.94 |

| cell | target | readout | seeds | best-layer OIR per seed | pooled OIR ± sd | layer(s) | CE determined subset | H(Z|h) | acc |
|---|---|---|---|---|---|---|---|---|---|
| r2-eps1 | owner-is-actor | linear | 3 | 0.45 / 0.47 / 0.44 | **0.46** ± 0.02 | 3,3,4 | 0.677 (0.663–0.693) | 0.173 | 0.73 |
| r3-eps1 | owner-is-actor | linear | 3 | 0.55 / 0.58 / 0.51 | **0.55** ± 0.03 | 3,2,2 | 0.653 (0.610–0.701) | 0.000 | 0.80 |
| r4-eps1 | owner-is-actor | linear | 6 | 0.57 / 0.50 / 0.54 / 0.56 / 0.51 / 0.56 | **0.54** ± 0.03 | 3,4,4,3,2,4 | 0.660 (0.622–0.714) | 0.000 | 0.80 |

v0.1 (pattern classes, lock 0):
| cell | target | readout | seeds | best-layer OIR per seed | pooled OIR ± sd | layer(s) | CE determined subset | H(Z|h) | acc |
|---|---|---|---|---|---|---|---|---|---|
| r2-eps1 | owner | linear | 3 | 0.36 / 0.37 / 0.35 | **0.36** ± 0.01 | 3,3,4 | 1.536 (1.506–1.553) | 0.234 | 0.51 |
| r3-eps1 | owner | linear | 3 | 0.43 / 0.44 / 0.44 | **0.43** ± 0.01 | 3,2,3 | 1.277 (1.260–1.294) | 0.000 | 0.61 |
| r4-eps1 | owner | linear | 6 | 0.38 / 0.36 / 0.40 / 0.40 / 0.37 / 0.40 | **0.39** ± 0.02 | 3,2,3,3,2,3 | 1.383 (1.342–1.434) | 0.000 | 0.58 |

Readings:

1. **"Is the lock held" is less accessible at r2 than at r3 or r4**: OIR
   0.57 ± 0.01 against 0.79 ± 0.03 and 0.73 ± 0.01, seeds tightly clustered,
   best layers 2–4. The cleaner comparison is the cross-entropy on
   the examples the prefix *determines* (H(Z | h) = 0 for the example): r2
   0.27 against r3 0.17 and r4 0.21 bits. Where the surface fixes whether
   the lock is held, the r2 model's boundary state carries it less.
2. The same ordering, smaller, for owner-is-actor (0.46 / 0.55 / 0.54).
3. **r4's two basins do not differ in lock-state access**: seeds 2 and 5
   (the high basin, §14–15) score 0.72 and 0.73 on held against 0.73–0.75
   for the low basin. The high basin's extra cost is not less accessible
   lock state at the boundary; the r4 leg of §13's hypothesis fails in this
   form.
4. Caveat on the ceilings: at r3 and r4 every visible lock's owner is
   determined by the prefix (the owner is printed on BLOCK, and ACQUIRE /
   RELEASE are visible), so their OIR measures retention of a printed fact;
   at r2 ownership is uncertain for a third of the (window, lock) examples
   (mean posterior entropy 0.23–0.26 bits) and the OIR measures retention of
   an inferred one. The normalization makes the numbers comparable in units,
   not in kind; reading 1's determined-subset CE is the like-for-like
   comparison.

What this does not say: nothing causal (§8.5 patching is not done); nothing
about *which* thread owns the lock, which needs a probe that reads at the
entity token's position (v0.4, designed but not built); nothing about r1 (no
locks in the pattern observer's names) or ε = ½. The ownership hypothesis
of §13 survives at r2 vs r3 in the form "the boundary state at r2 carries
less of the lock's held/free status, even where the prefix determines it,"
and fails for r4's basins.

## 17. Need, not presence — and the per-window link (appended 2026-09-24 09:09 PDT, from `date` in the writing command, by the instance of 2026-09-23)

§16 measured whether lock state is *present* at the record boundary. This section
asks two companion questions from artifacts that already existed (probe design
amendment v0.4): is the owner *worth holding* for the next record, exactly; and do
the windows where the probe reads the lock's state worst coincide with the windows
where the model over-pays on the record predicted from that same position.

**17.1 Setup.** *Need:* `yupi.learner.probe.next_dist_by_owner` partitions the
ceiling's next-record distribution by the owner class of the support point it came
from; `mutual_information` gives I(next record; owner of l | prefix) = H(P*(next)) −
Σ_z P*(z) H(P*(next | Z = z)), with the owner folded to held / none and the record
coarsened to its kind as variants (`scripts/learner_probe_voi.py`, raws
`learner-probe-voi-<cell>-k7-2026-09-24.json`, per-window rows under
`~/.cache/yupi-scratch/probes/`, sha256 in the raw). Exactness gate: the weighted
mixture of the conditionals equals `next_pattern_dist` as Fractions
(tests/test_learner_probe.py). The same pass records the *relevance* of lock l where
I is zero by construction: P*(record k+1 is on lock l) and P*(it is a BLOCK on l).
*Link:* `scripts/learner_probe_owner.py --per-example` writes each eval example's
soft-label CE on `held` at every layer; `scripts/learner_probe_link.py` joins the
best layer's rows to the window census's per-window excess at k = 7 (§13; the
census scores exactly the record predicted from p0) on the test-window index, and
reports Spearman ρ, the mean excess in the top minus the bottom quartile of probe
CE with a 200-draw permutation null, on all examples, on prefix-determined ones
(probe CE is pure representational error there), on residuals after removing
per-class means (windows of one class share the whole exact side), and between
class means (≥ 3 windows). Raws `learner-probe-link-<cell>-seed<s>-held-2026-09-24.json`;
tables from `scripts/learner_probe_link_summary.py`. Same 30k eval windows, same
labels, same runs as §16.

**17.2 Need.** Per window (summing the visible locks), bits:

| cell | windows | (window, lock) | uncertain share | H(next) | I(next; owner) | I(next; held) | I(kind; owner) | I(kind; held) | uncertain ex.: I(next; owner) / H(owner) | P*(next on lock) | P*(BLOCK on lock) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| r2 | 25508 | 38818 | 0.333 | 1.596 | 0.121 | 0.048 | 0.046 | 0.021 | 0.236 / 0.726 | 0.303 | 0.102 |
| r3 | 25558 | 38926 | 0.000 | 1.520 | 0.000 | 0.000 | 0.000 | 0.000 | — / — | 0.305 | 0.103 |
| r4 | 25566 | 39038 | 0.000 | 1.518 | 0.000 | 0.000 | 0.000 | 0.000 | — / — | 0.308 | 0.105 |

Readings:

1. **At r2 the owner accounts for 0.121 of the ceiling's 1.596 bits of
   next-record entropy per window, 7.6 %.** That is larger than the r2
   model's whole excess at this position (0.074–0.120 bits per record across seeds,
   §14) and three times the r2 − r1 gap (+0.036, §13). The information is not
   negligible to the predictor. It is concentrated: zero on the two thirds of
   (window, lock) examples the prefix determines, 0.236 bits per example on the
   uncertain third (whose owner entropy is 0.726 bits).
2. **Most of the owner's value is *which thread*, not *whether held*:** I(next; held)
   is 0.048 of the 0.121. The identity of the owner carries 0.074 bits per
   window that the held/free bit does not. §16 could only read the held bit at the
   boundary; the thing the predictor would pay most for is the thing a
   single-position probe cannot read (§16.1).
3. **r3 and r4 are exactly zero** (no uncertain example among 39k; the gate the
   amendment asked for). Their ceilings are lower than r2's by 0.076–0.077 bits
   per window with a longer record; the exact side's version of "printing the owner
   removes the uncertainty."
4. **Relevance is a world property, not an interface property:** on every rung,
   30 % of the ceiling's next-record mass is on an event on one of the visible
   locks and 10 % on a BLOCK, to two decimals. Where the owner is determined,
   the state still governs a third of what comes next.

**17.3 Link.** On *all* windows the link is null at every grain. Pooled ρ(probe CE,
excess) is +0.02 to +0.04 at r2 and about zero at r3 and r4; the pooled quartile
gap at r2 (+0.03 to +0.06, p < 0.005) comes from the uncertain third, where probe CE
carries the posterior's own entropy and the excess is higher for the same reason
(0.11–0.16 against 0.07–0.13 bits); on the determined subset it is +0.005 to +0.016
(p 0.10–0.25) except one (lock, seed) pair; after per-class residualization it is
zero in 23 of 24 (lock, seed) pairs across the three cells, and between class means
in 23 of 24. The per-window noise floor is the reason to expect this: the
per-window excess has sd 0.42 bits at r2 and 0.34 at r3/r4 (§13 census raws)
against effects of hundredths, and §13 already found that 75–85 % of it is the
realized record's own spread.

*Post hoc, and marked as such:* restricting to the windows whose realized record
k + 1 is an event on lock l (ACQUIRE, BLOCK or RELEASE; 19–20 % of examples, the
windows where the lock's state is what the prediction turns on) was added after the
null above was read. On those windows (gaps in bits of mean excess, top minus
bottom quartile of probe CE; p from the permutation null; bold at p ≤ 0.025; the
training-count column removes means within 50 bins of log(1 + the class's
frequency among the 1.70M training windows with ≥ 7 records,
`scripts/learner_class_frequency.py`):

| cell | lock | seed | layer | all determined: gap (p) | relevant n | relevant determined: gap (p) | … residual within training-count bins: gap (p) | within class: gap (p) | between classes: ρ (p) |
|---|---|---|---|---|---|---|---|---|---|
| r2-eps1 | 0 | 1 | 3 | +0.005 (0.24) | 4883 | **+0.045** (0.01) | **+0.062** (0.00) | +0.016 (0.20) | -0.064 (0.41) |
| r2-eps1 | 0 | 2 | 3 | +0.011 (0.12) | 4883 | **+0.070** (0.00) | **+0.074** (0.00) | **+0.047** (0.00) | -0.043 (0.74) |
| r2-eps1 | 0 | 3 | 4 | +0.011 (0.12) | 4883 | **+0.098** (0.00) | **+0.132** (0.00) | +0.014 (0.21) | +0.046 (0.19) |
| r2-eps1 | 1 | 1 | 1 | **+0.041** (0.00) | 2757 | **+0.072** (0.00) | **+0.063** (0.01) | -0.016 (0.81) | **+0.224** (0.01) |
| r2-eps1 | 1 | 2 | 3 | +0.016 (0.07) | 2757 | +0.043 (0.10) | +0.027 (0.20) | -0.016 (0.89) | **+0.201** (0.01) |
| r2-eps1 | 1 | 3 | 4 | -0.021 (0.95) | 2757 | +0.043 (0.12) | +0.037 (0.14) | -0.018 (0.79) | +0.157 (0.23) |
| r3-eps1 | 0 | 1 | 3 | -0.031 (1.00) | 4915 | +0.021 (0.11) | +0.024 (0.09) | -0.001 (0.55) | -0.000 (0.79) |
| r3-eps1 | 0 | 2 | 2 | +0.003 (0.27) | 4915 | **+0.066** (0.00) | **+0.035** (0.01) | -0.018 (0.97) | **+0.135** (0.01) |
| r3-eps1 | 0 | 3 | 2 | +0.006 (0.14) | 4915 | **+0.043** (0.00) | +0.011 (0.28) | +0.006 (0.28) | +0.106 (0.21) |
| r3-eps1 | 1 | 1 | 2 | -0.032 (1.00) | 2787 | +0.022 (0.11) | +0.010 (0.34) | +0.001 (0.47) | -0.019 (0.33) |
| r3-eps1 | 1 | 2 | 2 | -0.036 (1.00) | 2787 | -0.018 (0.82) | +0.021 (0.12) | -0.006 (0.76) | +0.028 (0.03) |
| r3-eps1 | 1 | 3 | 2 | -0.036 (1.00) | 2787 | -0.038 (0.98) | -0.008 (0.69) | -0.030 (0.99) | -0.029 (0.82) |
| r4-eps1 | 0 | 1 | 2 | **+0.011** (0.01) | 4898 | +0.027 (0.03) | +0.010 (0.27) | -0.004 (0.58) | +0.001 (0.79) |
| r4-eps1 | 0 | 2 | 2 | -0.060 (1.00) | 4898 | +0.033 (0.08) | +0.019 (0.23) | +0.013 (0.22) | +0.021 (0.14) |
| r4-eps1 | 0 | 3 | 3 | -0.006 (0.82) | 4898 | **+0.040** (0.01) | +0.019 (0.15) | +0.012 (0.20) | +0.047 (0.41) |
| r4-eps1 | 0 | 4 | 3 | -0.000 (0.50) | 4898 | -0.008 (0.73) | **+0.030** (0.01) | -0.014 (0.93) | +0.109 (0.05) |
| r4-eps1 | 0 | 5 | 2 | +0.011 (0.07) | 4898 | -0.003 (0.47) | +0.006 (0.34) | -0.010 (0.71) | -0.105 (0.94) |
| r4-eps1 | 0 | 6 | 3 | +0.009 (0.07) | 4898 | **+0.039** (0.00) | +0.018 (0.12) | -0.026 (0.98) | +0.004 (0.51) |
| r4-eps1 | 1 | 1 | 2 | -0.003 (0.65) | 2888 | **+0.040** (0.02) | **+0.037** (0.01) | -0.008 (0.80) | **+0.187** (0.01) |
| r4-eps1 | 1 | 2 | 2 | -0.048 (1.00) | 2888 | **+0.083** (0.00) | +0.036 (0.09) | +0.005 (0.38) | **+0.131** (0.00) |
| r4-eps1 | 1 | 3 | 2 | -0.008 (0.90) | 2888 | **+0.041** (0.02) | +0.033 (0.04) | -0.014 (0.88) | +0.203 (0.04) |
| r4-eps1 | 1 | 4 | 3 | -0.017 (0.99) | 2888 | **+0.049** (0.00) | +0.028 (0.05) | -0.001 (0.53) | **+0.229** (0.01) |
| r4-eps1 | 1 | 5 | 2 | -0.012 (0.88) | 2888 | -0.033 (0.91) | +0.005 (0.43) | -0.003 (0.57) | -0.002 (0.66) |
| r4-eps1 | 1 | 6 | 2 | +0.005 (0.23) | 2888 | -0.009 (0.71) | +0.017 (0.22) | +0.002 (0.46) | -0.057 (0.89) |

| cell | (lock, seed) pairs | relevant determined gap > 0 | p ≤ 0.025 | … after training-count residualization: gap > 0 | p ≤ 0.025 | within-class p ≤ 0.025 | between-class ρ > 0.1 and p ≤ 0.025 |
|---|---|---|---|---|---|---|---|
| r2-eps1 | 6 | 6 | 4 | 6 | 4 | 1 | 2 |
| r3-eps1 | 6 | 4 | 2 | 5 | 1 | 0 | 1 |
| r4-eps1 | 12 | 8 | 6 | 12 | 2 | 0 | 3 |

Readings on the relevant windows:

5. **At r2 the association is positive in every (lock, seed) pair** on the
   determined relevant windows, +0.043 to +0.098 bits between the top and bottom
   probe-CE quartiles, significant at p ≤ 0.025 in four of six, against mean
   excesses of 0.08–0.17 bits on those windows: the quartile where the boundary
   activation carries the lock's held/free status worst pays roughly half again
   to twice what the best quartile pays. At r4, eight of twelve positive, six
   significant, concentrated on lock 1 in seeds 1–4 (+0.040 to +0.083). At r3,
   four of six positive, two significant, none on lock 1.
6. **It is a between-class association.** Within class it survives in one pair of
   twenty-four. Between class means it is carried by lock 1: ρ = +0.22 / +0.20 /
   +0.16 at r2 (p 0.01, 0.01, 0.23) and +0.19 / +0.13 / +0.20 / +0.23 at r4 seeds
   1–4 (p 0.01, 0.00, 0.04, 0.01), and about zero for lock 0 everywhere. Read plainly: prefix classes
   whose boundary state carries the second lock's status poorly are classes where
   the model over-pays on that lock's next event. The lock 0 / lock 1 asymmetry is
   unexplained here (lock 1 is the later-appearing lock, with fewer examples and,
   at r2, more posterior mass on an unseen owner).
7. **r4's basins do not separate on this either:** seed 2 (high) shows the lock-1
   link, seed 5 (high) shows nothing; low seeds 1, 3, 4 show it and seed 6 does not.

8. **The training-frequency confound runs the other way.** Across the 24 (lock,
   seed) pairs on the relevant determined windows, the class's log training count
   correlates *positively* with probe CE (median ρ +0.09, range −0.06 to +0.20) and
   *negatively* with excess (median −0.08, range −0.15 to +0.03): frequent prefixes
   are predicted better and read *worse* by the linear probe. A shared-difficulty
   story would need both signs the same. Residualizing both sides on 50 bins of
   log count leaves the r2 association intact (6 of 6 positive, 4 significant;
   lock 0 gaps +0.062 / +0.074 / +0.132 at p ≤ 0.005) and the r4 lock-1 gaps
   positive but at p 0.01–0.09; r3 stays null (5 of 6 positive, 1 significant).

**17.4 What this does and does not say.** The need is now quantified: at r2 the
owner is worth 8 % of the ceiling's next-record entropy, more than the model's whole
excess, and most of that value is the owner's identity rather than the held bit;
lock state governs 30 % of the next record's mass on every rung. The presence
deficit of §16 and the excess of §13 co-occur in the same cell, and on the windows
where the lock's state is what the prediction turns on, the windows and classes
where the boundary carries less of it are the ones where the model pays more. None
of this is causal (§8.5 patching is not done). The relevant-window restriction was
chosen after the pre-specified all-window test came back null, and is reported as
exploratory. The probe's CE is a linear lower bound on accessibility, not the
model's operative error. The association lives between classes, so a third variable
that makes a prefix class both harder to represent and harder to predict would
produce it; the obvious candidate, the class's frequency in the training corpus,
is controlled (reading 8) and has the wrong sign to be it. Other class properties
are not controlled. The per-window noise floor (sd 0.34–0.42 bits) means a
within-class effect of a few hundredths would not be seen at this n.

**17.5 What follows, in my order.** (a) The which-thread readout (v0.4 proper) now
has a need argument: 0.073 of the 0.121 bits is identity, which the boundary does
not hold, so it reads at an entity token's position with a positive control there.
*(Same day, §18: answered without a probe — the identity is needed, and emitted, one
position after the boundary, and the evaluator's ACTOR-field excess on RELEASE
records against H*(actor | RELEASE) measures it; the probe is withdrawn.)*
(b) Causal patching is the only route from this association to a mechanism. (c) The
owed GPU items, through the lease.

Ledger: `yupi.learner.probe.next_dist_by_owner`, `mutual_information`;
`scripts/learner_probe_voi.py`, `learner_probe_owner.py --per-example`,
`learner_probe_link.py`, `learner_probe_link_summary.py`, `learner_class_frequency.py`; tests
`tests/test_learner_probe.py` (+1), `tests/test_learner_probe_link.py` (6); raw
prefixes `learner-probe-voi`, `learner-probe-link` registered as non-measurement;
raws `learner-probe-voi-r{2,3,4}-eps1-k7-2026-09-24.json`,
`learner-probe-owner-<cell>-seed<s>-held-2026-09-24.json` (the §16 held probes
refit with per-example rows; best-layer OIRs agree with the 09-23 raws to within 0.01, L-BFGS on CPU),
`learner-probe-link-<cell>-seed<s>-held-2026-09-24.json`; per-window,
per-example and class-frequency rows under `~/.cache/yupi-scratch/probes/`
(sha256 in the raws).

## 18. Which thread: exposure at the point of need (appended 2026-09-24 09:31 PDT, from `date` in the writing command, by the instance of 2026-09-23)

> **Correction (2026-09-24, same day, by the same instance; see §19).** The owner-determined / uncertain split
> in 18.2's second tables, reading 3 and §18.3 selects windows by the *realized* record's lock, an outcome
> correlated with the actor, so the realized-record estimator is biased on those subsets: on r2 seed 2's
> "determined" windows the realized actor equals the exact argmax 95.0 % of the time against P*'s own 87.4 %,
> and on the "uncertain" ones 68.1 % against 80.7 % (all labelled RELEASE windows: 83.8 % vs 84.6 %, calibrated).
> The exact per-window KL on the same subsets (§19) shows **no difference in exposure between them**
> (r2: 0.92 / 0.90 / 0.83 determined against 0.93 / 0.90 / 0.85 uncertain). Reading 3 and the
> "calibration-to-posterior gap, not a retrieval gap" sentence of §18.3 are withdrawn; readings 1, 2 and 4 and
> the pooled rows (conditioned on the realized kind only, which P*(actor | kind) also conditions on) stand.
> The original text is preserved below.

§17.2 put most of the owner's value on *which thread* holds the lock. The
which-thread probe was designed in words as a readout at an entity token's
position. Thinking it through changed the plan (probe design amendment v0.5): the
record layout is kind, actor, object, related, lineage, and the owner's identity is
needed one position after the boundary, when the model has read kind = RELEASE and
must name the releaser as the actor. Its own output distribution at that position
*is* the readout, and the window census already scores it: the ACTOR-field excess
on windows whose realized record k + 1 is a RELEASE. What was missing is the
ceiling beside it, H*(actor | kind, prefix), the exact observer's residual
uncertainty about the actor given the kind, so the excess can be read as a share.

**18.1 Setup.** `scripts/learner_release_actor.py` (raw prefix `learner-release-actor`,
raws `learner-release-actor-<cell>-seed<s>-2026-09-24.json`): for every census
window (§13 rows, k = 7, the whole test split, 85k windows) whose realized record
k + 1 has kind K, the ACTOR-field excess from the census row (a realized-record
estimate of KL(P*(actor | K, prefix) ‖ P̃(actor | K, prefix))), H*(actor | K, prefix)
from the k = 7 ceiling table (`yupi.learner.evaluate.actor_entropy_given_kind`,
tested), and the *exposure ratio* 1 − excess / H*: 1 when the model's actor
distribution matches the ceiling's, 0 when it carries none of the trace-available
information about the actor. On the 30k windows with §16 labels, RELEASE / BLOCK /
ACQUIRE windows are split by whether the prefix determines the owner of the
record's lock. Cells r1–r4 ε = 1, every seed with census rows (3 / 3 / 3 / 6).
Tables from `scripts/learner_release_actor_summary.py`.

**18.2 Tables.**

**RELEASE** (record k + 1 realized as RELEASE; ACTOR-field excess vs the ceiling's H*(actor | RELEASE), bits):

| cell | seeds | share of windows | actor excess per seed | pooled ± sd | H*(actor | kind) | exposure ratio per seed | pooled |
|---|---|---|---|---|---|---|---|
| r1-eps1 | 3 | 0.185 | 0.030 / 0.036 / 0.033 | **0.033** ± 0.003 | 0.424 | 0.93 / 0.92 / 0.92 | **0.92** |
| r2-eps1 | 3 | 0.185 | 0.034 / 0.041 / 0.068 | **0.047** ± 0.018 | 0.386 | 0.91 / 0.89 / 0.82 | **0.88** |
| r3-eps1 | 3 | 0.187 | 0.020 / 0.020 / 0.018 | **0.019** ± 0.001 | 0.296 | 0.93 / 0.93 / 0.94 | **0.94** |
| r4-eps1 | 6 | 0.188 | 0.016 / 0.039 / 0.023 / 0.019 / 0.028 / 0.018 | **0.024** ± 0.008 | 0.300 | 0.95 / 0.87 / 0.92 / 0.94 / 0.91 / 0.94 | **0.92** |

By whether the prefix determines the lock's owner (RELEASE windows with §16 labels):

| cell | seed | determined: n / actor excess / H* / exposure | uncertain: n / actor excess / H* / exposure |
|---|---|---|---|
| r2-eps1 | 1 | 2742 / 0.024 / 0.324 / 0.93 | 1364 / 0.042 / 0.479 / 0.91 |
| r2-eps1 | 2 | 2742 / 0.000 / 0.324 / 1.00 | 1364 / 0.086 / 0.479 / 0.82 |
| r2-eps1 | 3 | 2742 / 0.019 / 0.324 / 0.94 | 1364 / 0.130 / 0.479 / 0.73 |
| r3-eps1 | 1 | 4175 / 0.018 / 0.279 / 0.93 | — |
| r3-eps1 | 2 | 4175 / 0.017 / 0.279 / 0.94 | — |
| r3-eps1 | 3 | 4175 / 0.010 / 0.279 / 0.97 | — |
| r4-eps1 | 1 | 4233 / 0.011 / 0.279 / 0.96 | — |
| r4-eps1 | 2 | 4233 / 0.021 / 0.279 / 0.93 | — |
| r4-eps1 | 3 | 4233 / 0.015 / 0.279 / 0.95 | — |
| r4-eps1 | 4 | 4233 / 0.011 / 0.279 / 0.96 | — |
| r4-eps1 | 5 | 4233 / 0.017 / 0.279 / 0.94 | — |
| r4-eps1 | 6 | 4233 / 0.012 / 0.279 / 0.96 | — |

**BLOCK** (record k + 1 realized as BLOCK; ACTOR-field excess vs the ceiling's H*(actor | BLOCK), bits):

| cell | seeds | share of windows | actor excess per seed | pooled ± sd | H*(actor | kind) | exposure ratio per seed | pooled |
|---|---|---|---|---|---|---|---|
| r1-eps1 | 3 | 0.125 | 0.062 / 0.063 / 0.058 | **0.061** ± 0.003 | 0.474 | 0.87 / 0.87 / 0.88 | **0.87** |
| r2-eps1 | 3 | 0.126 | 0.066 / 0.075 / 0.103 | **0.081** ± 0.019 | 0.426 | 0.85 / 0.82 / 0.76 | **0.81** |
| r3-eps1 | 3 | 0.126 | 0.053 / 0.048 / 0.051 | **0.051** ± 0.002 | 0.379 | 0.86 / 0.87 / 0.86 | **0.87** |
| r4-eps1 | 6 | 0.123 | 0.046 / 0.094 / 0.060 / 0.040 / 0.071 / 0.046 | **0.059** ± 0.020 | 0.376 | 0.88 / 0.75 / 0.84 / 0.89 / 0.81 / 0.88 | **0.84** |

**ACQUIRE** (record k + 1 realized as ACQUIRE; ACTOR-field excess vs the ceiling's H*(actor | ACQUIRE), bits):

| cell | seeds | share of windows | actor excess per seed | pooled ± sd | H*(actor | kind) | exposure ratio per seed | pooled |
|---|---|---|---|---|---|---|---|
| r1-eps1 | 3 | 0.107 | 0.054 / 0.054 / 0.042 | **0.050** ± 0.007 | 0.518 | 0.90 / 0.90 / 0.92 | **0.90** |
| r2-eps1 | 3 | 0.108 | 0.046 / 0.057 / 0.070 | **0.058** ± 0.012 | 0.511 | 0.91 / 0.89 / 0.86 | **0.89** |
| r3-eps1 | 3 | 0.105 | 0.038 / 0.041 / 0.040 | **0.040** ± 0.002 | 0.471 | 0.92 / 0.91 / 0.91 | **0.92** |
| r4-eps1 | 6 | 0.105 | 0.039 / 0.086 / 0.057 / 0.038 / 0.065 / 0.039 | **0.054** ± 0.019 | 0.478 | 0.92 / 0.82 / 0.88 / 0.92 / 0.86 / 0.92 | **0.89** |

Readings:

1. **The model exposes most of the trace-available identity everywhere.** On
   RELEASE records the exposure ratio is 0.88–0.94 pooled at every rung; the
   exact observer's own uncertainty about the releaser is 0.30–0.42 bits and the
   model's excess against it is 0.02–0.05. On BLOCK it is lower (0.81–0.87) and on
   ACQUIRE 0.89–0.92. Naming the actor is not where the learner mainly fails.
2. **r2 is the lowest rung on every kind** (RELEASE 0.88 against 0.92 / 0.94 /
   0.92; BLOCK 0.81 against 0.87 / 0.87 / 0.84), with the widest seed spread
   (seed 3 lowest throughout). The identity-field version of the ladder.
3. **At r2 the deficit sits on the windows whose owner the prefix does not
   determine.** On RELEASE windows with a prefix-determined owner the r2 model's
   excess is 0.024 / 0.000 / 0.019 bits against H* = 0.324 (exposure 0.93 / 1.00 /
   0.94), indistinguishable from r3 and r4 on their determined windows (0.93–0.97).
   On the uncertain third it is 0.042 / 0.086 / 0.130 against H* = 0.479 (0.91 /
   0.82 / 0.73). The r2 model fetches a determined owner as well as a model that
   has it printed; what it does worse is reproduce the exact *posterior* over the
   owner when the ACQUIRE lies outside the window. The same shape on BLOCK
   (determined 0.82–0.88, uncertain 0.62–0.82); ACQUIRE is mixed.
4. **r4's basins separate here.** The high basin (seeds 2, 5) exposes less identity
   on every kind: RELEASE 0.87 / 0.91 against 0.92–0.95, BLOCK 0.75 / 0.81 against
   0.84–0.90, ACQUIRE 0.82 / 0.86 against 0.88–0.92 — all on determined windows,
   since r4 has no others. The first per-record quantity on which the basins
   differ (§15 found a general degradation with contention over-represented; §16
   and §17 found no difference).

**18.3 What this says against §16 and §17.** The boundary probe found less
*held/free* information at p0 at r2 than at r3 even where the prefix determines
it (§16.2). At the point of need, the r2 model exposes a determined owner's
identity as well as r3 does (reading 3). The two are compatible: the boundary
does not hold what attention fetches a position later, and the fetch works when
the fact is in the window. The r2 deficit that survives is on the uncertain
windows, where the ceiling is a posterior the model must have learned as a
distribution over the four candidate threads from the prefix's shape alone. That
is the same third of examples that carry all of §17.2's value-of-information
(I(next; owner) is zero where the owner is determined). So the which-thread gap
at r2 is a calibration-to-posterior gap, not a retrieval gap, and the
position-pair probe is withdrawn from the plan.

**18.4 What this does not say.** Exposure ratios are means of realized-record
estimates over windows of one kind; the per-window noise floor of §13 applies,
though at n ≈ 9–16k per (cell, seed, kind) the standard errors are 0.002–0.005
bits. The owner split covers the 30k labelled windows (n = 4,106 RELEASE per r2
seed), the pooled rows all 85k. Nothing causal. The ceiling H*(actor | K) is the
pattern observer's; the model's excess is measured after the naming rule, as
everywhere in this note.

**18.5 What follows.** (a) The uncertain-owner windows at r2 are the target: does
the model's actor distribution there track the exact posterior's shape (KL per
window against H(owner | prefix) from the §16 labels), or collapse toward the
most recent actor? (b) Causal patching. (c) The GPU items now running under the
lease (ε = ½ seeds 4–6 at r2 / r4; the r1 size-axis learning-rate sweep).

## 19. Where the identity deficit sits, by exact KL (appended 2026-09-24 09:51 PDT, from `date` in the writing command, by the instance of 2026-09-23)

§18's owner split was outcome-selected and its realized-record estimates biased
(correction at the head of §18). This section redoes the which-thread measurement
with the exact per-window quantity and prefix-only splits.
`scripts/learner_actor_shape.py` (raw prefix `learner-actor-shape`, raws
`learner-actor-shape-<cell>-seed<s>-RELEASE-2026-09-24.json`): for every labelled
window (the §16 30k) whose realized record k + 1 is a RELEASE, the model's
distribution over the actor at the position after the kind token
(`yupi.learner.evaluate.model_actor_dist`: mass on each seen thread token by pattern
index, unused thread tokens summed as "fresh", renormalized over thread tokens; the
off-thread mass is 0.0002–0.0008 and reported) against the ceiling's
P*(actor | RELEASE, prefix) (`actor_pattern_dist`; both tested). KL(P* ‖ P̃) in bits
per window, its mean and se, the realized-record estimate beside it, H* and H̃, argmax
agreement, and the mass each puts on record k's actor. Splits are functions of the
prefix: H*(actor | RELEASE) bins, and whether every lock visible in the prefix has a
prefix-determined owner ("all-determined") or some lock's owner is uncertain
("some-uncertain"; "no-lock" windows, 8–15 per cell, omitted from the tables).

**19.1 The direct measurement.** Cells r2 (3 seeds), r3 (3), r4 (seeds 1, 2, 5, 6;
2 and 5 are the high basin):

| cell | seed | n | KL(P* ‖ P̃) bits | realized estimate | H*(actor \| RELEASE) | H̃ | exposure 1 − KL/H* | argmax agree | mass on record k's actor: exact / model |
|---|---|---|---|---|---|---|---|---|---|
| r2-eps1 | 1 | 4693 | 0.0321 ± 0.0011 | 0.0356 | 0.390 | 0.427 | **0.92** | 0.905 | 0.480 / 0.484 |
| r2-eps1 | 2 | 4693 | 0.0385 ± 0.0016 | 0.0429 | 0.390 | 0.410 | **0.90** | 0.922 | 0.480 / 0.485 |
| r2-eps1 | 3 | 4693 | 0.0664 ± 0.0025 | 0.0709 | 0.390 | 0.457 | **0.83** | 0.913 | 0.480 / 0.482 |
| r3-eps1 | 1 | 4767 | 0.0169 ± 0.0010 | 0.0189 | 0.299 | 0.326 | **0.94** | 0.922 | 0.485 / 0.482 |
| r3-eps1 | 2 | 4767 | 0.0190 ± 0.0012 | 0.0201 | 0.299 | 0.324 | **0.94** | 0.923 | 0.485 / 0.484 |
| r3-eps1 | 3 | 4767 | 0.0193 ± 0.0011 | 0.0185 | 0.299 | 0.324 | **0.94** | 0.922 | 0.485 / 0.485 |
| r4-eps1 | 1 | 4843 | 0.0189 ± 0.0013 | 0.0201 | 0.299 | 0.312 | **0.94** | 0.922 | 0.482 / 0.481 |
| r4-eps1 | 2 | 4843 | 0.0349 ± 0.0017 | 0.0392 | 0.299 | 0.337 | **0.88** | 0.905 | 0.482 / 0.485 |
| r4-eps1 | 5 | 4843 | 0.0280 ± 0.0021 | 0.0334 | 0.299 | 0.319 | **0.91** | 0.936 | 0.482 / 0.484 |
| r4-eps1 | 6 | 4843 | 0.0167 ± 0.0008 | 0.0179 | 0.299 | 0.320 | **0.94** | 0.922 | 0.482 / 0.479 |

The realized-record estimate agrees with the exact KL to within its own standard
error (0.003–0.004) on every prefix-defined group, and the realized actor equals
the exact argmax as often as P* says it should (r2 0.838 vs 0.846; r3 0.875 vs
0.875; r4 0.870 vs 0.875), which is the calibration check the §18 subsets failed.

**19.2 Prefix-only owner split at r2.**

| cell | seed | all-determined: n / KL / H* / exposure | some-uncertain: n / KL / H* / exposure |
|---|---|---|---|
| r2-eps1 | 1 | 2227 / 0.0293 / 0.299 / 0.90 | 2456 / 0.0348 / 0.473 / 0.93 |
| r2-eps1 | 2 | 2227 / 0.0336 / 0.299 / 0.89 | 2456 / 0.0431 / 0.473 / 0.91 |
| r2-eps1 | 3 | 2227 / 0.0589 / 0.299 / 0.80 | 2456 / 0.0734 / 0.473 / 0.84 |

**19.3 By the exact observer's own uncertainty.**

| cell | seed | H* ∈ [0, 0.5): n / KL / H* / H̃ | H* ∈ [0.5, 1): n / KL / H* / H̃ / agree | H* ∈ [1, 1.5): n / KL / H* / H̃ / agree |
|---|---|---|---|---|
| r2-eps1 | 1 | 2779 / 0.0174 / 0.025 / 0.076 | 1656 / 0.0567 / 0.906 / 0.924 / 0.83 | 258 / 0.0334 / 1.000 / 1.015 / 0.40 |
| r2-eps1 | 2 | 2779 / 0.0162 / 0.025 / 0.074 | 1656 / 0.0732 / 0.906 / 0.883 / 0.88 | 258 / 0.0569 / 1.000 / 0.993 / 0.36 |
| r2-eps1 | 3 | 2779 / 0.0556 / 0.025 / 0.151 | 1656 / 0.0836 / 0.906 / 0.887 / 0.86 | 258 / 0.0711 / 1.000 / 0.993 / 0.40 |
| r3-eps1 | 1 | 3284 / 0.0086 / 0.012 / 0.038 | 1023 / 0.0423 / 0.908 / 0.939 / 0.86 | 460 / 0.0194 / 1.000 / 1.024 / 0.51 |
| r3-eps1 | 2 | 3284 / 0.0101 / 0.012 / 0.039 | 1023 / 0.0444 / 0.908 / 0.927 / 0.91 | 460 / 0.0257 / 1.000 / 1.022 / 0.42 |
| r3-eps1 | 3 | 3284 / 0.0102 / 0.012 / 0.044 | 1023 / 0.0458 / 0.908 / 0.915 / 0.89 | 460 / 0.0248 / 1.000 / 1.008 / 0.44 |
| r4-eps1 | 1 | 3335 / 0.0065 / 0.013 / 0.031 | 1023 / 0.0478 / 0.898 / 0.898 / 0.89 | 485 / 0.0433 / 1.000 / 1.010 / 0.46 |
| r4-eps1 | 2 | 3335 / 0.0201 / 0.013 / 0.069 | 1023 / 0.0814 / 0.898 / 0.892 / 0.84 | 485 / 0.0385 / 1.000 / 1.007 / 0.41 |
| r4-eps1 | 5 | 3335 / 0.0129 / 0.013 / 0.046 | 1023 / 0.0651 / 0.898 / 0.889 / 0.90 | 485 / 0.0535 / 1.000 / 0.990 / 0.58 |
| r4-eps1 | 6 | 3335 / 0.0076 / 0.013 / 0.037 | 1023 / 0.0437 / 0.898 / 0.914 / 0.87 | 485 / 0.0224 / 1.000 / 1.010 / 0.50 |

Readings:

1. **The identity ladder by exact KL:** exposure on RELEASE 0.92 / 0.90 / 0.83 at
   r2 against 0.94 / 0.94 / 0.94 at r3 and 0.94 / 0.88 / 0.91 / 0.94 at r4. KL
   0.032–0.066 at r2 against 0.017–0.019 at r3 and r4's low basin. §18's pooled
   rows are confirmed by the quantity they estimated.
2. **The r2 deficit is not concentrated on uncertain-owner prefixes.** On prefixes
   whose visible locks all have determined owners the exposure is 0.90 / 0.89 / 0.80;
   on prefixes with some uncertain owner 0.93 / 0.91 / 0.85. If anything the
   determined prefixes are worse. §18's withdrawn reading 3 said the opposite, from
   the biased subsets.
3. **The r2 model hedges on a releaser the exact observer is sure of.** On the
   2,779 windows with H* < 0.5 (mean 0.025 bits: the owner is all but determined),
   the r2 model's own entropy is 0.076 / 0.074 / 0.151 bits against 0.038–0.044 at
   r3 and 0.031–0.037 in r4's low basin, and its KL there is 0.017 / 0.016 / 0.056
   against 0.009–0.010 and 0.007–0.008. The excess is in every bin (mid bin 0.057 /
   0.073 / 0.084 against 0.042–0.046 at r3; two-candidate bin 0.033 / 0.057 / 0.071
   against 0.019–0.026), but its *ratio* to r3 is largest where the answer is
   determined. Together with §16.2 (less held/free information at the boundary at
   r2 even where the prefix determines it), the r2 learner represents determined
   lock state with less confidence than a learner that has it printed, and that
   shows at the point of need as probability spread off the right thread.
4. **No collapse onto the recent actor.** The model's mass on record k's actor
   matches the exact observer's to 0.005 at every cell and seed; argmax agreement is
   0.905–0.936. The r2 deficit is diffuse hedging, not a wrong heuristic.
5. **r4's high basin sits at r2's level.** Seeds 2 and 5: KL 0.035 / 0.028
   (exposure 0.88 / 0.91) against 0.019 / 0.017 for seeds 1 and 6, elevated in every
   H* bin, with the same hedging signature on near-determined windows (H̃ 0.069 /
   0.046 against 0.031 / 0.037). Whatever the high basin's solution is, on identity
   at the point of need it looks like the r2 learner.

**19.4 What this does not say.** Correlational, one position (the actor after a
RELEASE kind token), one k, the 30k labelled windows. "Hedging on a determined
answer" is a description of the output distribution, not a mechanism; the boundary
probe of §16 and this are two views of the same cell, not a causal chain. The
model's actor distribution is read after renormalizing over thread tokens (the
off-thread mass is negligible and reported).

**19.5 What follows.** (a) The same measurement at the BLOCK kind (the actor is the
blocker; identity of the owner enters through who *cannot* be acting). (b) Causal
patching on the near-determined RELEASE windows: does patching the boundary
activation from an r3 model's representation of the same prefix sharpen the r2
model's releaser? That is the first intervention this note would license.
(c) The GPU items running under the lease.

**19.6 The same at BLOCK (appended 2026-09-24 10:05 PDT, from `date` in the writing command).** The
actor of a BLOCK is the blocker, not the owner; the owner enters through who cannot
be the one acting. Same script, `--kind BLOCK`, raws
`learner-actor-shape-<cell>-seed<s>-BLOCK-2026-09-24.json`:

| cell | seed | n | KL bits | realized est. | H*(actor \| BLOCK) | H̃ | exposure | all-determined: KL / exposure | some-uncertain: KL / exposure | H* < 0.5 bin: KL / H* / H̃ |
|---|---|---|---|---|---|---|---|---|---|---|
| r2-eps1 | 1 | 3160 | 0.0637 ± 0.0029 | 0.0638 | 0.423 | 0.511 | **0.85** | 0.0595 / 0.86 | 0.0704 / 0.83 | 0.0570 / 0.070 / 0.193 |
| r2-eps1 | 2 | 3160 | 0.0764 ± 0.0033 | 0.0697 | 0.423 | 0.515 | **0.82** | 0.0705 / 0.84 | 0.0856 / 0.79 | 0.0651 / 0.070 / 0.211 |
| r2-eps1 | 3 | 3160 | 0.1090 ± 0.0046 | 0.0965 | 0.423 | 0.579 | **0.74** | 0.0953 / 0.78 | 0.1292 / 0.69 | 0.1158 / 0.070 / 0.299 |
| r3-eps1 | 1 | 3164 | 0.0470 ± 0.0019 | 0.0551 | 0.377 | 0.462 | **0.88** | 0.0467 / 0.88 | — | 0.0386 / 0.051 / 0.151 |
| r3-eps1 | 2 | 3164 | 0.0527 ± 0.0032 | 0.0506 | 0.377 | 0.447 | **0.86** | 0.0516 / 0.86 | — | 0.0367 / 0.051 / 0.139 |
| r3-eps1 | 3 | 3164 | 0.0484 ± 0.0024 | 0.0498 | 0.377 | 0.459 | **0.87** | 0.0482 / 0.87 | — | 0.0382 / 0.051 / 0.159 |
| r4-eps1 | 1 | 3145 | 0.0474 ± 0.0023 | 0.0520 | 0.381 | 0.454 | **0.88** | 0.0472 / 0.88 | — | 0.0349 / 0.049 / 0.138 |
| r4-eps1 | 2 | 3145 | 0.0807 ± 0.0035 | 0.0954 | 0.381 | 0.494 | **0.79** | 0.0803 / 0.79 | — | 0.0682 / 0.049 / 0.194 |
| r4-eps1 | 5 | 3145 | 0.0716 ± 0.0038 | 0.0770 | 0.381 | 0.471 | **0.81** | 0.0714 / 0.81 | — | 0.0576 / 0.049 / 0.174 |
| r4-eps1 | 6 | 3145 | 0.0484 ± 0.0027 | 0.0415 | 0.381 | 0.447 | **0.87** | 0.0483 / 0.87 | — | 0.0356 / 0.049 / 0.131 |

6. **Same ladder, same signature, larger.** Exposure on BLOCK 0.85 / 0.82 / 0.74 at
   r2 against 0.88 / 0.86 / 0.87 at r3 and 0.88 / 0.79 / 0.81 / 0.87 at r4 (the two
   low values are the high basin). On the near-determined windows (H* ≈ 0.07 bits,
   1,802 per r2 seed) the r2 model's entropy is 0.19 / 0.21 / 0.30 against 0.14–0.16
   at r3 and 0.13–0.14 in r4's low basin: the same hedging on a blocker the exact
   observer is sure of. The realized estimate agrees with the KL within its error
   on every prefix-defined group (calibration check 0.829 vs 0.835 at r2).
7. **At BLOCK the uncertain-owner prefixes are worse, by 15–35 %** (KL 0.070 /
   0.086 / 0.129 against 0.060 / 0.071 / 0.095 at nearly equal H*), where at RELEASE
   they were not (19.2). Reading 2 stands as stated for RELEASE; across the two
   kinds the honest summary is that the r2 deficit is present on both kinds of
   prefix and not confined to either.
