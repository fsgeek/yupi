# Actor long-lag: verdict (v0.1, 2026-09-30)

> **Status: CONFIRMATORY result against `docs/actor-long-lag-design-prereg-v0.1.md`** (stamped in
> 0c8bde4 before any actor-target ι was computed or any actor analysis run). The exact side is in
> `docs/actor-iota-40-8-2-k7-2026-09-30.json`: all 60 rows gated, and a reviewer independently
> recomputed 400 sampled classes. The frozen analysis is `scripts/implicit_info_bintest_actor.py`
> (sha256 `09ba6f42…4c09`). A fidelity reviewer confirmed its diff from the frozen KIND script
> before any census was read. Results: `docs/actor-long-lag-results-2026-09-30.json`. Written by
> the owner (instance of 2026-09-28/29/30).

## Scorecard

| prediction | criterion | result |
|---|---|---|
| **A1** | β_long > 0 with t ≥ 3 in every one of 36 runs | **PASS, 36 / 36** (β_long 0.026–0.111, t 5.98–17.99) |
| **A2** | pooled per cell, t ≥ 5 | **PASS, 8 / 8** (t 12.3–29.0) |
| **A3** | pooled β_long > β_short | **PASS, 8 / 8** (β_long 0.031–0.061 vs β_short 0.003–0.012, ratio 4–12×) |
| A4 | A1 on the converged ladder | pending (censuses not yet run) |

The model scored is `full_plus_log2_class_mass`, the specification of the D1 verdict. The
model without the mass term also passes all three predictions.

## What it adds to the KIND result

1. **The law extends from *what happens next* to *who does it*.** A small transformer's excess on
   the next actor rises with the exact information about that actor, given the kind, that lies
   more than four records back. Class entropy and frequency are controlled.
2. **For identities, near history is not free.** On KIND, short-range information cost
   essentially nothing (pooled β_short −0.000 to +0.003). On the actor it costs something real:
   β_short 0.003–0.012, with t ≥ 5 in 6 of 8 cells. Distance still dominates (4–12×). The
   reading is that carrying *who* costs the learner at any lag, and much more across a long one.
   The one exception is r1 ε=½, where the short term disappears without the mass control.
3. **The actor's long-lag coefficient is larger than KIND's** (pooled 0.031–0.061 against
   0.029–0.041). There was no prediction, so this is an observation, but it fits the secondary
   D1 result that the cost lives where identities have to be carried.

## Caveats carried forward

- The pooled HC1 errors treat windows from different seeds as independent. There is no seed
  clustering, so A2's pooled t is somewhat anti-conservative. A1 (per run) does not depend on
  this.
- ι_{A|K} is a lower bound, because an actor seen only before the suffix reads as fresh.
- All runs use the 5-epoch recipe. A4 carries the converged test.
- Correlational, like D1. The relay intervention is the causal test, and it targets KIND.
