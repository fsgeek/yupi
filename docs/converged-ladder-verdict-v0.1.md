# The converged-budget ladder: verdict v0.1 (2026-10-02)

> **2026-10-04, read with care: "per bit".** The confirmatory slopes below (β_long, bits of excess per bit of ι)
> come from a linear model with no step term. Binned fits (exploratory; `relay-free-difficulty-results-v0.1.md`,
> corrections) show the learner's cost is roughly a **plateau**: about +0.015 to +0.024 bits for any ι4 in (0, 0.4],
> rising only above that. The sign and significance of the confirmatory results stand. Reading β_long as a
> marginal price per bit, or comparing its magnitude across budgets, is not supported.

> **Status: CONFIRMATORY verdict** against `docs/converged-ladder-prereg-v0.1.md` (05e3543, stamped
> before any converged model was evaluated). It also scores **A4** of
> `docs/actor-long-lag-design-prereg-v0.1.md`. The scorer is the instance of 2026-10-02, which did not
> write these predictions. The raws were committed **unscored** at e3d1f06 (OTS-stamped) before any
> analysis ran on them. A workflow did the scoring (`docs/scoring-2026-10-02/`): one runner ran the frozen
> commands, then two reviewers independently recomputed every line from the raws and tried to refute
> it, one Claude and one Codex (GPT). The reviewers raised nine objections. All were accepted, and none
> changed a number. One (C2) changed a result's label, from PASS to AMBIGUOUS. The full scorecard and
> objections are in `docs/scoring-2026-10-02/workflow-result-wf_5cab0a84-e8c.json`.

## Scorecard

| | prediction | result |
|---|---|---|
| **C1** | β_long > 0, t ≥ 3, every r1–r4 run (24) | **PASS 24/24** (β_long 0.011–0.029, t 5.3–11.3) |
| **C2** band | pooled β_long per cell in [0.01, 0.05] | **PASS 8/8** (0.013–0.025, t 10.8–16.4) |
| **C2** clause | "convergence shrinks the long-lag cost no more than the overall excess shrinks, and does not remove it" | **"does not remove it": PASS 8/8. "No more than": FAIL 8/8** |
| **C3** ε = ½ | KIND excess r2 > r1 > r3 | **FAIL**. Observed order r2 > r3 > r1. No pair is seed-resolved |
| **C3** ε = 1 | r2 > r3 | **PASS, seed-resolved** (0.0189 vs 0.0134) |
| **C4** | r0 lowest KIND excess at each ε | **PASS**, seed-resolved at both ε (with and without r1 ε = 1) |
| **A4** | actor A1 on every converged r1–r4 run (24) | **PASS 24/24** (t 3.07–10.1; two runs near the line: r3 ε=1 s3 t 3.07, r4 ε=½ s3 t 3.17) |

Model row: `full_plus_log2_class_mass` throughout, as frozen. The frozen-script hashes were checked
before and after scoring: bintest `c73fab6b…acfc`, actor bintest `09ba6f42…4c09`. Every per-window
file matched its recorded sha256 (39/39), and so did every ι cache. Evaluation and census agree to
4.7e-16 at k = 7. The evaluations ran on CPU; the 5-epoch ones ran on CUDA.

## C2: why the label is split, not a pass

The stamped C2 has two parts. One is a band. The other is a sentence that begins "The prediction is
that…". Read as a test, the sentence fails in every cell. On matched seeds 1–3, the 15-epoch pooled
β_long is 0.39–0.69 of its 5-epoch value. Over the same budgets, the KIND excess shrinks to
0.51–0.76 and the total structural excess to 0.56–0.78. The cell closest to passing is r3 ε = ½:
β ratio 0.689 against KIND 0.737, which is within an approximate, unclustered se of the ratio. The
wording allows no noise, and the other cells separate by 2–4.7 such se.

I score it as two lines and do not pick the reading that passes. **The band was too wide to test the
sentence it was meant to operationalize.** It would have accepted a fourfold fall in β. The finding
that counts: **convergence reduces the long-lag cost proportionally more than it reduces the excess,
and it does not remove it.** Converged learners still pay per bit of distant information, but about
half as much as at 5 epochs.

## C3: the cross-cell ordering does not follow ι at ε = ½

KIND excess at ε = ½ (cell means over seeds, between-seed sd):

| r0 | r1 | r2 | r3 | r4 |
|---|---|---|---|---|
| 0.0049 (0.0004) | 0.0213 (0.0030) | 0.0293 (0.0058) | 0.0218 (0.0013) | 0.0230 (0.0053) |

r1 and r3 are inverted by 0.00046, about a sixth of r1's between-seed sd. The excess cannot tell them
apart, while the exact quantity puts them 0.033 bits apart in ι_kind,4. r2 sits above both on means
but resolves from neither. At ε = 1, r2 > r3 holds with every seed separated (r1 is excluded by the
prereg). In short, a cross-cell ordering predicted from exact quantities alone **holds where the ι
gap is large relative to seed spread, and is not supported where it is not.** As the prereg says
for this case ("If C3 fails while C1 holds…"), paper 1 reports the law **within cells only**. Not
scored: the evaluator's exact kind_kl_bits flips the r1/r3 pair by 0.0003, which confirms that the
pair is in the noise.

The C3/C4 numbers come from `scripts/converged_ladder_c3c4.py`, written after the raws existed. It
was not stamped. It implements the stamped estimator (the plain mean of `by_field.kind` over the
k = 7 test per-window rows), and both reviewers reproduced it independently to 5 decimals.

## What this establishes and what it does not

- **Within-cell long-lag cost survives convergence**, for both KIND (C1) and actor identity (A4).
  It is smaller, and it shrank more than the excess did (C2 clause).
- **The between-cell claim does not survive.** Paper 1 must not say that ι ranks interfaces by learner
  shortfall.
- **This is still correlational.** The causal test is the relay intervention, scored the same day in
  `docs/relay-intervention-verdict-v0.1.md`. That verdict bears directly on how the within-cell
  correlation can be read. Read it before citing C1 as evidence for a distance mechanism.
- Caveats carried over: pooled t is not seed-clustered; three seeds per cell; r4 basins (r4 ε = ½
  seeds 0.029 / 0.019 / 0.021).
