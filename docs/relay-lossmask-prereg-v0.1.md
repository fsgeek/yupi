# The loss-masked relay arm: pre-registration v0.1 (2026-10-13)

> **Status: PRE-REGISTRATION, committed and OTS-stamped before any masked model is trained.** Exploratory in
> scale (3 + 3 + 3 models; the smallest exact p this design can give is 1/20), and it is labelled that way in
> paper 1. Owning instance. Occasion: the Claude reviewer's blocking finding 1 on the paper 1 drafts
> (2026-10-13). Every window position is scored in training (`src/yupi/learner/data.py`), so r1R models are also
> *trained to predict* the relay value, i.e. to find the same actor's last record and copy its KIND. Their gain over
> r1 could come from that auxiliary supervision, and not from the copy being present in the input.

## 1. The arm

r1Rm is r1R with the OBJECT slot excluded from the training loss (`--unscored-fields OBJECT`, tests in
`tests/test_learner_data.py` and `tests/test_learner_train.py`). Everything else equals the 10-02 r1R secondary
arm:
- the same corpus, `corpus/c1prime-loop-40-8-2-r1R-eps1/fd5da4c31e43d73d` (manifest sha256 `d8c23cab…84df3`);
- d = 128, 15 epochs, lr 1e-3 → 1e-4, batch 256, warmup 500;
- seeds 1, 2 and 3;
- the GPU, under deterministic settings.

The model still *sees* the relay field as input. It is never trained to produce it.

## 2. The measurement

For each model, the KIND shortfall is the mean of `by_field.kind` over the k = 7 test windows. It is computed by
the frozen `scripts/learner_window_census.py`, the estimator of the relay verdict, on the same test split. The
comparison sets are already fixed and were read before this document was written:
- r1 (15 ep): 0.01570, 0.01464, 0.01576
- r1R (15 ep): 0.01296, 0.00947, 0.01252

## 3. Readings, fixed now

Let S = the three r1Rm seed means.
- **P (presence suffices):** every value in S is below min(r1) = 0.01464. In that case the copy in the input lowers
  the shortfall without being a training target (exact one-sided permutation p = 1/20 against r1).
- **T (supervision contributes):** every value in S is above max(r1R) = 0.01296 (p = 1/20 against r1R).
- **Both P and T:** S lies strictly inside (0.01296, 0.01464). Presence helps, and supervision adds to it.
- **Neither, in the other direction:** some value in S is ≥ 0.01464, or some is ≤ 0.01296, without the pattern
  above. Then the arm does not separate the readings with three seeds, and paper 1 says so.

Whatever S shows, paper 1's relay paragraph is rewritten to its reading. Under "neither", the relay claim becomes
"r1R models beat r1 models; whether through presence or supervision is not separated."

## 4. Reported alongside, not scored

- The per-model relay-field (OBJECT) excess of r1Rm. It is expected to be large, since the field is never trained.
- The ACTOR shortfall, from `by_field.actor`.
- The training and validation loss curves.

## 5. Gates

- Each run's `run.json` records `unscored_fields: ["OBJECT"]`, a clean git revision, the corpus manifest sha256
  above, and steps_total 117,195.
- The census reproduces its own `crosscheck` block, as for the 10-02 raws.
