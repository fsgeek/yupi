# Completing the relay 2×2: pre-registration v0.1 (2026-10-13)

> **Status: PRE-REGISTRATION v0.1, revised after two-family pre-stamp review (Claude and Codex, both "stamp after
> fixes"; every fix adopted, listed in §7).** It is committed and stamped before any model
> in it is trained. Exploratory in scale: 3 seeds per arm, so the smallest unpaired exact p is 1/20 and the
> smallest seed-paired one is 1/8. Owning instance. Occasion: both reviews of `relay-lossmask-verdict-v0.1.md`
> (Claude findings 1–4, Codex findings 1–2). r1Rm's deficit against r1 is confounded three ways: a varying field
> against a constant placeholder, r1's trivial OBJECT target, and a loss denominator about 24 % smaller. And
> supervision without presence was never tested.

## 1. The design

Two factors, both at the OBJECT slot of r1-projected records, all at ε = 1, d = 128, 15 epochs, and the 10-02
recipe. The corpora are paired: r1 and r1R (`fd5da4c31e43d73d`) have identical masks in every split and differ only
at OBJECT, which was checked on 2026-10-13 over 2.11 M windows.

| | OBJECT not a target | OBJECT target = MASKED (trivial) | OBJECT target = relay value |
|---|---|---|---|
| **input: MASKED** | **r1m** (new) | r1 (10-02) | **r1Rs** (new) |
| **input: relay copy** | r1Rm (10-13) | — | r1R (10-02) |

- **r1m:** the r1 corpus with `--unscored-fields OBJECT`.
- **r1Rs:** inputs from the r1 corpus and targets from the r1R corpus (`--target-corpus-dir … --target-fields
  OBJECT`). It is gated: the trainer refuses unless the masks are identical and the targets differ only at OBJECT
  (`paired_targets`, tested). The model is trained to predict the relay value at OBJECT, and then sees MASKED there
  as input.
- Seeds 1, 2 and 3. Seed i shares initialization and batch order across arms, because `torch.manual_seed` and
  `epoch_order` depend only on the seed and the corpora have equal size.

## 2. The measurement

KIND shortfall: the mean of `by_field.kind` over the k = 7 test windows, from the frozen census script. r1m and r1Rs
are censused on the **r1** corpus (their inputs). r1Rm and r1R are censused on the r1R corpus, as they were. The test
windows and KIND targets are identical across the two corpora, and so are the ceilings, class by class.

Known values, read before this document was written:
- r1: 0.01570, 0.01464, 0.01576
- r1R: 0.01296, 0.00947, 0.01252
- r1Rm: 0.02809, 0.04114, 0.03072

## 3. Contrasts and readings, fixed now

For contrast X against Y and seed s, let d_s = shortfall(X, s) − shortfall(Y, s), with matched seeds. Each
contrast has a **pre-registered direction**. For each contrast we report two things:
- **Decision rule (descriptive):** *resolved in the predicted direction* if every model of X is beyond every model
  of Y in that direction; *resolved against* if all are beyond in the opposite direction; otherwise *not resolved
  with three seeds*. Ties count as not resolved. Not resolved is a reading in its own right, and it is not
  evidence of no effect.
- **Paired p:** an exact one-sided sign-flip test in the pre-registered direction. The statistic is Σ_s d_s,
  enumerated over all 2³ flips, with the tail inclusive (≥ the observed value). The floor is 1/8. A
  resolved-against outcome gets no p, only description.

The contrasts:
- **C1, presence without supervision: r1Rm against r1m.** Direction: r1Rm > r1m. The mask and denominator are the
  same, and only the OBJECT input differs. Resolved reading: "with OBJECT unscored, carrying the relay copy in the
  input costs the learner relative to a constant placeholder". It cannot tell an informative but unscored copy
  from a varying decoy field.
- **C2, relay supervision in place of trivial supervision, without presence: r1Rs against r1.** Direction:
  r1Rs < r1. The mask and denominator are the same, and only the OBJECT target differs (relay value vs MASKED).
  Resolved reading: "supervising the OBJECT slot with the relay value helps, even when the copy is never shown".
  It cannot tell lookup supervision from *any* nontrivial predictable target in that slot. The control that could
  (r1 inputs with r1D or r1S targets) would touch the blind pilot corpora and is not run.
- **C3, presence given relay supervision: r1R against r1Rs.** Direction: r1R < r1Rs. The mask and targets are the
  same, and only the OBJECT input differs. Resolved reading: "showing the copy helps once its slot is supervised".
  This is a *simple effect*, not an interaction.
- **I, the interaction (difference-in-differences), per seed:**
  I_s = (r1R_s − r1Rs_s) − (r1Rm_s − r1m_s). It is reported with its sign pattern and its paired p (statistic
  Σ I_s, two-sided, enumerating |Σ| over 2³ flips, floor 1/4). "Interaction" is said only if C1 and C3 are both
  resolved, with opposite signs.
- **C4, the normalization and trivial-target check: r1m against r1.** Descriptive only. The expected result is
  near-null: under AdamW a constant loss scale barely moves the updates, and the trivial target's gradient
  vanishes early (Claude pre-stamp finding 9). Its |d_s| serves as an empirical noise floor for near-identical
  recipes on the same seed.

**Reachability, stated before the run.** C1 is close to settled in advance, if r1m lands near r1 (0.015) and r1Rm
stays at 0.028 or above. C2 and C3 split a gap of about 0.0037 between r1R and r1, against r1R's seed spread of
0.0019. If r1Rs lands in between, both contrasts are *not resolved*, and that is a realistic outcome. A second wave
on seeds 4–6 would be a new pre-registration, not a continuation of this one.

## 4. What paper 1 will say

Every contrast's reading is reported. Where several apply, they are read jointly, with no ranking among them.
Fixed sentences:
- C2 resolved: "supervising the OBJECT slot with the relay value helped without the copy present".
- C2 resolved and C3 not resolved: add "whether showing the copy adds to that is not resolved".
- C3 resolved: "showing the copy helped once its slot was supervised". A distance or binding role is then a live
  hypothesis, not a result.
- C1 resolved: "an unscored copy in the input cost the learner, relative to a constant placeholder".
- Nothing resolved: "the 2×2 does not separate presence from supervision with three seeds".

## 5. Reported alongside, not scored

- **Did r1Rs learn the lookup?** We report the OBJECT cross-entropy against the relay values (`scripts/relay_object_ce.py`:
  r1Rs on r1 test inputs, r1R on its own). The ideal observer pays 0 bits. Reference values were measured before
  stamping on 4,000 windows: r1R seed 1 pays 0.0001 bits per OBJECT slot on its own inputs and 0.006 on r1 inputs,
  and r1 seed 1, which never learned the relay, pays 71. Rule: r1Rs "learned the lookup" if it pays ≤ 0.05 bits.
  If it did not, C2 and C3 are reported as uninterpretable for lookup supervision.
- The ACTOR shortfall.
- The validation-loss curves, as a committed raw. These are not comparable across arms: r1Rs is validated on r1R
  targets, and r1m on a smaller mask.

## 6. Gates

- Each `run.json` records its arm's fields, a clean git revision, `corpus_manifest_sha256`, and, for r1Rs,
  `target_corpus_manifest_sha256`. Completion means the final checkpoint and census are at step 117,195, not merely
  that steps_total is recorded.
- `paired_targets` refuses mismatched masks, differences outside OBJECT, and a target corpus that never differs at
  OBJECT (the input corpus given twice by mistake). This is tested.
- **The trainer reproduces the 10-02 runs.** Before the six jobs, the wave trains r1 seed 1 for 1,000 steps on the
  GPU under HEAD. Its step-1000 train and validation losses must equal the 10-02 log exactly (0.6791265606880188,
  0.6846594339672173), or the wave stops. This authenticates the historical r1 and r1R baselines, whose run.json
  files predate the provenance fields.
- The wave propagates every trainer's exit status (a fix for Codex pre-stamp finding 6, which also applies to the
  loss-mask wave; those runs did reach their final step, as verified).
- The census sha256 matches its JSONL.
- The current census re-run on one existing r1 checkpoint reproduces its 10-02 per-window file bit-exactly. This
  replaces the nonexistent `crosscheck` block that the loss-mask prereg named.
  **Done before stamping (2026-10-13):** the current census on the r1 seed-1 15-epoch checkpoint reproduces
  `c1prime-loop-40-8-2-r1-eps1-2M-d128-lr1e-3-e15-s1-k7-test.jsonl` byte for byte (sha256 prefix 7a0f6b570f01811c).
  The Claude loss-mask verdict reviewer did the same for r1R seed 1.

## 7. Pre-stamp review record (2026-10-13)

- **Codex:** C3 is not an interaction, so the difference-in-differences was added. The p statistic and its
  sidedness are now fixed. C2 is worded as target replacement. The summaries are read jointly. Both manifest
  hashes are recorded. The launcher exit status was a real bug, now fixed in both wave scripts.
- **Claude:** C2 tests a nontrivial OBJECT target, not specifically the lookup. §4 had overclaimed, so it is
  weakened. The same interaction point as Codex. 1/20 is not the design's p, so the paired sign-flip test is used.
  The lookup-learned check was added. The manifest hash was added. The trainer-reproduction gate was added. The
  identical-corpus refusal was added. C4's expected near-null was added. The note on validation losses was added.
- **Not adopted:** the r1D/r1S-target control for C2 (it would touch the blind pilot corpora), and a
  pre-registered second wave (it would be a new pre-registration if needed).
