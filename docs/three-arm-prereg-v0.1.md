# The three-arm intervention: pre-registration v0.1 (2026-10-05)

> **2026-10-05: BLOCKED BEFORE STAMP. NOT a pre-registration.** Both pre-stamp reviewers (Claude and Codex) found
> blocking problems. Most importantly, its inference ignores between-model variance, which dominates at 5 epochs.
> See `docs/three-arm-prereg-review-2026-10-05.md`. It is kept as the record of what was proposed. No model was
> trained.
>
> **Original status line:** CONFIRMATORY, pre-registered by the owner, the instance of 2026-10-05. **No three-arm model has been
> trained** when this is stamped, and none exists on the fresh corpus. Design: `docs/three-arm-design-v0.1.md`.
> Exact side: `docs/three-arm-exact-side-r1{D,S}-2026-10-05.json` (all gates passed) and the relay's
> `docs/relay-exact-side-2026-09-30.json`. Severity: `docs/three-arm-severity-2026-10-05.json`. Frozen scorer:
> `scripts/three_arm_score.py` with `tests/test_three_arm_score.py` (sha256 in §6).

## 1. What is tested

Three readings of the relay's learner gain, which was V-shaped in Δι, zero at ι4 = 0, and persistent:

- **H_move:** the gain tracks how much long-lag KIND information an added field moves, |Δι|, whatever the field
  says.
- **H_bind:** the gain comes from the relay's binding content (the KIND *of this actor*).
- **H_field:** any added deterministic field changes learning.

The arms are window-level rungs over r1. Each fills the OBJECT slot that r1 masks, and each has a ceiling identical
to r1's class by class (gates A–C):

| arm | field | binding content | mean Δι_kind,4 (ε = 1) |
|---|---|---|---|
| r1R relay | the KIND of the latest earlier record of t's actor | yes | 0.094 |
| r1D decoy | the KIND of record t − 1 | no | 0.068 |
| r1S self-copy | record t's own KIND | no | 0 exactly in every class |

On the 10-02 relay windows, the per-window |Δι| of relay and decoy correlate 0.47. The decoy moves more than the
relay by 0.1 bits or more in 7.7 % of windows, and the relay more than the decoy in 19.3 %.

## 2. Models and data

- **Fresh paired corpus:** run 0582ffbeb4693d27, (40, 8, 2) c1prime-loop, ε = 1. Train seeds 10M–12M, val 13M–13.01M,
  test 14M–14.1M. Its episodes are disjoint from every earlier corpus, because trajectories depend on the episode id
  and earlier corpora used ids below 4.1M. There are four renderings: r1, r1R, r1D, r1S. Manifests are in
  `docs/corpus-manifests/`. Each arm's pairing gate (`scripts/relay_corpus_check.py --rung`) must pass before
  training.
- **Transformer:** `scripts/learner_train.py`, d = 128, lr 1e-3, seeds 1–3, for each of the four rungs.
  - **Primary (scored):** 5 epochs.
  - **Secondary (reported, not scored):** 15 epochs. §5 says why.
  - 24 runs under the ayllu-gpu lease (`--holder yupi`), four at a time.
- **Census:** k = 7, full test split, `scripts/learner_window_census.py`, for every run.
- **Count learner:** `CountKind` on the fresh r1 corpus, reported beside the r1 transformer as a replication of
  the 1.5–4.7× ratio. Descriptive only.

## 3. Predictions (5 epochs; frozen scorer)

Per window: G_arm = mean r1 excess − mean arm excess (realized KIND excess, seed means). Slopes are taken on the
arm's own per-class |Δι_kind,4|, with CR1 errors by r1 class.

| | prediction | supports |
|---|---|---|
| **P_V** | relay slope on |Δι_R|: t ≥ 3 | replication of the V on fresh windows and models |
| **P_move** | decoy slope on |Δι_D|: t ≥ 3, and slope_D / slope_R ≥ 0.5 | H_move |
| **P_bind** | slope_D / slope_R ≤ 0.25 | H_bind |
| **P_null** | self-copy mean gain within ±2 se of 0 | against H_field |

**Reading (fixed now):**
- **H_move** if P_move and P_null.
- **H_bind** if P_bind and P_null.
- **"H_field indicated"** if P_null fails with a positive mean.
- Otherwise **"unresolved"**. A ratio in (0.25, 0.5), for instance, supports neither.
- If P_V fails, the V did not replicate. The arm comparison is still reported, but it is read as uninformative about
  the relay's mechanism.

Reported without a test: each arm's mean gain on ι4_r1 = 0 windows and off them. Every reading predicts about zero
on, so this is a check.

## 4. Severity (computed before stamping; `three-arm-severity`)

Method: a wild cluster bootstrap on the 10-02 relay arm's windows and residuals, 1000 simulations, arms with
independent noise. The real arms share the r1 seeds, so these numbers are conservative.

| prediction | power (own hypothesis) | severity vs rivals |
|---|---|---|
| P_move | 1.00 | 1.00 vs H_bind, 1.00 vs H_field |
| P_bind | 0.996 | 1.00 vs H_move |
| P_null | 0.96 | 1.00 vs H_field (field effect = the relay's intercept, 0.003) |

Every prediction clears design §7's bar of 0.8.

## 5. Why 15 epochs is not scored

At 15 epochs the relay's slope on |Δι| was t 2.26 in the 10-02 data. Severity stays at least 0.98, but power falls
to 0.60 (P_move) and 0.77 (P_bind). A test that misses a true effect a third of the time is not scored. Its numbers
are reported with the same scorer (`--budget e15`, `scored: false`).

## 6. Frozen artifacts and gates

- **Frozen code:** `scripts/three_arm_score.py` and `tests/test_three_arm_score.py` are committed in the same commit
  as this file. Neither is edited after the first model trains. If the scorer has a bug, the fix goes in a dated
  addendum, and both the original and the fixed outputs are reported.
- **Scorer gates:**
  - every census is on the fresh run;
  - all 12 censuses have identical window sets;
  - |Δι| comes from sha-gated caches;
  - the self-copy's |Δι| is identically 0.
- **Raws are committed unscored before scoring.** The scorer is run, and the verdict written, only after the raws'
  commit. Before the verdict is adopted, one Claude reviewer and one Codex reviewer recompute it independently.

## 7. What is not claimed

- Anything about mechanism inside the transformer.
- Anything about ε = ½.
- Anything beyond d = 128 at this world and scale.
- "Binding content" here means only the difference between the relay's rule and the decoy's. A positive H_bind is
  not evidence of entity binding in the activations; that is paper 1 §5's question.
