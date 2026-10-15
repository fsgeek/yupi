# Identifiability of the R/G split at finite precision: declared check (2026-10-15)

> Owning instance. Declared before the run. Replaces the grid rounding in the correction to
> `one-step-identifiability-check-2026-10-15.md` (skeleton v0.8 §4(c), owed item 1). Exact side.

**Setting.** Pattern observer, k = 7, KIND, rungs r1–r4, both ε; rows in `~/.cache/yupi-scratch/split-v2/`. For a class
c with exact predictive p_c = P\*(KIND | c) and gap G_c, and a tolerance δ in total variation, the *δ-ball* of c is
the set of classes c′ with TV(p_c, p_c′) ≤ δ. A monitor that knows the kernel but reads the prediction only to
within δ cannot distinguish c from anything in its ball.

**Statistic.** U(δ) = law mass of classes c whose δ-ball contains some c′ with |G_c′ − G_c| ≥ 0.1 bits. Computed on
distinct p vectors (exact grouping first, then ball search between groups), for δ ∈ {0.005, 0.01, 0.02, 0.05}.

**Learner precision, as a bound.** Pinsker: TV ≤ √(KL · ln 2 / 2) with KL in bits. Paper 1 §4's 15-epoch KIND KL means
of ≈ 0.012–0.024 bits give TV bounds of ≈ 0.065–0.09 per window on average; δ = 0.05 is therefore *below* typical
learner imprecision. This is a bound, not a measurement of the models' TV.

**Declared reading.**
- "At a learner's precision, one prediction does not determine the split" may be written if U(0.05) ≥ 25 % on at
  least three of four content rungs at each ε.
- If U(0.05) < 5 % on every content rung, the split stays readable at learner precision, and §4(c) says so.
- Otherwise: report U(δ) as a curve, with no general sentence.
