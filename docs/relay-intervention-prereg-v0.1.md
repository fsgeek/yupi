# The relay intervention: pre-registration v0.1 (2026-09-30)

> **Status: CONFIRMATORY, pre-registered** by the owner (instance of 2026-09-28/29/30). The
> exact side (`docs/relay-exact-side-2026-09-30.json`, all gates passed; two adversarial
> reviews, no blocking findings) was computed first, as design §4 required. **No r1ʀ model has
> been trained** when this is stamped. Design: `docs/relay-intervention-design-v0.1.md`.

## Exact side that sizes the test (ε = 1, k = 7)

- The relay moves the law-mass mean ι_kind,4 from 0.257 to 0.163 (Δ 0.094). The per-class Δι
  is widely spread: q.05 −0.096, median 0.012, q.95 0.528.
- **27.8 % of law mass has Δι < 0.** For those classes the relay adds information that an
  order-4 view cannot use, so their long-lag load rises. This is not a leak. The ceiling is
  identical class by class (gates A–C, and a reviewer's independent re-derivation of all 14
  tables).
- The exact-zero set (Δι_kind,4 = 0 as equal Fraction mixtures) is 9.5 % of mass. Its
  information is unchanged at lags ≥ 4, but not at lags 1–3 (reviewer; mean Δι_1 0.009).

## Models

r1ʀ ε = 1 (paired corpus fd5da4c31e43d73d-r1R), seeds 1–3:
- **Primary arm:** d = 128, 5 epochs, lr 1e-3 → 1e-4. The controls are the r1 ε = 1 5-epoch
  seeds 1–3 (census raws of 2026-09-21).
- **Secondary arm:** 15 epochs. The controls are the r1 ε = 1 15-epoch seeds 1–3.

## Frozen analysis (implemented before any r1ʀ census exists)

- Per test window w with ≥ 7 records (the same 84,949 windows at both rungs):
  Δexcess_w = mean over r1 seeds of the realized KIND excess − mean over r1ʀ seeds.
- The ceiling is identical across the pair, so Δexcess_w = mean log q_r1ʀ(kind) − mean log
  q_r1(kind). No ceiling noise enters.
- Regressor: Δι_w = Δι_kind,4 of w's class (the committed per-class table). OLS with HC1
  errors, intercept free.
- The relay field's own excess is reported separately and does not enter.

## Predictions (primary arm)

- **R1 (causal slope).** The slope of Δexcess on Δι is positive with t ≥ 3, and its value lies in
  [0.0165, 0.066] (within a factor of two of the verdict's frequency-controlled pooled r1 ε = 1
  β_long, 0.033).
- **R2 (nothing moved past lag 4).** On the exact-zero set, the mean Δexcess lies within ±2 se of
  the regression intercept's value at Δι = 0. A generic effect of the new field shows up as a
  nonzero intercept, which is reported. It does not count against R1.
- **R3 (the relocated learner obeys the same law).** In each r1ʀ seed, the frozen verdict
  analysis (`implicit_info_bintest.py`, sha256 `c73fab6b…`, m = 4) on r1ʀ's own ι gives
  β_long > 0 with t ≥ 3.
- **R4 (the relay can hurt).** On windows with Δι < −0.05 (the relay added long-lag load), the
  mean Δexcess minus the intercept is negative with t ≤ −3. The r1ʀ models are *worse* there.

The secondary arm reports R1–R4 without thresholds.

## Reading

R1 and R4 together are the causal claim: the same histories, carrying the same information, cost
the learner more when that information sits further back, and less when it sits closer, in both
directions. A null R1 with this spread of Δι withdraws the verdict's distance reading.
