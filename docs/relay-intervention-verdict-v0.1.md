# The relay intervention: verdict v0.1 (2026-10-02)

> **Status: CONFIRMATORY verdict** against `docs/relay-intervention-prereg-v0.1.md` and addendum
> v0.1.1, both stamped before any r1ʀ model finished training. The scorer is the instance of
> 2026-10-02, which did not write the predictions. The raws were committed **unscored** at e3d1f06. The
> workflow was the one used for `docs/converged-ladder-verdict-v0.1.md`: one runner, then a Claude
> reviewer and a Codex (GPT) reviewer, each recomputing independently (the Claude reviewer with its own
> join code). Gates: every `relay_paired.py` gate passed in both arms, including the window-by-window
> check r1 records = drop_relay(r1ʀ records). Checkpoint provenance was 12/12 for the arm recipes
> (addendum §3).

## Scorecard (primary arm, 5 epochs)

| | prediction | observed | result |
|---|---|---|---|
| **R1** | slope of Δexcess on Δι > 0, t ≥ 3, in [0.0165, 0.066] | slope 0.01627, se 0.0026, t 6.24 | **FAIL**, below the floor by 0.0002 (0.09 se). Positive and strong, just outside the band |
| **R2** | exact-zero set: mean Δexcess within ±2 se of the intercept | set mean 0.00076; intercept 0.00458 (t 10.2); difference 13 set-se | **FAIL** |
| **R3** | relocated learner obeys the frozen law: β_long > 0, t ≥ 3, each seed | t 6.28, 4.65, 5.89 | **PASS 3/3** |
| **R4** | where the relay adds long-lag load (Δι < −0.05): mean − intercept < 0, quadrature t ≤ −3 | +0.0067, quadrature t **+3.42** (set-se t +3.51) | **FAIL, wrong sign**: r1ʀ models do *better* there |

Relay field's own excess, reported separately as the prereg requires: 9.4e-5 (se 1.8e-6) per window.
R4 is scored on the quadrature t (addendum §2). `relay_paired.py`'s help text calls that t
"not scored", and the addendum governs. Both t's fail.

## Secondary arm (15 epochs, reported without thresholds)

Slope **+0.0005 (t 0.21)**, intercept +0.0037 (t 9.1). On the zero set, the mean minus the
intercept is −0.0036 (11.6 se). For R4, the mean minus the intercept is +0.0044 (t +2.6, same wrong
sign). R3 β_long: 0.013, 0.008, 0.011 (t 4.6, 3.4, 4.3). Relay-field excess 1.7e-4.

## What the deciles show (addendum §4)

Mean Δexcess (r1 excess − r1ʀ excess; positive means the relay helped) by decile of Δι
(`docs/scoring-2026-10-02/relay-deciles-2026-10-02.json`). That script is post-hoc and imports the
frozen functions unchanged; both reviewers reproduced every bin independently:

| decile | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |
|---|---|---|---|---|---|---|---|---|---|---|
| mean Δι | −0.157 | −0.020 | −0.003 | +0.000 | +0.005 | +0.023 | +0.059 | +0.132 | +0.270 | +0.620 |
| 5 ep | **+0.0109** | +0.0033 | +0.0019 | +0.0007 | +0.0039 | +0.0023 | +0.0047 | +0.0082 | +0.0102 | **+0.0153** |
| 15 ep | **+0.0078** | +0.0033 | +0.0006 | −0.0001 | +0.0023 | +0.0038 | +0.0026 | +0.0066 | +0.0072 | +0.0033 |

At 5 epochs the effect is **V-shaped in Δι**. It is near zero where the relay leaves long-lag
information unchanged. It rises where the relay moves information closer (the prediction), and it
also rises where the relay pushes information *further back* (against the prediction). The
learner's gain tracks **the size of the change |Δι|, not its sign**. The positive slope in R1 comes
from the right arm of the V. The large intercept in R2 is what a straight line through a V produces.
At 15 epochs the left arm stays (dec0 is the largest bin). The right arm flattens and collapses at
the top decile, which is why the slope is 0.

## Reading

The prereg's reading: "R1 and R4 together are the causal claim: the same histories, carrying the
same information, cost the learner more when that information sits further back, and less when it
sits closer, in both directions." **That claim fails.** The relay helps in both directions. At the
converged budget it does not scale with Δι at all.

What survives:
- Within every cell, the learner's excess correlates with ι_long, for KIND and for actor identity,
  and at the converged budget (C1, A4, R3).
- Adding an explicit relay field improves the learner by a few millibits per window. The ceiling is
  identical class by class, so this is learnability, not information. The improvement is
  concentrated where the relay changes the long-lag structure in **either** direction.

What is withdrawn, by the prereg's own terms: **the causal distance reading of D1.** Nothing here
shows that long-lag information costs the learner *because* it is far back. ι_long may index
something else the learner finds hard. One candidate: classes whose next kind depends on
entity-binding history, which the relay makes explicit whichever way it moves ι_4. The transformer
sees all 7 records at k = 7, so "beyond lag 4" is a property of the exact Markov decomposition, not
of the learner's access. This candidate is untested. It is named so that the next design can test it,
not adopted.

Caveats: three seeds per arm; HC1 errors on windows, not clustered by class; one interface (r1, ε = 1);
the band floor in R1 was set from a rounded 0.033 (unrounded 0.03266 gives a floor of 0.01633, and the
slope still fails).

## Consequence for paper 1

The lesson the 2026-10-02 handoff proposed for skeleton v0.2 §4, "shortfall tracks distance; richer
interfaces help partly by moving information closer", **is not licensed.** Its first half survives
only as a within-cell correlation (C1, A4). Its second half fails here and in C3. Skeleton v0.2 must
be written from these two verdicts, not from the handoff's anticipated lesson.
