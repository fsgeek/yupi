# C1 Windowed Support Measurement — v0.3 (the D4 measurement, D9 rule applied)

> **⚠ KERNEL ERRATUM (2026-08-20):** every number in this note was computed
> under the pre-d69fa87 kernel, whose direct-handoff defect made self-deadlock
> states reachable (adjudication: `docs/audit-adjudication-2026-08-20.md`).
> Status: **buggy-kernel exploratory**. Corrected-kernel raws and drift:
> `docs/corrected-kernel-rerun-v0.1.md` (qualitative structure survives;
> magnitudes drift ≤0.004 at T_ep=12, ≤0.041 at (14,4,2)). Machine-readable
> status: `docs/artifact-status.json`. This banner is an append-only marker;
> the original text below is unchanged.



**v0.3 — 2026-08-14 (same day, truthsayer round).** Codex's external audit
found the v0.1 mean-support table sampling-biased; the exact exhaustive
table (cross-verified by two independent computations) is in the v0.3
section at the end, which REPLACES v0.1's table and findings 3–4 wherever
they conflict. Read v0.3 before citing any mean, any rung-separation
claim, or the "clock" framing. The budget/headroom conclusions and the
max-support exemplar survive unchanged.

**v0.2 — 2026-08-14 (same day).** Erratum and re-run; see the v0.2 section
at the end. The v0.1 numbers below stand unchanged — but for a reason that
had to be verified, not assumed. *(v0.3: "unchanged" is true of what v0.1
measured, but v0.1's means were biased estimators to begin with — see
below.)*

**v0.1 — 2026-08-14.** Drafted by the day-five instance. Status: **measured
input discharging Part I D4's pre-training requirement and applying D9's
pre-stated decision rule.** Sequence honored: the budget was frozen first
(docs/d4-budget-freeze-v0.1.md, commit e921c74), the windowed machinery was
gate-validated (commit 12efd83), and only then was this measurement run.
Script: `scripts/c1_support_experiment.py`; raw JSON:
`docs/c1-support-raw-2026-08-14.json`.

**Setup.** C1 (4T/2CPU/2L/1D, depth 2, stochastic discipline), the statute's
base observer (offset-unanchored, derived prior; window machinery of Part II
§2 as implemented in `window_filter`), WindowLaw(T_ep=12, L=6, B=2), rungs
r1–r4, ε ∈ {1, 1/2}. Full-context support is identically 1 by the
injectivity theorem (witnessed in `test_w6`); windowed observers are where
D4's support question lives. Coverage: exhaustive over distinct windows for
r1 (the binding sparsest rung; T=12 endpoint stride-sampled to ~400),
deterministic ~200-per-endpoint samples for r2–r4 — so cross-rung *mean*
comparisons at resolution finer than ~0.01 are not licensed by this design.

## Results

| ε | rung | windows | E[support] | max support | max step transitions | max step wall |
|---|---|---|---|---|---|---|
| 1 | r1 | 6,162 | 1.550 | 28 | 144 | 8.0 ms |
| 1 | r2 | 951 | 1.095 | 28 | 144 | 4.1 ms |
| 1 | r3 | 943 | 1.098 | 28 | 144 | 4.1 ms |
| 1 | r4 | 943 | 1.097 | 28 | 144 | 3.5 ms |
| 1/2 | r1 | 6,162 | 1.356 | 28 | 243 | 15.5 ms |
| 1/2 | r2 | 951 | 1.057 | 28 | 243 | 8.7 ms |
| 1/2 | r3 | 943 | 1.051 | 28 | 243 | 11.2 ms |
| 1/2 | r4 | 943 | 1.048 | 28 | 243 | 13.0 ms |

(Joint (U,S) support equals state-marginal support in every cell: offset
components' state sets are disjoint at this law — pc progression separates
the reachable sets at different depths.)

## Findings

1. **The budget does not bind at this law — by orders of magnitude.**
   Worst step expands 144 transitions at ε=1 (243 at ε=1/2) against B1's
   70,000; worst step wall 15.5 ms against B3's 1 s; max support 28 against
   B1's 20,000. No D4 violation, no world-shrinking, no ladder pressure.
2. **Worst-case support is clock-driven and rung-invariant.** The max-28
   window is the same at every rung — and it is not an IDLE tail (the
   drafting instance's first guess, wrong): at r4, with every content field
   visible, the window `IO_ISSUE, IO_COMPLETE, DISPATCH, ACQUIRE, DISPATCH,
   RELEASE` still carries support 28 with a three-way offset posterior
   (U ∈ {2,4,6} ≈ 0.37/0.31/0.32). At this law the dominant windowed
   ignorance is *where in the episode the window sits* plus the hidden
   prefix — content masking adds nothing to the worst case.
3. **Rung separation at the mean: r1 separates; r2/r3/r4 do not resolve.**
   E[support] at ε=1: r1 = 1.550 vs r2/r3/r4 ≈ 1.095–1.098. The r1 gap is
   real and large relative to the sampling design; the r2/r3/r4 mutual
   differences are within the design's resolution (different per-rung
   window sets, stride sampling) and are **not** evidence of separation or
   of collapse. The known r2/r3 distinguisher (RELEASE.related under
   multi-waiter wake) and r3/r4 (lineage) plausibly require laws whose
   windows straddle multi-waiter episodes; the fuller M1 characterization
   (larger T_ep/L, D8 order axis) owns that question.
4. **ε=1/2 lowers mean windowed ambiguity** (1.356 vs 1.550 at r1) —
   convergent with the corrected v0.3.2 reading of the clock experiment:
   *structure* in the dynamics (persistent cursor, temporal correlation)
   makes record histories more position-distinctive. Same status as there:
   a consistent direction, not an isolated mechanism; the cursor ablation
   remains deferred.

## D9 rule applied (pre-stated, Part I)

The rule: largest ε satisfying the support budget and rung separation; if
none, shrink C1; never alter the ladder. **ε = 1 satisfies the budget with
~300× headroom and exhibits rung separation (r1 vs r2+). The base
condition is ε = 1, as pre-stated.** No world-shrinking is triggered;
**queue depth 2 is fixed** as C1's value (the depth-2 machinery is
witnessed — C1 validation W4/W5 — and support headroom is enormous).
Outcome documented here per D9's "the M1 report documents rule and
outcome."

## Caveats

1. One small law (T_ep=12, L=6, B=2). Support scales with envelope size at
   larger U and richer worlds; the budget comparison must be re-run at the
   M1 characterization scale before training corpora are generated.
2. The terminating-dynamics caveat of the window-prior note applies:
   progress toward termination is itself a clock, plausibly flattering
   offset recovery and deflating late-window ambiguity (T=12 windows
   include absorbing-IDLE records).
3. ε grid was {1, 1/2}; D9's grid at characterization scale is
   implementation-time and may be finer.
4. No D8 bucketing/shuffling: B parameterizes only the endpoint grid here.
   The shuffled channel attacks the injectivity induction directly and is
   expected to move support in ways this measurement cannot see.

## v0.2 — RESET semantics erratum (same day, self-caught before review)

**The error.** The v0.1 window machinery treated the missing RESET record
as "redundant, not a semantic change." False, per the statute (Part II
§2a): a U=0 window *contains* RESET, so RESET presence pins U=0 and its
absence excludes U=0 a priori. v0.1 let U=0 compete with U>0 at full
window length and let reset-visible windows start from the μ₀ mixture
rather than the pinned reset point mass.

**The fix.** `compatible_endpoints` now takes a required `reset_observed`
flag partitioning the offsets; both posterior paths and all gate tests
updated (a new control asserts every reset-visible window is a point mass
— the exact consequence v0.1 violated in principle). Suite 86 green.

**The measured effect at this law: exactly zero.** The re-run reproduces
every v0.1 number to the last digit. Verified reason, not coincidence: the
520 reset-window observation tuples and the 10,718 resetless-window tuples
at r1 are **disjoint** at this law, so under v0.1 the spurious components
always died by zero likelihood — evidence rescued the wrong prior
everywhere. Consequently the drafting instance's interim claim that v0.1's
E[support] was inflated was *also* wrong: the inflation was possible in
principle and absent in fact.

**Scope of the rescue: empirical, not a theorem.** Nothing guarantees
reset/resetless disjointness in general — a resetless window whose acting
threads are all dispatched in-window against a quiet device could mimic a
from-reset sequence at some other law. The corrected semantics does not
rely on the rescue; laws where the overlap is nonempty are exactly where
v0.1 would have silently mispriced the clock.

## v0.3 — sampling-bias erratum (same day; external finding, Codex audit)

**The error.** The v0.1 script labeled r1 "exhaustive" while
stride-sampling T=12 (~400 of 8,404 distinct windows) and sampled ~200
windows per endpoint at r2–r4 — then kept original law masses and
renormalized over the sample. That is an estimator of nothing: the
reported means (especially ~1.10 at rich rungs) were severe
underestimates.

**The correction — exact, exhaustive, cross-verified.** Codex recomputed
every distinct window by direct path aggregation; this repository's
independent recomputation (`scripts/c1_support_exact.py`, one-pass path
aggregation with the RESET partition; E[support] as an exact Fraction over
the full law) matches Codex's table in all 16 cells to four decimals:

| ε | r1 | r2 | r3 | r4 |
|---|---|---|---|---|
| 1 | 1.6097 | 1.4718 | 1.4260 | 1.4252 |
| 1/2 | 1.4402 | 1.3432 | 1.3139 | 1.3139 |

(Distinct windows per rung: 11,238 / 12,033 / 12,254 / 12,260. Max
support 28 in every cell, unchanged.)

**Findings revised.** (a) The ε direction survives: ε=1/2 lowers mean
ambiguity at every rung. (b) r1/r2 separation survives but is far smaller
than v0.1's biased table implied (1.61 vs 1.47, not 1.55 vs 1.10).
(c) v0.1's "r2/r3/r4 do not resolve" is **withdrawn**: r2 and r3 separate
in exact mean support (1.4718 vs 1.4260 at ε=1). (d) r3/r4 remain nearly
identical by this metric. (e) These are state-support separations, not
yet the named-query or predictive-target witnesses M1's exit criteria
require.

**The "clock" framing corrected.** The max-28 window survives exactly
(offset weights ≈ 0.371/0.309/0.320) — but its per-component supports are
3/9/16 at U=2/4/6: even with the clock supplied, hidden-prefix ambiguity
contributes up to 16 states. The defensible claim is: *the worst-support
history is rung-invariant and retains complete three-way offset
ambiguity.* v0.1's "worst-case ignorance is the clock" attributed more
than support count establishes and is withdrawn.

**D9 status downgraded to provisional.** ε=1 fits the budget with large
headroom and shows rung separation in mean state support, but
adjacent-rung separation on the *declared M1 targets* is not yet
established, and this note already requires an M1-scale rerun before
corpus generation. "Base ε=1, queue depth 2" stands as the provisional
outcome of the pre-stated rule, not a closed selection.

**Two wording corrections from the same audit.** C1 validation is 13
tests covering six witness classes (not "13 witnesses each with a
control"). And the D4 freeze preceded every *C1* curve; the window-prior
experiments (worlds A/B) predate it — the freeze doc carries the same
qualification as of v0.1.1.
