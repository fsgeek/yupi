# Worst-case certification with a known error bound: result (2026-10-25)

> Owning instance. Scores `certified-bound-declared-2026-10-25.md` (stamped at bd55470 before running). Script:
> `scripts/certified_bound.py`. Raw: `certified-bound-2026-10-25.json`. Ten learners; 8,836 fresh paired test windows
> each. The certifier uses no prior; the bound B is fitted on val.

## At q = 0.95 (share of pure windows certified pure, one step → two steps)

| learner (val one-step mean TV) | one step | two steps | false certificates, one / two |
|---|---|---|---|
| d128, 45 epochs (0.023) | 0.074 | 0.841 | 0.18 % / 0.11 % |
| d128, 5 epochs (0.026) | 0.085 | 0.693 | 0.23 % / 0.14 % |
| d256, 45 epochs (0.029) | 0.073 | 0.681 | 0.18 % / 0.07 % |
| d128, lr 3e-4 (0.030) | 0.073 | 0.507 | 0.41 % / 0.24 % |
| d256, 15 epochs (0.031) | 0.072 | 0.670 | 0.21 % / 0.09 % |
| d64, 15 epochs (0.033) | 0.034 | 0.637 | 0.29 % / 0.18 % |
| GRU 256×2 (0.040) | 0.023 | 0.430 | 0.42 % / 0.22 % |
| d64, 5 epochs (0.042) | 0.042 | 0.237 | 0.74 % / 0.62 % |
| d64, lr 3e-4 (0.061) | 0.000 | 0.027 | 0.90 % / 1.14 % |
| d256, lr 1e-4 (0.077) | 0.000 | 0.016 | 0.91 % / 0.89 % |

Withheld windows are certified withheld at 0.66–0.95 at one step and 0.72–0.95 at two.

## Predictions

- **B1 (two steps certify more pure windows than one, ≥ 8 of 10): holds, 10 of 10.**
- **B2 (false-certificate rate ≤ (1 − q) + 0.01 at every q and s, ≥ 9 of 10): holds, 10 of 10.** The worst rates are
  1.7 % (q = 0.90), 1.1 % (q = 0.95) and 1.4 % (q = 0.99).
- **B3 (one step, q = 0.95, the four worst learners certify < 0.5 of pure windows): holds.** In fact every learner
  certifies at most 0.085 at one step.
- **B4 (certified share falls as q rises): holds** for every learner, at both s.

**The check on the bound:**
- **One step:** the val bound under-covers test. The share of test windows with error above B is 0.154–0.181
  (q = 0.90), 0.074–0.103 (q = 0.95) and 0.016–0.028 (q = 0.99), against nominal 0.10 / 0.05 / 0.01.
- **Two steps:** 0.087–0.156 / 0.040–0.073 / 0.009–0.020.
- False certificates stay far below the error-above-B rate, because errors beyond B seldom reach the other kind.

## What this restores

The worst-case form of the withdrawn claim, now with an error bound the observer can know. For these learners,
without a prior:
- one output almost never certifies "this is randomness, not hidden state" (≤ 8.5 % of pure windows at 95 %);
- a second question certifies most of them for good learners (51–84 %), at false-certificate rates of about 0.1–0.4 %.

For the worst learners, neither suffices. The certificate is honest about that: it abstains instead of guessing.
That is the auditor's version of the question, and it is the version PACMI asks.
