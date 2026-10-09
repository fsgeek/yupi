> **2026-10-09: WITHDRAWN BEFORE STAMP.** Both pre-stamp reviewers blocked it: the "back" set moves information
> closer at lags 1–2, so a pass would not contradict locality (inventory §G). No model was trained. Kept as the
> record.

# Replicating §4a at the model level: design v0.1 (2026-10-09)

> **Status: DESIGN.** Skeleton v0.4 owes this before external review, because §4a contradicts a published result
> (Someya et al., ACL 2025: loss rises as information is pushed further away) and today rests on 3 + 3 models.
> Written by the owning instance. A pre-registration, a frozen scorer and a two-family pre-stamp review follow. No
> model is trained before the stamp.

## 1. The one question

When an exact, ceiling-identical relay pushes next-KIND information **further back** (Δι_R < −0.05), does the
typical model learn those windows **better** (gain > 0, §4a), or worse or no better (gain ≤ 0, the locality
account)?

This is the most discriminating contrast available. Where the relay moves information *closer* (Δι > 0.05), both
accounts predict a gain, so that arm is reported but not tested.

## 2. Statistic (offset-cancelling, per seed s)

  L_s = mean over windows with Δι_R < −0.05 of (y_r1,s − y_R,s)  −  mean over windows with Δι_R = 0 exactly of the same

Here y is realized KIND excess on the fresh test split, and the sets come from the exact side (relay cache,
sha-gated). Any seed-level offset, and any uniform field effect, cancels.

Template values (10-02 models, 15 epochs, seed-matched):
- L = 0.0072, 0.0137 and 0.0031;
- the null spread between two r1 models is sd 0.0017.

## 3. Test (distribution-free)

- **Estimand: the typical model.** The pass condition is **#{s : L_s > 0} ≥ 10 of 12**. The one-sided sign-test p
  under "median L ≤ 0" is 0.019, under any distribution, including mixtures with heavy tails or seeds in an
  off-phase.
- Reported alongside, not scored: the mean, a t, and a seed-bootstrap interval of L. The right arm's contrast. Every
  seed's value.
- **Power (templates):** with L ~ N(0.008, 0.0053), P(L > 0) per seed is ≈ 0.93, so the pass probability is ≈ 0.96.
  If the seed sd is 3× larger (the upper bound of a df-2 estimate), P ≈ 0.69 per seed and the pass probability is
  ≈ 0.2. That trade is accepted and stated: a false pass is bounded at 0.019, and a miss is a non-answer.

## 4. The field confound, and what is claimed

The relay adds a field. L cancels a *uniform* field effect, but not one that differs by class set. A pass therefore
licenses only this claim:

> On the windows where an exact, ceiling-identical relay pushes next-KIND information further back, the typical
> model's excess is lower with the relay than without it, relative to windows where nothing moves. That is the
> opposite sign to the locality account's prediction.

It does not claim *why*. The self-copy arm r1S is trained alongside as a **descriptive check**. If LS_s (the same
contrast with the self-copy, which moves nothing) is as large as L_s, the reading is "a field effect on those
classes", and the paper says so. The self-copy cannot be a gate, because its field has zero entropy (see the
three-arm review record).

## 5. Models and GPU

- **Corpus:** the fresh paired corpus run 0582ffbeb4693d27 (gated). Rungs r1, r1R and r1S. Seeds 1–12, each
  trained on all three rungs. 15 epochs, d = 128, lr 1e-3.
- 36 runs. Pilot seeds 101–103 are excluded, under their own protocol.
- **Leases:** 9 one-wave leases of 4 runs each (about 70 min, `--expected-until` +75 min), with ≥ 60 min between
  them. Per Tony, the card is the ayllu's.
- **Before the first lease,** one line is added to `scripts/learner_train.py` to record the git revision in
  `run.json`. Scorer v3 has a gate for it, but the trainer doesn't write it yet.

## 6. Reuse

The scorer reuses three_arm_score_v3's gates: frozen seeds, recipe, split hashes, table sha, duplicate ids and
pairing. Its claim function is replaced by §3.
