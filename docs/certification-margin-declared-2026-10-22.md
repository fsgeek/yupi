# Certification margin: declared before any per-window data is read (2026-10-22)

> Owning instance. EXPLORATORY, with a declared prediction. Follows `kind-classifier-result-2026-10-22.md`:
> pure-randomness windows are mostly abstained on, because the outputs sit nearest small-withheld laws.

**Definition.** For a class c whose truth is pure, the *certification margin* μ_c is the TV distance from its exact
law P_c to the nearest exact law (same cell table) whose kind is not pure (withheld, or none with G > 0). Computed from
the split-v2 tables alone.

**Hypothesis (geometric).** Pure laws are isolated; laws with withheld state are mixtures and lie around them. An output
q is certified pure by a nearest-law observer only if the model's error t = TV(P_c, q) is below about μ_c / 2.

**Prediction M1.** On pure windows, for every model (12, the same as the monitor's), the monitor's m = 0 decision is
"pure" on at least 90 % of the windows with t < 0.4 μ_c, and on at most 10 % of the windows with t > 0.6 μ_c.
(Windows with t in [0.4 μ_c, 0.6 μ_c] are reported, not scored.)

**If M1 holds:** the one-sided limit is a computable property of the world (μ per class) together with the learner's
precision; v4 reports μ's distribution per cell as a pre-training quantity. **If it fails:** the asymmetry is not
explained by nearest-law geometry, and the error direction (follow-up 2) becomes the lead.

Per-window (P_c, q, truth) arrays are captured by re-running the monitor's capture, to
`~/.cache/yupi-scratch/kind-windows-2026-10-22/`.

## Addendum, written before any per-window data was read (same day)

Writing the analysis showed that M1's low half is close to a theorem. If t < μ_c/2, then every non-pure law is at
TV ≥ μ_c − t > t from q, while P_c is at t, so the nearest law cannot be non-pure. The one way the low half can fail
is a nearer *deterministic* law, which is excluded from μ_c and makes the monitor abstain. The low half is therefore a
check, not a test. **The informative half is the high one:** that beyond 0.6 μ_c the output has actually moved toward
the mixtures, rather than in some other direction that keeps it nearest P_c. That half bears on follow-up 2 (the
direction of the error). The declared prediction is unchanged. The result will report the two halves separately and
weigh only the high half as evidence.
