# Corrected-Kernel Rerun — Drift Report (v0.1)

**Status: measured note, written 2026-08-20 13:57 PDT (`date` in the writing command),
ninth instance.** First rerun of the C1 measurement chain under the
corrected kernel (handoff fix d69fa87, guards 87ed0a7), per the
adjudication note's revised ordering. 20 new raws
`docs/c1-*-corrected-2026-08-20.json`; every day-5–7 raw untouched.
Thresholds remain unstamped: these runs are **corrected-kernel
exploratory**. Scripts unchanged except one repair below.

## The gate that caught its own reference

The first chain run FAILED at `c1_divergent_resolution.py`: its
state-level exact-equality gate (v0.1.2, hardened after the second
truthsayer round) compared the corrected kernel against the day-seven
full-context reference — a buggy-kernel artifact — and refused. That is
the gate doing its job: it detected a law change between reference and
measurement. Repaired (v0.1.3) by pointing the reference at the
corrected-kernel full-context raw produced earlier in the same chain;
8/8 exact-equality assertions pass. The failure and repair are part of
the record on purpose.

## Drift: buggy law → corrected law (max over entropy/mass/gap leaves)

| note | law | max quantity drift | where |
|---|---|---|---|
| support-exact | (12,·,·) family | 0.0010 | mean_support 1.6097→1.6107 |
| predictive targets | (12,2,2) | 0.0027 | kinds2 gap 0.7887→0.7860 |
| predictive targets | (12,12,2) | 0.0037 | state div. mass 0.9773→0.9736 |
| query ceilings | (12,2,2) | 0.0028 | state entropy 2.9265→2.9236 |
| Q4 ceilings | (12,2,2) W4 | 0.0005 | total 0.9325→0.9330 |
| Q4 ceilings | (12,12,2) W4 | 0.0001 | total 0.6676→0.6677 |
| offset-vs-state | (12,2,2) | 0.0032 | H(S\|w,U) 1.5944→1.5911 |
| divergent grid | (12,2,2) | 0.0002 | div_mass 0.0137→0.0134 |
| predictive targets | (14,2,2) | 0.0052 | kinds2 gap 0.8208→0.8156 |
| query ceilings | (14,2,2) | 0.0285 | endpoint-14 state entropy 3.6910→3.6626 |
| Q4 ceilings | (14,2,2) W4 | 0.0047 | total 1.0774→1.0820 |
| divergent grid | (14,2,2) | 0.0011 | div_mass 0.0652→0.0663 |
| **predictive targets** | **(14,4,2)** | **0.0409** | **div. mass 0.3952→0.3543** |
| query ceilings | (14,4,2) | 0.0137 | endpoint-8 state entropy |
| Q4 ceilings | (14,4,2) W4 | 0.0044 | total 0.8737→0.8780 |
| **divergent grid** | **(14,4,2)** | **0.0411** | **div_mass 0.4114→0.3703** |
| offset-vs-state | (14,4,2) | 0.0046 | H(U\|w) 0.7258→0.7304 |
| offset-vs-state | (14,8,2) | 0.0027 | clock share 0.1621→0.1649 |

Count-level scars of the bug: −6 windows at (12,2,2) r3/r4; horizon-8
endpoint census 1244→1135 states (the 109 removed are exactly the
contaminated set); state P-next classes 353→317.

## Qualitative claims re-verified on the corrected raws

- **Divergent-grid structure holds**: observer-monotonicity 24/24
  columns, pair-set nesting 72/72 (asserted in-run), r4 > r1 in all six
  diagonal cells, and the diagonal r3→r4 sign pattern (− at (12,2,2),
  + at the T_ep=14 laws) all survive.
- **Divergent class non-empty at every law/rung/ε** (deliverable 5.3's
  existence answer stands).
- **Conservation identities** (irreducible-term rung-invariance) held
  in-run via the scripts' own checks; offset-is-a-coordinate-of-state
  (I(U;S)=H(U)) reproduced at all three offset-vs-state laws.
- **Magnitudes to re-quote**: (14,4,2) divergent masses are ~10%
  (relative) lower than the day-seven values; the (14,·) endpoint-14
  entropies move in the second decimal. Any prose citing those specific
  numbers must cite the corrected raws from now on.

## Not rerun here

Sync sweep (`c1_sync_sweep.py` and per-endpoint family), δ/δ_sync/TV
sweeps, multi-waiter census, rung-gap decompositions, window-prior and
clock experiments — queued; the sweeps should be rerun once, under
whatever thresholds the pending second stamp fixes, to double as the
confirmatory pass on fresh corrected-kernel curves (subject to the
audit's fresh-laws caveat on confirmation).

## Caveats

- Same scripts as the originals (modulo the v0.1.3 reference repair);
  single-path aggregation over two-path-gated posteriors, as before.
- σ/entity naming remains unimplemented: all quantities are the
  role-known structural quotient (audit finding 3).
- Drift maxima are per-leaf maxima of |old − new| over leaves matching
  entropy/mass/gap patterns; full leaf-level diffs reproducible from the
  committed raw pairs.
