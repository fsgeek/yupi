# Does the ι4 > 0 step survive stratification by class type? Design v0.1 (2026-10-05)

> **Status: DESIGN for an EXPLORATORY analysis.** Committed with its script (`scripts/plateau_stratified.py`)
> before the script runs. Written by the instance of 2026-10-05, which owns the project. The question is suggested
> by data, namely the tabulation in §1, so nothing here can be confirmatory.

## 1. Why

The plateau reading (skeleton v0.2 D2′) says that learner cost tracks the *presence* of long-range dependence,
because classes with ι4 in (0, 0.001] already cost about 0.02 bits. Last-kind fixed effects absorbed about half of
that step in the r1ʀ fits (`relay-free-difficulty-results-v0.1.md`). **The binned profiles never included them**:
not in the owner's reproduction, and not in `scripts/count_plateau.py`, where the count learner's step was read.

An exact-side tabulation of r1 (ε = 1, k = 7, law mass, scratch, 2026-10-05) shows the two sets differ sharply
in observable type:

| | within ι4 = 0 | within ι4 > 0 |
|---|---|---|
| last record DISPATCH | 4.8 % | 56.3 % |
| last record IO_ISSUE | 37.3 % | 5.0 % |
| last record RELEASE | 26.1 % | 12.4 % |
| an IO_ISSUE anywhere in the window | 93.9 % | 47.1 % |
| reset window | 10.7 % | 5.4 % |
| distinct actors 3 / 4 | 47.7 / 43.0 % | 50.6 / 35.3 % |

The "no entity bound yet" guess is not supported, since the actor counts barely differ. The step may compare
"after DISPATCH" with "after IO_ISSUE" more than it compares "some long-range information" with "none".

## 2. Data

The same windows, excess values and covariates as `scripts/count_plateau.py`:
- cells r1–r4 × ε ∈ {1, ½};
- k = 7 test windows;
- the converged transformer (d128, e15, seed-mean of seeds 1–3) and the count learner;
- covariates S = ι1 − ι4, H_kind and log2 mass, with CR1 errors clustered by class.

New covariates are computed from each window's surface records: the last prefix record's kind (LK), whether any
of the 7 prefix records is IO_ISSUE (IO), and the reset flag (R).

## 3. Specifications

- **A.** count_plateau's binned model, unchanged. Gate: its betas must reproduce
  `docs/count-baseline-comparison-2026-10-04.json` to 1e-9. If not, stop.
- **B.** A plus last-kind fixed effects.
- **C.** A plus fixed effects for every observed LK × IO × R cell.
- **D (the step test).** Only windows with ι4 ≤ 0.01. Regress y on 1[ι4 > 0] plus the C fixed effects plus S, H
  and M. The indicator compares classes carrying under 10 millibits of long-range information with classes
  carrying none, within the same observable type.

## 4. Reading rule (declared before running)

For each learner, using D's indicator across the 8 cells:
- **survives:** β > 0 with t ≥ 3 in at least 6 of 8 cells;
- **absorbed:** |t| < 2 in at least 6 of 8 cells;
- **mixed:** anything else.

B and C are reported to show where the low bins go (bin (0, 0.001] and the top bin). They are not scored.

If the step is **absorbed** for both learners, D2′'s plateau reading ("presence of long-range dependence")
becomes "class type, observably indexed", and the confirmatory test must not predict a presence step. If it
**survives**, the plateau reading stands with a stronger control, and the confirmatory prediction should be stated
within strata.
