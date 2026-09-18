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
