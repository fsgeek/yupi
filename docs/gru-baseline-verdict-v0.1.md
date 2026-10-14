# A recurrent baseline: verdict v0.1 (2026-10-13)

> **Status: VERDICT against `docs/gru-baseline-prereg-v0.1.md`** (frozen at 886bab5 after two-family pre-stamp
> review, before any GRU was trained beyond CPU smoke tests). Scored by the frozen scorer
> `scripts/gru_baseline_score.py`. Raw: `docs/gru-baseline-score-2026-10-13.json`. Owning instance.

## 1. Gates: all pass

- **Wave:**
  - HEAD reproduced the 10-02 transformer r1 seed-1 step-1000 losses exactly;
  - two identical 200-step GRU runs on the GPU gave identical losses (1.091910719871521), so the GRU is
    deterministic on this setup.
- **Reference gate R:** the regression code reproduced the committed 10-02 fit (β_long 0.017472070944896154,
  t 6.790).
- **All eight models:**
  - arch gru, d 256, 2 layers, seed 1;
  - revision bf418e6, clean;
  - checkpoint step = census step = 117,195;
  - k = 7, the test split, and n equal to the transformer census of each cell;
  - census sha256 matches.
- Training ran 17:24–18:51 PDT under the lease, and the census and scoring ran 18:51–18:59.

## 2. Pre-registered readings

**Quality floor: no GRU model is informative.** All eight have a mean KIND shortfall *above* the count table's in
their cell:

| cell | GRU | transformer, seeds 1–3 | count table |
|---|---|---|---|
| r1 ε1 | 0.0449 | 0.0157, 0.0146, 0.0158 | 0.0422 |
| r2 ε1 | 0.0591 | 0.0157, 0.0172, 0.0238 | 0.0540 |
| r3 ε1 | 0.0698 | 0.0122, 0.0140, 0.0142 | 0.0635 |
| r4 ε1 | 0.0642 | 0.0141, 0.0130, 0.0127 | 0.0622 |
| r1 ε½ | 0.0562 | 0.0195, 0.0197, 0.0248 | 0.0386 |
| r2 ε½ | 0.0755 | 0.0324, 0.0226, 0.0329 | 0.0438 |
| r3 ε½ | 0.0704 | 0.0230, 0.0219, 0.0204 | 0.0470 |
| r4 ε½ | 0.0665 | 0.0290, 0.0191, 0.0210 | 0.0439 |

Per §3, each is **uninformative (under-trained)**: Y = 0 informative models, so **G1 has no reading**. Paper 1's
sentence is the pre-registered "otherwise": the counts, with no further reading.

**G2, descriptive:** the table above. The parameter-matched GRU, with the transformer's untuned recipe, is about
2–5 times worse than the transformer on KIND at position 7, and worse than the count table in every cell.

## 3. Post hoc, labelled and not read

- **Overall loss.** On r1 ε1 the GRU's validation loss over all positions is close to the transformer's (0.6161
  against 0.6112 nats per token). Its deficit is concentrated at the late, scored prediction: KIND about 3× and
  ACTOR about 3× (0.099 against about 0.031).
- **The association.** The GRU's frozen-model coefficients are positive, with large t in all eight cells (HC1
  12–23; class-clustered 11–19; coarse fixed effects 5.3–12), and its raw bins rise more steeply than the
  transformer's (top bin 0.10–0.15 against 0.03–0.06). The pre-registration does not read these, because the
  models are under the floor. Reading them now would be the post hoc move the floor was written to prevent.
- **Why the GRU is under-trained, or ill-suited:** not established. Candidates are the untuned learning rate, the
  fixed recurrent state compressing a 41-token history, and initialization.

## 4. For paper 1

§4d: "A parameter-matched GRU with the transformer's untuned recipe did worse than the count table in all eight
cells, so by our pre-registered floor it is uninformative about the within-cell association. A tuned recurrent
baseline remains owed." The comparison that stands is therefore still the transformer against the count table.
