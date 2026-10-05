# Adversarial review of the 2026-10-04 exploratory relay notes

A Claude reviewer with independent code (`build.py`, `an1.py`–`an7.py`; its arrays, 199 MB, stay in
`~/.cache/yupi-scratch/review-2026-10-04/`) reviewed `relay-v-diagnosis-*` and `relay-free-difficulty-*`. The
review raised eight objections. The owner adopted them only after re-deriving the load-bearing numbers with
separate code: `owner-reproduction-2026-10-04.py`, whose printed outputs are listed below.

**Confirmed by the reviewer.** No code bugs. CR1 matches statsmodels to the printed digit. The joins are exact
(25,005 classes paired one-to-one). Both pre-declared reading rules were applied correctly. The decile table and
the "exact-zero set = classes with ι4_r1 = 0" claim are correct.

**Objections and their disposition (all accepted):**
1. *Changes conclusion.* The H-free separation collapses under last-kind fixed effects. Re-derived: r1ʀ 5 ep,
   ι4_r1 +0.0062 (t 1.2), ι4_r1R +0.0097 (t 1.6).
2. *Changes conclusion.* "Speed-up / no lasting advantage" is contradicted. Re-derived: the 15-ep gain is
   +0.0041 off the zero set, and the paired step at 15 ep is +0.0039 (t 5.9).
3. *Changes number.* The 15-ep gain is neither "uniform" nor "gone". Re-derived as in 2.
4. *Wording.* The step marks a class type. Re-derived: binned effects of +0.022 at ι4 in (0, 0.001] (t 8.0), a
   plateau through 0.4, and +0.049 above 0.6, in all four fits.
5. *Wording.* n_relay is 7 − distinct actors. Re-derived: identity holds in every window, in both arms.
6. *No issue.* The "fewer entity records" confound does not apply.
7. *Minor.* 9 windows have 0 < ι4_r1 < 1e-9. This is negligible for the fits.
8. *Minor.* The V-diagnosis log's mtime equals the commit time. Cause: the log was written to
   `~/.cache/yupi-scratch/census/` at run time (22:35) and `cp`'d into `docs/` at commit, which updates the mtime.
   The content is the run's stdout, unchanged.

Corrections: read-first blocks at the top of both results notes, and "per bit" cautions at the top of the D1 and
converged-ladder verdicts. Skeleton v0.2 was written after the review, from the corrected reading.
