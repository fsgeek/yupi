# Two-step certification margin: result (2026-10-23)

> Owning instance. Scores `two-step-margin-declared-2026-10-23.md`. Rows are built by `scripts/two_step_split.py` (a
> derivative of `kind_uncertainty_split.py` that adds each class's exact two-step KIND law). Analysis:
> `scripts/two_step_margin.py`. Raw: `two-step-margin-40-8-2-k7-2026-10-23.json`; row hashes in
> `two-step-rows-sha256-2026-10-23.txt`.

## Integrity (before reading any margin)

- The §3.1 ceiling gate holds on all ten cells.
- **Two-step marginal equals one-step law:** exactly, on every class. Checked at the small law (386 classes) and at
  the frozen law, r3 ε = 1 (146,455 classes).
- **One-step columns:** identical to the pinned `split-v2` rows at r3 ε = 1 (the cell checked).

## The coin's margin to substantially withheld state (γ = 0.1), median over the coin's classes

| | floor 0: μ1 → μ2 | floor 1e-5 | floor 1e-4 |
|---|---|---|---|
| r0, ε = 1 | 0.027 → 0.120 | 0.027 → 0.120 | 0.027 → 0.122 |
| r1–r4, ε = 1 | 0.015 → 0.130–0.145 | 0.023 → 0.137–0.169 | 0.108–0.152 → 0.227–0.443 |
| r0, ε = ½ | 0.027 → 0.119 | 0.027 → 0.119 | 0.028 → 0.121 |
| r1–r4, ε = ½ | 0.014–0.015 → 0.117–0.130 | 0.014–0.017 → 0.179–0.187 | 0.160–0.205 → 0.377–0.504 |

The 10th percentile of the coin's μ2 at floor 0 is 0.032–0.054 on r1–r4 and about 0.065–0.070 on r0. Medians over all
pure classes (μ2, floor 0) are 0.110–0.136 on r1–r4 and 0.117–0.119 on r0.

## Predictions

- **T0 (check): holds.** No pure class has μ2 < μ1 at any floor, interface or ε.
- **T1: holds.** At floor 0 the coin's median μ2 is 0.117–0.145 on r1–r4 at both ε, against ≥ 0.05 declared. That is
  8–9.5 times the one-step margin, and above the trained models' typical one-step error (median TV 0.008–0.032).
- **T2: holds as declared, but not by the stated mechanism.** μ2/μ1 at floor 0 is 7.8–9.5 on r1–r4 against 4.3–4.5 on
  r0. The absolute μ2 is about the same everywhere (about 0.12). The ratio is larger on rich interfaces because their
  μ1 is smaller (rare neighbours), not because those neighbours are more exposed at the second step. The declared
  reason ("rare neighbours betray themselves at the second step") is not supported by this measurement.

## Reading

- **Asking more works where observing more did not, existentially.** Against *any* substantially withheld law,
  however rare, the dominant randomness is about 0.12 TV away at two steps, on every interface. At one step, rare
  neighbours on the rich interfaces bring it within 0.015.
- With a prior (mass floor), both levers compound. A floor of 1e-4 with two steps gives 0.23–0.50 on r1–r4.
- This is the constructive counterpart the founding document asked for, in exact form, *for this world*: a
  single-step output cannot certify the dominant randomness against every withheld alternative at learner
  precision, and a two-step query can, by a margin about eight times wider.
- It is a statement about exact laws. Whether trained models' two-step predictions are precise enough to use it is a
  separate, learner-side question.

## Caveats

- **Window position.** At position 7 the second step lies beyond the 8-record window. The exact law is well defined
  (time-homogeneous kernel), but a learner trained on 8-record windows can only be queried for two steps from
  position 6. A learner test must be built at k = 6. That needs the one-step split at k = 6 too.
- **Dominance of the coin.** The coin carries 86–95 % of pure mass, so "the dominant randomness" means this one
  mechanism. Other pure laws are included in the all-pure medians, which agree.
- **One world.** The size of the widening (eight times) belongs to this kernel. Whether a second step widens the margin
  in general depends on withheld state inducing serial correlation, which is a property of the mechanism.
