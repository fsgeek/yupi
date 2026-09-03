# Deep-truncation census — the C1 ladder at horizon 32: every adjacent pair is above δ at L = 8, in a world that is already half dead

**v0.1 — 2026-09-03.** Exploratory, enumerator side (window-process
recursion, `window-process-enumerator-v0.1.md`), ungated per window except
for a filter spot check (§4). Producers `scripts/r0_ladder_census.py` and
`scripts/c1_residual_ambiguity_census.py` under `YUPI_AGG=window`; raws
`r0-ladder-census-32-{4,8}-2-2026-09-03.json`,
`c1-residual-ambiguity-census-32-{4,8}-2-2026-09-03.json`; pins
`tests/test_deep_truncation.py`. Corrected kernel, canonical track, both
statutory ε, C1 programs unchanged. This is a **new law**, (32, L, 2), not
a re-measurement of any committed one; nothing frozen refers to it.

## 1. Why horizon 32

The C1′ pilot showed that every collapse measurement so far — D1 Part B,
the residual census, the exposure-side check, the witness-11 searches —
was made on windows that start at reset or drop at most about four
instructions. The question was whether the ladder collapses along L
because C1 synchronizes, or because those windows begin at the one moment
the whole state is known. Horizon 32 is the first horizon where most
windows are dropped into a running episode.

## 2. The caveat that goes first: C1 is dying by tick 24

State marginal from reset, ε = 1 (forward recursion, no windows):

| tick | E[# TERMINATED threads] | P(all four terminated) | reachable states |
|---|---|---|---|
| 14 | 0.04 | 0 | 342 |
| 24 | 0.99 | 0 | 456 |
| 32 | 2.28 | 0 | 317 |
| 40 | 3.76 | 0.79 | 185 |
| 48 | 3.98 | 0.99 | 185 |
| 64 | 4.00 | 1.00 | 185 |

So at horizon 32 the endpoint mixture (T ∈ {2, …, 32}) contains windows
from a live world (T ≲ 22) and from a world with two or three dead threads
(T ≳ 26). Dead threads produce no records and no ambiguity; they pull every
mean below the live-world value. **The numbers below understate what a
live world at this depth would show**; the direction of the bias is toward
the collapse verdict, not away from it. Horizon 64 is a fully dead world
after tick 40 and is not censused here.

## 3. The ladder, horizon 32 against horizon 14 (law-mass means, bits)

`kinds2 gap` = observation-gap part of the next-2-EVENT_KIND split
(rung-comparable). Fact queries are mean posterior entropies.

| law | ε | H(S) r0 / r1 / r2 / r3 / r4 | kinds2 gap r1 / r4 (r1 − r4) | Q1[L0] r1 / r2 / r3 | Q3[D0] r3 / r4 |
|---|---|---|---|---|---|
| (14, 4, 2) | 1 | 4.132 / 1.344 / 1.211 / 1.100 / 1.098 | 0.388 / 0.311 (0.076) | 0.247 / 0.224 / 0.115 | 0.066 / 0.065 |
| **(32, 4, 2)** | 1 | 4.854 / 2.012 / 1.894 / 1.661 / 1.614 | 0.629 / 0.490 (**0.139**) | 0.414 / 0.361 / 0.149 | 0.174 / **0.128** |
| (14, 8, 2) | 1 | 2.869 / 0.152 / 0.119 / 0.109 / 0.109 | 0.058 / 0.035 (0.023) | 0.016 / 0.013 / 0.003 | 0.006 / 0.005 |
| **(32, 8, 2)** | 1 | 3.086 / 0.484 / 0.449 / 0.346 / 0.332 | 0.173 / 0.108 (**0.064**) | 0.118 / 0.106 / 0.009 | 0.026 / **0.012** |
| (14, 8, 2) | ½ | 2.565 / 0.073 / 0.053 / 0.050 / 0.050 | 0.040 / 0.025 (0.015) | 0.005 / 0.004 / 0.000 | 0.003 / 0.002 |
| **(32, 8, 2)** | ½ | 2.350 / 0.186 / 0.170 / 0.125 / 0.115 | 0.074 / 0.046 (0.029) | 0.048 / 0.043 / 0.001 | 0.015 / 0.006 |

**Against the statutory collapse criterion** (Part II §6: adjacent rungs
collapse at L if the max query gap < δ = 0.01 bits), read on these
exploratory means:

| pair | (14, 8, 2) ε = 1 | (32, 8, 2) ε = 1 | (32, 8, 2) ε = ½ |
|---|---|---|---|
| r1 → r2 | Q1[L0] 0.003, kinds2 0.021 — statutory verdict L\* = 10 | Q1[L0] **0.012**, kinds2 0.019, H(S) 0.035 | Q1[L0] 0.005, kinds2 0.009 |
| r2 → r3 | Q1[L0] 0.010 — L\* = 8 (the marginal cell) | Q1[L0] **0.097**, H(S) 0.103 | Q1[L0] **0.042** |
| r3 → r4 | Q3[D0] 0.001 — collapsed at every C1 law | Q3[D0] **0.014**, H(S) 0.014 | Q3[D0] 0.009, H(S) 0.010 |

At horizon 32, ε = 1, L = 8, **every adjacent pair is above δ on a
statutory query**, including the lineage rung, which D1 Part B found
collapsed at every measured C1 law from reset. At ε = ½ the object and
lineage steps sit at the threshold (0.009, 0.010) and the related step is
well above it. At L = 4 the r1 → r4 exposure-side range nearly doubles
(0.076 → 0.139) and the lineage rung's Q3 gap goes from 0.001 to 0.046.

## 4. Residual census at horizon 32 (per-window accounting, v0.1.1 of the census note)

| law | ε | amb | reachable (split by r4) | unreachable | largest signatures |
|---|---|---|---|---|---|
| (14, 4, 2) | 1 | 0.670 | 0.350 | 0.320 (48 %) | pc+status+own+wq 0.123; pc+own 0.100; pc-only 0.055 (never split) |
| (32, 4, 2) | 1 | 0.857 | 0.594 | 0.262 (31 %) | pc+status+own+wq+dev_q 0.230 (r4 splits 1035/1086); +running 0.171; pc+status+wq+dev_q 0.098 (r4 329/453) |
| (14, 8, 2) | 1 | 0.165 | 0.057 | 0.108 (65 %) | pc-only 0.069 (never split); pc+own 0.050 |
| (32, 8, 2) | 1 | 0.541 | 0.361 | 0.180 (33 %) | pc+status+wq+dev_q 0.094 (r4 9355/10584); pc-only 0.070 (r4 11186/71437); pc+status+own+wq+dev_q 0.067 |

Mid-episode, the device queue is ambiguous on a large share of windows and
lineage is the rung that resolves it; from reset it was a sliver. The
unreachable share falls from about half to about a third at the same L,
and pc-only ambiguity — never split by any rung from reset — is split by
lineage in 16 % of its windows at horizon 32 (a dropped COMPUTE now sits
next to issue-order information the request id carries).

Filter spot check at (32, 4, 2), ε = 1: 75 windows per rung (the 15
largest supports plus 60 drawn with seed 20260903), all five rungs, through
`filter_window` against the recursion's aggregate — **375 of 375 exact**.
The recursion's gate covers horizons ≤ 14 bit for bit; this is the
evidence that it holds where the gate cannot reach.

## 5. What it means, stated with the caveat attached

1. **"The ladder collapses along L in C1" was a from-reset statement.**
   Measured mid-episode, in a world that is already losing threads, every
   rung is above δ at eight visible records, and the exposure-side range
   is two to three times the from-reset figure. D1 Part B's *measurement*
   at (14, ·, 2) stands exactly as adjudicated; its *generalization* — that
   C1 over-synchronizes — does not survive the first look at a deeper
   window. That is the pattern the house has met before: generalization,
   not measurement, is what reversals hit.
2. **The Part C question changes shape.** The intervention the evidence
   set was assembled to choose among — workload redesign so that rungs
   stay distinct — may be unnecessary for the ladder's dynamic range and
   necessary only for the episode's *length*: C1 dies at tick 24–40, so
   any horizon long enough for mid-episode windows to dominate needs
   programs that do not run out. That is the exhaustion reason for
   nonterminating workloads, which the pilot note separated from the
   collapse reason. The two reasons have now swapped weight.
3. **What is not yet known:** the live-world ladder (C1′ at horizon 64–96,
   where the pilot programs recur), which these numbers bound from below;
   whether the L = 12 ladder recovers (L = 12 at horizon 32 costs ~30 min
   and 24 GB per ε per rung and was not run); statutory status, which
   needs the ceilings producer switched to the recursion and every window
   gated.

## 6. Order of work from here (researcher's)

1. C1′ deep census at (64, {4, 8}, 2) and (96, {4, 8}, 2) — the live-world
   ladder; cost by the pricing table is minutes per law.
2. Switch `c1_query_ceilings.py` / `c1_q4_ceilings.py` to `YUPI_AGG=window`
   with the per-window filter gate intact; produce statutory (32, L ≤ 8, 2)
   and C1′ ceilings; D4 erratum (unit = pairs; RSS line for L = 12).
3. Then, and only then, decide whether any workload *redesign* is needed,
   with the PI. The recommendation on record changes accordingly: from
   "pilot recurring contention to restore range" to "extend the episode
   with nonterminating programs so the instrument measures a live world;
   the range may already be there."

## 7. Not claimed

Any statutory ceiling; any Part B re-adjudication; that the live-world
ladder is wider than the half-dead one (likely by the direction of the
bias, unmeasured); anything at L = 12 or beyond; anything about ε other
than the statutory pair.
