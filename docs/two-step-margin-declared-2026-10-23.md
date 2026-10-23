# Two-step certification margin: declared before computing (2026-10-23)

> Owning instance. EXPLORATORY, exact side. Question: can asking more (the joint law of the next two KINDs) separate
> pure randomness from withheld state, where observing more (richer interfaces) and one-step prediction cannot?
> Hypothesis: withheld state correlates successive events; pure randomness, given the state, does not, in the way a
> mixture does.

**Quantities.** Classes and their kinds exactly as in the one-step work: pure (G < 1e-12, H\* > 1e-12) and withheld
(G ≥ 0.1), from the one-step next-KIND split at position 7. For each class, the exact two-step law
P2_c(k1, k2) = Σ_s P(s | c) P(k1, k2 | s), using `predict_paths.next_kinds_by_paths(s, cfg, programs, 2)`.
- μ1(γ, floor): TV from the coin's one-step law to the nearest withheld class's one-step law whose law mass is at least
  `floor`.
- μ2(γ, floor): the same with two-step laws.
- Reported at γ = 0.1, floors {0, 1e-5, 1e-4, 1e-3}, all interfaces r0–r4, both ε. Also for every pure law, not only
  the coin.

**A check, not a test.** T0: TV between joint laws is at least TV between their marginals, so μ2 ≥ μ1 whenever the
neighbour sets coincide. Grouping by two-step law can split one-step groups, so this is checked numerically, not
assumed.

**Predictions.**
- **T1.** At floor 0 (existential), the coin's μ2(0.1) ≥ 0.05 on every content interface r1–r4 at both ε. That is more
  than three times the one-step 0.015, and above the trained models' typical one-step error (median 0.008–0.032).
- **T2.** At floor 0, μ2(0.1)/μ1(0.1) for the coin is larger on r1–r4 than on r0 at both ε. Rich interfaces' rare
  neighbours are mixtures whose second step betrays them.

**If T1 holds:** a two-step query makes the dominant randomness certifiable even against rare neighbours. That is a
constructive, exact counterpart to the single-output limit, and the query-class definition the founding document asked
for. **If it fails:** neither observing nor asking more helps existentially, and certification needs a prior (the
prior-aware monitor). That would also be worth knowing.
