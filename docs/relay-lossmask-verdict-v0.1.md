# The loss-masked relay arm: verdict v0.1 (2026-10-13)

> **Status: VERDICT against `docs/relay-lossmask-prereg-v0.1.md`**, which was committed and OTS-stamped at dc26a03
> before any masked model was trained. Exploratory in scale (3 + 3 + 3 models). Scored by the owning instance,
> which also wrote the pre-registration. Two-family review of this verdict is owed (§6).

## 1. Gates (prereg §5): pass, with one substitution disclosed in §6

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
- **T (supervision contributes): MET.** Every value in S is above max(r1R) = 0.01296. The pre-registered calculation is the *unpaired* exact
  one-sided permutation, p = 1/20, which assumes the six models are exchangeable. Seeds are matched across arms
  (same initialization and batch order), and swapping labels only within seed pairs gives p = 1/8 (Codex verdict
  review, finding 3). This does not change whether T's literal threshold was met.
- **Ambiguity in the pre-registration, disclosed (Claude verdict review, finding 5).** Literally, the "neither"
  bullet reads "some value in S is ≥ 0.01464 … without the pattern above", and S meets its first clause. T and
  "both" also overlap. The verdict scores the 2×2 reading: P fails and T holds. Under that reading the "neither"
  bullet does not fire. Read the other way, its pre-committed rewrite ("whether through presence or supervision is
  not separated") would apply. §5 below is written to be compatible with both readings.

**Scored reading: T.**

## 4. Beyond the pre-registration (EXPLORATORY)

- **S also lies entirely above r1.** The smallest r1Rm value (0.02809) exceeds the largest r1 value (0.01576),
  again an exact p of 1/20 against r1. The pre-registration did not foresee this ordering and fixed no reading
  for it. **A copy that is present in the input but never a training target leaves the learner worse than no copy
  at all.**
- **Where the deficit sits, checked at the finest grain before interpreting it.** We compared r1R and r1Rm models
  on the *same* 20,000 r1R test windows, using raw next-KIND cross-entropy at each record position (`scripts/relay_lossmask_kind_by_position.py` →
  `relay-lossmask-kind-by-position-2026-10-13.jsonl`). This check uses unconditional per-token cross-entropy; the census conditions on the continuation (Codex finding
  4). Seed-paired, r1Rm − r1R is −0.0029 to +0.0023 bits at records 1–5. It grows
  from record 6 on (+0.0033 to +0.0112) and reaches +0.0158 to +0.0329 at record 8, the same size as the census
  gaps (0.0151–0.0317). The onset is gradual. The check compares r1Rm with r1R only, not with r1. Two readings remain open: the deficit sits where the far information is, or where the most unscored relay tokens
  precede the prediction. Either way the census is not producing it.
- **ACTOR is also worse.** The r1Rm actor shortfall is 0.0328–0.0363, against r1 0.0299–0.0314 and r1R
  0.0262–0.0308.
- **Overall loss is not.** On non-OBJECT tokens, r1Rm's validation loss is 0.7580–0.7582 nats/token against r1's
  0.7583–0.7593 (Codex's recomputation; the Claude reviewer's rescaling agrees to within 0.001). The masked models are not broken overall. They are worse specifically at late, far-dependent predictions.
- **The relay field itself** is predicted at 17.7–19.1 bits per window by r1Rm, which never trained on it. That is
  expected (prereg §4), and it is not subtracted from anything.

## 5. What this changes (revised after the Claude verdict review, same day)

**What the arms show.** The relay's gain over r1 requires the relay value to be a training *target* as well as an
input. With the copy present but unscored, every model does worse than every r1R model and also worse than every
r1 model.

**What they do not show:**
- That supervision is *sufficient*, or that it is "the mechanism". Supervision may be what teaches the learner to
  read the near copy, which would then help through distance or binding. These arms cannot separate a presence ×
  supervision interaction.
- That distance plays no role. Only a distance account in which an unscored copy costs nothing is contradicted. A
  real distance benefit outweighed by the cost of an unsupervised variable field fits the data as well.
- That "an unscored copy hurts" is a fact about the copy. Two confounds are open:
  - (a) r1 has a constant MASKED token in that slot, while r1Rm has varying KIND-typed tokens, which may act as
    decoys. This is the variable-field confound named in §5.3 and §6.
  - (b) r1 trains a trivial MASKED target there, and r1Rm trains nothing.
  - (c) Leaving OBJECT out shrinks the cross-entropy denominator from 76.4 M to 61.6 M training targets, so each
    remaining loss term weighs about 24 % more per step (Codex verdict review, finding 1).

**The arms that would separate them** (none run; the blind r1D/r1S pilots stay unopened):
- **Supervision without presence**, which is constructible because the corpora are paired: inputs from the r1
  corpus, targets from the r1R corpus. The model predicts the relay value at OBJECT and then sees MASKED.
  (Correction: v0.1 called this "not constructible autoregressively". It is not a generative model of one corpus,
  but it is well-defined training.)
- **r1m:** r1 with OBJECT unscored and loss normalization matched, which closes (b) and (c).
- **A masked variable-but-uninformative field**, which closes (a).

The verdict's original §5 is at commit 880e83b.

## 6. Owed

- **Gates, disclosed.** Prereg §5 asked each census to "reproduce its own `crosscheck` block", but neither these
  raws nor the 10-02 raws have one. A sha256 match stood in for it. The Claude reviewer re-ran the current census
  on the r1R seed-1 checkpoint and reproduced the 10-02 per-window file bit-exactly, so evaluator drift is ruled
  out. Seed 2 and 3 census raws record `+dirty`, because the seed-1 raw had already been written to `docs/`.
- The loss curves promised in prereg §4 are owed as a raw, as is the rescaled validation-loss figure.

- Two-family review of this verdict and of the §4e rewrite.
- Inventory §J and skeleton v0.6's relay paragraph, rewritten to this reading.
- The scratch position check committed as a script with a raw, so §4's position numbers have a source.
