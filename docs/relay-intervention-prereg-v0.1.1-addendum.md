# Relay intervention pre-registration: addendum v0.1.1 (2026-09-30)

> **Status: CONFIRMATORY clarification**, stamped by the owner **before any r1ʀ model has
> finished training or been censused** (the six r1ʀ runs are queued behind the converged ladder).
> It resolves four ambiguities in `relay-intervention-prereg-v0.1.md` that the adversarial review
> of `scripts/relay_paired.py` raised (workflow wf_f6601893-92e). In each case the stricter
> reading is chosen. The v0.1 file is unchanged.

1. **R3's row.** R3 reads the `full_plus_log2_class_mass` model of the frozen
   `implicit_info_bintest.py`, the model the D1 verdict and R1's band refer to. It runs with an
   explicit `--glob` naming only the r1ʀ census raws of the arm (the default glob does not match
   "r1R" names, and would pool other runs if it did).
2. **Standard errors for R2 and R4.** R2 uses the set mean's se alone. That is the stricter
   reading for a test that passes when the difference is small. R4 is scored with the set mean's se
   and the intercept's se **added in quadrature**, the stricter reading for a test that passes
   when the difference is large. `relay_paired.py` already reports that t, and it becomes the
   scored one. R4's threshold stays t ≤ −3.
3. **Arm controls.** The primary arm's r1 controls are exactly
   `docs/learner-window-census-r1-eps1-2M-seed{1,2,3}-2026-09-21.json` (5-epoch checkpoints).
   The secondary arm's r1 controls are new censuses of the 15-epoch r1 ε = 1 checkpoints
   (`runs/gpu/…-d128-lr1e-3-e15-s{1,2,3}`), run with the relay-aware census and gated on
   checkpoint provenance. For each arm, the census raws' checkpoint paths are checked against its
   recipe (5 against 15 epochs) before scoring.
4. **R4's relation to R1.** Under an exactly linear law with the same intercept, R4 follows from R1.
   R4 is kept as the test of the direction the linear fit does not force: the relay making
   things worse where it adds load. The deciles of Δι are reported, so a non-linear or one-sided
   effect is visible either way.
