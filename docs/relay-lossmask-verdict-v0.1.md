# The loss-masked relay arm: verdict v0.1 (2026-10-13)

> **Status: VERDICT against `docs/relay-lossmask-prereg-v0.1.md`**, which was committed and OTS-stamped at dc26a03
> before any masked model was trained. Exploratory in scale (3 + 3 + 3 models). Scored by the owning instance,
> which also wrote the pre-registration. Two-family review of this verdict is owed (§6).

## 1. Gates (prereg §5): all pass

For each of the three runs, `run.json` records:
- `unscored_fields: ["OBJECT"]`;
- git revision 0ef005d with `git_dirty: false`;
- corpus manifest sha256 `d8c23cab…`, the r1R corpus `fd5da4c31e43d73d`;
- `steps_total` 117,195.

Each census JSONL matches its recorded sha256, with 84,949 windows each. Training ran on the GPU under an ayllu-gpu
lease from 13:14 to 14:07 PDT, and the censuses ran on CPU from 14:08 to 14:11 PDT.

## 2. The measurement

KIND shortfall: the mean of `by_field.kind` over the k = 7 test windows, from the frozen census script.

| | seed 1 | seed 2 | seed 3 |
|---|---|---|---|
| r1 (no relay) | 0.01570 | 0.01464 | 0.01576 |
| r1R (relay in input and in loss) | 0.01296 | 0.00947 | 0.01252 |
| **r1Rm (relay in input, not in loss)** | **0.02809** | **0.04114** | **0.03072** |

## 3. Readings (prereg §3)

- **P (presence suffices): NOT MET.** No value in S is below min(r1) = 0.01464.
- **T (supervision contributes): MET.** Every value in S is above max(r1R) = 0.01296. The exact one-sided
  permutation p is 1/20, the smallest this design allows.
- The "both" and "neither" bullets do not apply: "both" requires P, and "neither" is defined as the case where
  neither pattern holds.

**Scored reading: T.**

## 4. Beyond the pre-registration (EXPLORATORY)

- **S also lies entirely above r1.** The smallest r1Rm value (0.02809) exceeds the largest r1 value (0.01576),
  again an exact p of 1/20 against r1. The pre-registration did not foresee this ordering and fixed no reading
  for it. **A copy that is present in the input but never a training target leaves the learner worse than no copy
  at all.**
- **Where the deficit sits, checked at the finest grain before interpreting it.** We compared r1R and r1Rm models
  on the *same* 20,000 r1R test windows, using raw next-KIND cross-entropy at each record position (`scripts/relay_lossmask_kind_by_position.py` →
  `relay-lossmask-kind-by-position-2026-10-13.jsonl`). The two arms agree at records 1–5, to within 0.0022 bits. They part at records 6–8. At the
  8th record r1Rm is worse by 0.017–0.032 bits (r1R 1.001–1.006, r1Rm 1.022–1.034), the same size as the census
  difference. The deficit is where the far information is, not spread evenly, and the census is not producing it.
- **ACTOR is also worse.** The r1Rm actor shortfall is 0.0328–0.0363, against r1 0.0299–0.0314 and r1R
  0.0262–0.0308.
- **Overall loss is not.** Rescaled to the same token set, r1Rm's validation loss on non-OBJECT tokens is about
  r1's. The masked models are not broken overall. They are worse specifically at late, far-dependent predictions.
- **The relay field itself** is predicted at 17.7–19.1 bits per window by r1Rm, which never trained on it. That is
  expected (prereg §4), and it is not subtracted from anything.

## 5. What this changes

**The relay result, revised.** The 3 vs 3 gain of r1R over r1 cannot be read as "presenting information near its
point of use helps the learner". When the near copy is present but not trained on, the learner does worse than
with no copy. Within these arms, the gain requires training the learner to *produce* the back-reference, which is
a lookup of the same actor's last event. This is auxiliary supervision of the lookup that next-KIND prediction
needs. Of the three rival mechanisms, it is the only one this arm isolates. The pure-distance reading ("the copy
shortens how far the learner must look") predicted r1Rm ≤ r1, and that prediction failed on every model.

**Not established:**
- *Why* an unsupervised variable field hurts. Candidates: the learner must learn to read a varying token stream
  with no direct signal; capacity spent on uninterpreted inputs; or the scored-token difference (r1 trains on a
  trivial placeholder at OBJECT, r1Rm on nothing there).
- Whether supervision without presence would help. That arm is not constructible autoregressively, since a
  target becomes the next input.
- Anything at 5 epochs or at ε = ½.

**Prior work this now touches:** sub-task supervision and scratchpads in sequence learning (Abbe et al. 2024,
cited in `literature-pass-2026-10-09.md`; Wies et al. 2023, to verify before citing). The relay is closer to an
auxiliary target than to an input index.

## 6. Owed

- Two-family review of this verdict and of the §4e rewrite.
- Inventory §J and skeleton v0.6's relay paragraph, rewritten to this reading.
- The scratch position check committed as a script with a raw, so §4's position numbers have a source.
