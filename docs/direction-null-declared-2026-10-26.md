# Fairer null for the direction lean: declared before running (2026-10-26)

> Owning instance. Robustness check of `direction-intervention-result-2026-10-26.md` (I2 failed: real certifies less
> than Dirichlet-random in 19 of 22). The concern is that Dirichlet(1) directions put mass on kinds impossible in the
> state, which moves outputs away from every law and makes "random" artificially safe.

**Family-random null.** R is drawn from the exact family's law groups, all kinds, with probability proportional to
law mass. The output is P_c + α(R − P_c) with α = min(1, e / TV(P_c, R)), at the same per-window e. Same windows, B
and certifier; seed 20261027.

## Predictions

- **N1.** The family-random arm certifies less than the Dirichlet arm in at least 18 of 22 models (two steps). This
  confirms the suspected bias of the first null.
- **N2.** Real < family-random in at least 14 of 22 models (two steps). The lean survives the fairer null.

If N2 fails, the 10-26 lean was an artefact of the Dirichlet baseline, and F11's revision is withdrawn.
