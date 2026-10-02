# D1 held-out test: verdict (v0.1, 2026-09-29)

> **2026-10-02 correction, read first.** The result below stands as a within-cell correlation. It also holds at
> the converged budget (`docs/converged-ladder-verdict-v0.1.md`, C1 24/24). Any *distance* (causal) reading of it
> is withdrawn: the relay intervention found the learner's gain V-shaped in Δι, so moving information further
> back also helped, and at 15 epochs the slope is 0 (`docs/relay-intervention-verdict-v0.1.md`). The cross-cell
> ordering (C3) failed at ε = ½. The text below is unchanged.

> **Status: CONFIRMATORY result against `docs/d1-long-lag-prereg-v0.1.md`** (stamped in commit
> fbe0178, before any held-out census existed). The analysis script's sha256 was checked equal
> to the pre-registered value (`c73fab6b…ad32dd7acfc`) immediately before the run. Raws:
> `docs/d1-long-lag-heldout-primary-2026-09-29.json` (21 primary runs) and
> `docs/d1-long-lag-heldout-secondary-r0-2026-09-29.json`. Censuses:
> `docs/learner-window-census-*-2026-09-29.json` (24). Written by the instance of 2026-09-28/29.

## Scorecard

| prediction | criterion | result |
|---|---|---|
| **P1** | β_long > 0 with t ≥ 3 in every primary run | **PASS, 21 / 21** (β_long 0.023–0.083, t 8.7–19.7) |
| **P2** | pooled per cell, β_long > 0 with t ≥ 5 | **PASS, 5 / 5** (t 17.7–30.6) |
| **P3** | pooled β_long > β_short per cell | **PASS, 5 / 5** (β_short −0.000 … +0.003) |
| **P4** | pooled β_long in [0.01, 0.06] | **PASS, 5 / 5** (0.029–0.041) |

Pooled per cell (the model with frequency control: terms 1, ι_kind,4, ι_kind,1 − ι_kind,4,
H_kind, log₂ class mass; OLS, HC1):

| cell | seeds | β_long (t) | β_short (t) |
|---|---|---|---|
| r1 ε=½ | 3 | 0.0400 (21.9) | +0.0000 (0.0) |
| r2 ε=1 (seeds 4–6) | 3 | 0.0291 (17.7) | +0.0008 (1.5) |
| r2 ε=½ | 6 | 0.0411 (30.0) | −0.0000 (0.0) |
| r3 ε=½ | 3 | 0.0312 (18.3) | +0.0027 (4.7) |
| r4 ε=½ | 6 | 0.0395 (30.6) | +0.0029 (6.8) |

**Secondary (not scored).** r0 ε=½, kind-only traces with no entities: pooled β_long 0.0036
(t 4.6; per seed t 2.5–2.9), **about a tenth** of the content rungs'.

## What is established

Within every interface cell tested, on held-out models, a small transformer's excess over the
exact ceiling on the next event's kind rises with the exact amount of information about that
kind lying more than four records back. The rise is about **0.03–0.04 bits of excess per bit of
long-lag information**. Information of the same kind within the last four records costs
essentially nothing. The class's entropy and its frequency do not account for the effect.

Read with the secondary result: the cost is large where the long-lag information has to travel
with entity identities (r1–r4) and small where it does not (r0).

## What is not established

- **Causation.** Long-lag information is a property of the prefix class. A covariate of it that
  was not controlled (for example, token distance to the relevant record, or attention-pattern
  difficulty) could carry the effect. The load-separating control (skeleton readiness item 6)
  and a causal intervention are what would separate these.
- **Budget.** Every model here is the 5-epoch recipe, which §22–§23 show is under-converged.
  Whether the coefficient shrinks at the converged budget is the next stamped prediction
  (readiness item 5).
- **Target.** KIND only. The entity fields are the larger part of the excess (§8). Extending ι
  to them needs the naming-aware target of design §2.
- **Functional form.** Linear in ι. The deciles in the raws show the shape, and that is the
  right figure for the paper.
- **The cell-level ladder.** This result is within cells. It suggests, but does not show, that
  the ladder's r2 penalty is the long-lag information r2 withholds locally (§1 of the first-results
  note). That would need a cross-cell model with cell effects, which is a separate analysis.

## Consequence for paper 1

D1 has its first confirmed answer, and §4 of the skeleton has its lesson: **a small
transformer's shortfall tracks how far back the needed information lies, and a richer interface
helps the learner partly by moving information closer.** Both halves are exact-side quantities
only this instrument can compute. The paper-1 skeleton moves to v0.2 once the converged-budget
test is designed.
