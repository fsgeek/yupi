# Fresh held-out laws for confirmatory threshold measurement — proposal

> **Status (2026-08-21, v0.2 at ~22:30 PDT): PROPOSAL, not enacted.** Part II
> v0.2.5 froze δ = δ_sync = Δ_τ = 0.01 and the δ_p axis and says confirmatory
> measurement "requires fresh held-out laws not used in the sweeps." This
> note fixes *which* laws before any ceiling is computed at them. The only
> quantities examined at the proposed laws were enumerator cost (§2) and the
> source of `WindowLaw` (§1.1); no curve at any law below has been computed.
>
> **v0.2 supersedes v0.1 (same evening, never committed).** v0.1 is kept in
> §7 verbatim. Changes: (i) the contamination of horizon-extension families
> is stated exactly instead of called "fresh"; (ii) predictions rewritten as
> mechanism-derived point predictions, the theorem dropped as a test, the
> δ-circular one replaced; (iii) the D4 B4 exceedance is no longer handled
> by footnote — T_ep = 16 is demoted until B4 is amended by its own process.
> The three criticisms that forced v0.2 are recorded in §7.

## 1. What "law" and "fresh" mean

A law is `WindowLaw(T_ep, L, B)` under `WorldConfig.c1(epsilon=ε)`, evaluated
by exact enumeration (`src/yupi/enumerator.py`). No sampling, no RNG, on the
confirmatory path; the Aug-20 seed-secrecy design is a corpus-generation
concern and is not invoked here.

The three §C sweeps (`docs/sweep-rerun-comparison-2026-08-21.md`) consumed
**T_ep ∈ {12, 14}, B = 2, ε ∈ {1, ½}** at every even L. Varying L is not
fresh.

### 1.1 Which axes are actually fresh (verified against `window.py`)

- **T_ep.** The enumeration tree at T_ep′ > T_ep is a prefix-extension of
  the tree at T_ep. Per-endpoint *conditional* posteriors (T known) at
  endpoints T ≤ 14 are bit-identical to rows already viewed in the
  `…-perT.json` raws of Aug 16. **But** `WindowLaw.compatible_endpoints`
  mixes every endpoint the law permits for an observed window length, so
  the learner-facing posterior over (U, S_T) — the one the §B1
  truncation-conditional mean and every law-mass quantity use — changes at
  *every* truncated window when an endpoint is added. A horizon-extension
  family therefore inherits its conditional rows and not its law-mass
  curves. Contamination is real and partial; it is stated, not hidden.
- **ε.** Leaves the tree untouched (path count is ε-independent, §2) and
  changes only the observation projection. Fresh in exactly the sense an
  observation-interface paper should care about, and inherits nothing.
- **B.** Changes the endpoint grid and thus the derived truncation prior.
  Inherits the conditional rows at shared endpoints; law-mass curves fresh.

## 2. Cost, measured before selection

`paths(WorldConfig.c1(ε), c1_programs(), T_ep)`:

| T_ep | paths | wall (ε=1 / ε=½) |
|---|---|---|
| 10 | 13,864 | 0.5 s |
| 12 | 69,210 | 1.9 / 2.4 s |
| 14 | 308,690 | 12.3 / 13.6 s |
| 16 | 1,315,454 | 42.9 / 66.9 s |

T_ep = 16 exceeds D4 **B4** (≤ 10⁶ paths per posterior check). The ceilings
scripts use one path-aggregation pass per (ε, rung, T), which is arguably
not B4's "validation path"; but B4's text is the frozen commitment and its
consequence clause reads "the world shrinks — not the ladder." This note
does not get to reinterpret that in a notes field. **Position:** T_ep = 16
is excluded from the confirmatory set until B4 is amended by an appended,
versioned erratum to `d4-budget-freeze-v0.1.md` that states the
aggregation-vs-validation distinction and re-measures memory at 1.3 M
Fraction-weighted paths (unmeasured tonight; the 30–45 min/run figure in
v0.1 was extrapolated, not measured).

## 3. Proposed held-out set (fixed list; stamp before computing)

**F2 — ε axis (primary).** (14, L ∈ {2,4,…,14}, 2) at **ε ∈ {¼, ¾}**. Same
tree as the consumed T_ep = 14 laws (cost known: ~7 min per ceiling run);
no sweep saw either ε; inherits nothing. Two values bracket the consumed ½
from both sides so that a monotone-in-ε artefact would show. D9's ε rule is
untouched; these are probes, not candidate operating points.

**F3 — bucket axis (secondary).** (12, L ∈ {2,4,…,12}, **1**), ε ∈ {1, ½}.
Cheap (69 k paths). Fresh law-mass curves, inherited conditional rows at
even endpoints (stated contamination: 6 of 12 endpoints).

**F1 — horizon axis (deferred, conditional on a B4 amendment).** (16, L
even, 2), ε ∈ {1, ½}. If admitted, its contamination is: conditional rows
at 7 of 8 endpoints inherited; all law-mass curves fresh. It is the only
family in which L\* = 12/10 can move by a full step, so it is the most
*informative* family and the one the budget currently forbids.

Not proposed: T_ep = 10 (no L < 10 for r2–r4 to cross), T_ep = 18 (~6 M
paths), odd T_ep at B = 2 (statute: T_ep must be a multiple of B).

## 4. Pre-stated predictions

These are written by an instance that has seen the sweeps; pre-statement
does not launder that. What makes a prediction a test here is that it is
**derived from a stated mechanism** and would be false if the mechanism is,
not that it is written down first. Each names its failure condition.

- **P1 (ε-invariance of the ladder, F2).** Mechanism: ε governs tracing
  coverage of the projection, so it scales per-record information but does
  not create or destroy the structural reason r2–r4 coincide (the lineage
  rung carries ~0 bits because I5 makes request-id matching structurally
  empty). Prediction: at both ε ∈ {¼, ¾}, L\*(r2) = L\*(r3) = L\*(r4) under
  δ_sync = 0.01, and L\*(r1) exceeds it by ≥ 2. **Fails if** any of r2–r4
  separate by a step, or r1 joins them.
- **P2 (ε-monotone synchronization, F2).** Mechanism: lower ε removes
  records, so truncation-conditional entropy is pointwise ≥ at ε = ¼ than
  at ε = ½ and ≤ at ε = ¾, for every rung and L. Prediction: L\*(¼) ≥
  L\*(½) ≥ L\*(¾) rungwise. **Fails if** any inversion. (This is an
  ordering the sweeps could not test: they had two ε values only.)
- **P3 (lineage rung bound, F2 + F3).** Replaces v0.1's δ-circular P3.
  Prediction: max over (law, ε, L) of the r3→r4 gap ≤ **0.003 bits** — the
  measured ~0.002 plus a 50 % margin, *not* the 0.01 threshold. **Fails if**
  exceeded anywhere.
- **P4 (prior-change mechanism, F3).** Mechanism: B = 1 doubles the
  endpoint count and halves each endpoint's prior; the truncation-conditional
  mean is H_law / Pr(U > 0) with Pr(U > 0) = (T_ep − L)/T_ep unchanged in
  form. Prediction: L\* at every rung is unchanged from the (12, ·, 2)
  sweep values at both ε. **Fails if** any rung's L\* moves.
- **P5 (divergent class, F2).** pair_prob(δ_p = 0, Δ_τ = 0.01) > 0 at
  (14,2,2) and (14,4,2) for both new ε, and the δ_p = 10⁻⁴ jump exceeds the
  δ_p = 0 anchor by ≥ 10×. **Fails if** either.

Dropped from v0.1: the injectivity-theorem "prediction" (it cannot fail and
belongs among controls, where it already lives as the L = T_ep row).

A failed prediction is a confirmatory failure of the v0.2.5 thresholds'
generalization and is reported as such — not re-tuned.

## 5. Rule

1. The list in §3 is frozen by the commit that stamps this note. Any
   ceiling computed at a listed law before that stamp voids the law.
2. Reuse the existing scripts with the law on the command line; artifacts
   `…-heldout-2026-08-DD.json`; append, never overwrite.
3. F1 runs only after a B4 erratum is appended and stamped; if no erratum,
   F1 is dropped and the note says so.
4. After F2–F3 (and F1 if admitted): `held-out-confirmation-v0.1.md` reports
   P1–P5 verdicts and receives the truthsayer pass the sweeps received.

## 6. Decision rights

This note changes no world, no threshold, no freeze. What is the PI's is
whether the §3 list is the confirmatory set and whether B4 is opened. What
is the instance's is everything else in it, including having been wrong
in v0.1.

## 7. v0.1 record and the criticisms that forced v0.2

**v0.1 list (superseded):** F1 = (16, L even, 2) ε ∈ {1, ½} *primary*;
F2 = (14, ·, 2) ε = ¼; F3 = (12, ·, 1) ε = 1. Predictions: sync ordering
with ranges {12,14}/{10,12}; collapse ordering; r3→r4 ≤ 0.01; pair_prob
≥ 10×; injectivity at L = T_ep. B4 exceedance "recorded as a finding."

**Criticism 1 — "fresh" was asserted on the wrong axis.** Horizon extension
inherits viewed conditional rows. Verification against `window.py` showed
the criticism was itself too strong (law-mass curves are fresh because the
endpoint mixture changes); v0.2 states the exact inheritance.

**Criticism 2 — predictions tailored to seen sweeps; one a theorem, one
circular in δ.** v0.2 derives each from a mechanism with a named failure
condition, tightens the lineage bound to 0.003, drops the theorem.

**Criticism 3 — a frozen budget overridden in a notes field.** v0.2 excludes
T_ep = 16 pending an appended B4 erratum, and flags the unmeasured runtime.

---

## v0.3 (2026-08-21 22:45 PDT) — two tiers, selection by seed, B4 erratum proposed

*Appended; v0.2 above stands as written. What changed and why.*

**Why v0.2's framing of option B was wrong.** The discussion record: v0.2
(and the decision-space walk that followed it) presented a cross-world
confirmation as "robust but more work, paper 2." Two of the reasons were
real and one was not. Real: (i) a different world can have different
synchronization horizons, so a cross-world failure cannot distinguish
"threshold does not generalize" from "world differs" — within-world
confirmation is therefore *necessary* for the C1 exit claims; (ii) the cut
says hold the frozen world. Not real: the cut is about papers, not
enumerations, and the instance sized the options to what one session
could close. An instance-horizon bias is a planning defect in a project
that carries work across instances by design. Recorded so the next reader
can see it.

**The confirmatory set, v0.3.**

- **Tier 1 — within-world (required for M1 exit).**
  - F2: (14, L ∈ {2,…,14} even, 2), ε ∈ {¼, ¾}.
  - F3′: (14, L ∈ {1,3,…,13} odd, **1**), ε ∈ {1, ½} — L values the
    sweeps could not express; replaces v0.2's (12, ·, 1). Inherits
    conditional rows at even endpoints only.
  - F1: (16, L even, 2), ε ∈ {1, ½} — **conditional on D4 erratum E1**
    (appended tonight to `d4-budget-freeze-v0.1.md`, proposed). Runs
    first as a kernel-validation pass regardless: ticks 15–16 of the
    corrected kernel are unobserved since the deadlock fix (d69fa87).
  - Predictions P1–P5 of v0.2 apply; P4 restated for F3′: L\* at every
    rung unchanged from the (14, ·, 2) sweep values.
- **Tier 2 — cross-world (threshold-as-principle; not required for M1
  exit, reported separately).** One C1′: same machine shape (4T/2CPU/2L/1D),
  a different program set, support measured against D4 before any
  ceiling, the 13 C1 witnesses re-run. P1–P5 restated for C1′ *before*
  enumeration. A Tier-2 failure is reported as "δ/δ_sync/Δ_τ do not
  transfer," never as an M1 failure; a Tier-2 pass is what would make
  0.01 bits a threshold rather than a C1 constant.
- **Selection (E).** The ε pair, the odd-L set, and the C1′ program draw
  are fixed by a committed seed over a declared grid (grid and seed
  recorded in the enacting commit), so the instance's hand is off the
  choice. Over a grid this small it is largely ceremony; it answers
  criticism 2 fully where v0.2 answered it partly.

**Cost.** Tier 1: ~60 ceiling runs, ~7 min each at T_ep = 14, ~45 min at
16; about two hours on 64 cores. Tier 2: roughly one instance-day for the
world plus Tier-1-sized compute. The writing is the cost.

**Decision rights (unchanged).** The PI decides the tiers, the E1
enactment, and whether Tier 2 is opened now or after Tier 1 reports.
Nothing below runs before the stamp.
