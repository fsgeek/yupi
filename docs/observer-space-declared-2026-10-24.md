# The observer's design space: declared before computing (2026-10-24)

> Owning instance. Tests the hypothesis in `failure-ledger-2026-10-24.md` §5: what a monitor concludes about a
> learner's uncertainty depends as much on the observer as on the learner. EXPLORATORY with declared predictions. It
> uses the existing k = 6 test dumps (12 models × 10,000 windows) and the scorer's family. No new model runs.

**Observer grid** (prior-aware form, π_pure from Σ_g W_g^β exp(−TV/τ); pure if ≥ 0.9, withheld if ≤ 0.1, else abstain):
- **prior temper** β ∈ {0 (ignore mass), 0.5, 1 (true prior), 2 (over-trusts the prior)};
- **query:** one step or two steps;
- **noise scale:** τ = c × (val mean error), c ∈ {¼, ½, 1, 2}.

That is 32 observers per model. The metric is conservative balanced accuracy (abstain = error), on the headline
population.

**Observer share vs learner share.** In each cell (interface × ε):
- the *observer range* is the max − min over the 32 observers, within a model, averaged over the 3 seeds;
- the *learner range* is the max − min over the 3 seeds, at a fixed observer, averaged over the 32 observers.

## Predictions

- **O1.** In every cell, the observer range exceeds the learner range by at least 3×.
- **O2.** At two steps, with the best c, ignoring the prior (β = 0) costs at most 0.03 against β = 1, in every cell.
  Asking more substitutes for the prior.
- **O3.** At one step, with the best c, β = 0 costs at least 0.05 against β = 1, in at least 3 of 4 cells.
- **O4.** For every model and both queries, the best c is below 1. The declared τ = mean error is too broad everywhere,
  not only at r3 ε = 1.

**If O1 holds,** the ledger's pattern B is a measured property of this setting: the observer's choices move the
verdict more than the learner seed does. Whether that also holds across learners of different *quality* (not just
seeds) is the next step, and it is not tested here.
