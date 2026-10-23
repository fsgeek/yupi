# Certification margin: result (2026-10-22)

> Owning instance. Scores `certification-margin-declared-2026-10-22.md` (declared, plus an addendum written before
> any data was read). Script: `scripts/certification_margin.py`. Raw: `certification-margin-40-8-2-k7-2026-10-22.json`.
> The per-window capture re-ran the monitor, and its scores are identical to the committed run.

## M1 (declared: in every model)

- **Low half (a check, per the addendum):** the m = 0 decision is "pure" on 100 % of low-t windows in all 12 models.
- **High half (the test):** "pure" on 1.4–21.3 % of windows with t > 0.6 μ. It is at most 10 % in 8 of 12 models and
  exceeds it in 4 (r1 ε = 1 seeds 2, 3: 16.0 %, 15.3 %; r3 ε = 1 seeds 1, 3: 17.2 %, 21.3 %).
- **M1 fails** (it was declared for every model).

## What was not expected, and matters more

μ is tiny. The per-model median μ over pure windows is about 0.001 (r1 ε = 1), 0.003 (r3 ε = 1) and below 0.0005
(ε = ½), against model errors with a median of 0.008–0.032. Over pure *laws* (mass-weighted, three cells checked):
- the nearest non-pure law has median G of 0.0033–0.0285 bits;
- 87–99 % of pure mass has its nearest non-pure neighbour at G < 0.01 bits at r1 ε = 1 and r3 ε = ½ (7 % at r3 ε = 1);
- the nearest G ≥ 0.1 law is at TV ≈ 0.015 in every cell checked.

So "pure randomness" is not isolated in law space. It is surrounded, very closely, by laws carrying a trace of
withheld state. The margin that matters for the declared question (pure vs substantial withheld) is about 0.015, not μ.
This shows the declared kind monitor was answering a different question, and its interpretation is corrected in
`kind-classifier-result-2026-10-22.md`.

## For what comes next

- **The certification margin is still the right object, measured against the right neighbour set.** Define
  μ_c(γ) = TV to the nearest law with G ≥ γ. It is a family indexed by how much withheld state one cares about, not a
  single number. At γ → 0 it is tiny everywhere. At γ = 0.1 it is about 0.015.
- **Follow-ups 3 (two-step queries) and 4 (interfaces) are about widening μ_c(γ).** That is now a well-posed exact
  quantity to compute per interface and per query class, before any learner.
