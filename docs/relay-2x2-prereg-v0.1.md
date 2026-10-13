# Completing the relay 2×2: pre-registration v0.1 (2026-10-13)

> **Status: PRE-REGISTRATION, DRAFT for two-family pre-stamp review.** It is committed and stamped before any model
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

Each contrast changes one thing and holds the mask and the loss denominator fixed. "Separated below" means every
model of the first arm is below every model of the second (unpaired exact p = 1/20). "Separated above" is the
reverse. Anything else is "overlapping", and reads as *not resolved with three seeds*. That is a reading in its own
right, not evidence of no effect.

- **C1, presence without supervision: r1Rm against r1m.** The mask is the same and only the OBJECT input differs.
  - Separated above: "an unscored varying copy costs the learner".
  - Separated below: "an unscored copy helps".
- **C2, supervision without presence: r1Rs against r1.** The mask is the same and only the OBJECT target differs
  (relay value vs MASKED).
  - Separated below: "training the lookup helps even when the copy is never shown".
  - Separated above: "it hurts".
- **C3, presence given supervision: r1R against r1Rs.** The mask and targets are the same, and only the OBJECT input
  differs.
  - Separated below: "the copy helps once it is supervised".
  - Separated above: "it hurts".
- **C4, the normalization and trivial-target check: r1m against r1.** Reported descriptively, with no reading.

For each contrast, the seed-paired sign pattern (3 pairs) is reported beside it, and so is its paired p (1/8 when
all three pairs agree in sign).

## 4. What paper 1 will say under each pattern

- **C1 above and C2 below:** both the confound reading and the supervision reading hold. An unscored varying field
  costs the learner, and lookup supervision helps without presence.
- **C2 below and C3 overlapping:** within these arms the gain is supervision of the lookup. Showing the copy adds
  nothing resolvable with three seeds.
- **C3 below:** presence contributes once the copy is supervised (a presence × supervision interaction). A distance
  or binding role is then live again.
- Every other pattern is reported cell by cell, without a summary sentence.

## 5. Reported alongside, not scored

The ACTOR shortfall; the OBJECT-field excess, interpreted for each arm (for r1m and r1Rs scored on the r1 corpus,
whose OBJECT is MASKED); and the validation-loss curves, as a committed raw.

## 6. Gates

- Each `run.json` records its arm's fields, a clean git revision, the corpus manifests, and steps_total 117,195.
- The census sha256 matches its JSONL.
- The current census re-run on one existing r1 checkpoint reproduces its 10-02 per-window file bit-exactly. This
  replaces the nonexistent `crosscheck` block that the loss-mask prereg named.
