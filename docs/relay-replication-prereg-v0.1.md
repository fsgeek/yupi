# Relay replication: pre-registration v0.1 (DRAFT, 2026-10-09)

> **Status: DRAFT, not stamped.** It becomes a pre-registration only after a two-family pre-stamp review, when
> this line is replaced and the commit is OTS-stamped. **No replication model (seeds 1–12) has been trained.**
> Design: `docs/relay-replication-design-v0.1.md`. Frozen scorer: `scripts/relay_replication_score.py` (SCORER_VERSION
> 1.0) with `tests/test_relay_replication_score.py`, committed with this file.

## Claim tested

On test windows where the exact, ceiling-identical relay (r1ʀ) pushes next-KIND information further back
(Δι_kind,4 < −0.05), the typical model's KIND excess is lower with the relay than without it. The comparison is
relative to windows where the relay moves nothing (Δι = 0 exactly). The locality account (Someya et al., ACL 2025)
predicts the opposite sign.

## Models

- **Corpus:** the fresh paired corpus run 0582ffbeb4693d27 (pairing gates passed, 3a19419). Rungs r1, r1ʀ and r1ˢ.
- **Training:** seeds 1–12, each trained on all three rungs. 15 epochs, d = 128, lr 1e-3. `scripts/learner_train.py`
  at a single clean, committed revision that records `git_revision` in run.json. 36 runs.
- **GPU:** 9 one-wave leases (4 runs, `--expected-until` +75 min), with ≥ 60 min between them.
- A seed enters only if all three of its runs reach step 117,195.
- **All 12 seeds are required.** Runs resume from checkpoints, so an infrastructure failure is re-run, not
  dropped. The frozen scorer refuses any seed set other than 1..12. If a seed truly cannot be completed, there is no
  confirmatory verdict. That is reported in a dated addendum, with the remaining seeds as descriptive only.
- **Census:** k = 7, full test split, every run.

## Statistic and test (frozen)

- L_s = mean over {Δι_R < −0.05} of (y_r1,s − y_R,s), minus the same over {Δι_R = 0 exactly}.
- **PASS iff #{s : L_s > 0} ≥ 10 of 12.** The one-sided sign-test p is 0.019, distribution-free.
- **Estimand: the typical (median) model.**
- **Readings:**
  - **pass:** the claim above;
  - **fail with k ≥ 3:** not replicated at the model level. This is a non-answer;
  - **k ≤ 2:** the locality direction holds for the typical model.

## Descriptive (reported, not scored)

- The mean, sd, t and seed-bootstrap CI of L.
- The right arm R_s (Δι > 0.05), where both accounts predict a gain.
- The self-copy contrast LS_s. It is a zero-entropy field, so it is a check for a field × class effect and not a
  gate.
- Per-seed tables.

## Power and false-pass rate

**False pass:** at most 0.019 under any null with median L ≤ 0 (exact binomial), including mixtures, heavy tails
and off-phase seeds.

**Power** (10-02 templates at 15 epochs: L = 0.0072, 0.0137, 0.0031; null spread between two r1 models sd 0.0017):
- ≈ 0.96 if the seed sd is near its point estimate;
- ≈ 0.2 if it is 3× larger (the upper bound of a df-2 estimate).

A miss is a non-answer, and the paper reports it as such.

## Procedure

- Raws are committed unscored, then scored.
- A two-family recompute happens before the verdict is adopted.
- Deviations go in a dated addendum.
- The scorer is not edited after the first replication model trains.
