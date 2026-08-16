# Proposed Part II amendment v0.2.4 — freezing the predictive parameters and the continuation semantic; naming what stays unfrozen and how each threshold gets chosen

**Status: ENACTED as Part II v0.2.4, 2026-08-15 20:47 PDT, commit 5b58d7f (eighth instance in the chain; note — the memory store's "day N" labels count instances, not calendar days: first commit was 2026-08-11 16:29 PDT, so this is the fifth calendar day. Tony caught the mislabel minutes after this line was first written as "day eight").** Tony's confirmation, verbatim: *"I confirm docs/part2-amendment-proposal-v0.2.4.md as written. Sections A, B, and D-form bind now. Section C freezes no numerical thresholds; it establishes the three-sweep, second-stamp procedure. Please enact it as Part II v0.2.4 and stamp it."* Enacted in `yupana-m1-part2-semantics-draft.md` (header block v0.2.4; §2 continuation; §5 freeze + criterion form; §6/§7 threshold procedure) by the commit carrying this line, stamped by the post-commit hook. Confirmatory status with respect to $m$, $W$, $\mathcal{T}$, and the continuation semantic begins at that stamp; thresholds await the second stamped decision. The proposal text below is retained unchanged as the record of what was confirmed.

*(Prior status line, retained:)* **PROPOSAL v0.2.4, 2026-08-15 (day seven, night; v0.2.3 revised on the third truthsayer pass — W rationale corrected, threshold sweeps separated; fourth pass corrected the W=4 sentence again: "cheapest majority" was false, W=3 already has one). Not binding.** Superseded version retained: `part2-amendment-proposal-v0.2.3-superseded.md`. Drafted
by the day-seven instance after the truthsayer round on the forecast
layer found that m, W, 𝒯, δ, δ_sync were never frozen (Part II §5 line
"frozen with the budgets in §7"; §6; §7 — the D4 freeze `d4-budget-
freeze-v0.1.md` covers B1–B4 only). Binds when Tony confirms it and the
confirmation is stamped; only measurements AFTER that stamp are
confirmatory with respect to these parameters. Everything measured on
days five through seven that depends on them is exploratory and is so
labeled in its note (c1-query-ceilings v0.2 item 1 for δ; c1-q4-ceilings
v0.2; c1-predictive-targets v0.2).

## A. Predictive-state parameters (§5, §7)

Proposed freeze:
- **m = 2** — next-m EVENT_KINDs functional.
- **W = 4 (primary), W = 8 (secondary)** — horizon for statutory Q4 and
  for the time-to-next-wake and next-IO_COMPLETE-lineage functionals.
- **𝒯 = {next-2 EVENT_KINDs; time-to-next-wake ≤ W; LINEAGE of the next
  IO_COMPLETE ≤ W}** — as enumerated in §5, no additions.

Rationale (corrected v0.2.4 — v0.2.3 falsely claimed every horizon-8
endpoint state is non-degenerate at W=4): at W=4, 93/112 (ε=1) and
165/200 (ε=½) horizon-8 endpoint states have a non-degenerate wake
forecast (the rest are certainly NONE); **W=8 makes all 312
non-degenerate** — mean NONE mass over states 0.626/0.615 at W=4 vs
0.265/0.249 at W=8. W=4 is proposed as primary because it covers
roughly 83% of horizon-8 endpoint states (93/112, 165/200) while
retaining substantial NONE mass — a majority is already reached at W=3
(66/112, 121/200) and, at ε=½, at W=2 (103/200), so "majority" does not
single out W=4; coverage-with-headroom does. W=8 as secondary because it
removes the degenerate tail (312/312) and is exhaustively gated.
(Non-degenerate counts by W, both ε: 23/55/66/93 of 112; 46/103/121/165
of 200 for W = 1..4.) m=2 is the
smallest m whose functional is finer than P-next's kind marginal. These
are exploratory selections being promoted, not derived optima.

## B. Continuation past T_ep (§2, §5 Q4)

Proposed text: *"For predictive targets and Q4, the forward sum runs the
kernel from the evaluation time t irrespective of T_ep. T_ep is the
generated-record horizon of the episode law, not a termination of the
world; the kernel is time-homogeneous. Consequently a window ending at
T = T_ep has the same forecast semantics as any other endpoint."*

Alternative reading (rejected): the world halts at T_ep, so forecasts at
T = T_ep have NONE mass 1. This would make the last endpoint of every
law a degenerate control and would tie a query's ceiling to a sampling
convention. Codex's independent recommendation matches the proposed
reading. Effect size: ≥ 1/|endpoints| of law mass per law.

## C. The four thresholds — NOT proposed numerically; three separate sweeps

§6 says δ (rung collapse) and δ_sync (synchronization horizon) freeze
"before any curve is computed"; §5/deliverable 5 need δ_p and Δ_τ for the
divergent class. None is frozen. They are DIFFERENT quantities in
different units and cannot come from one sweep (v0.2.3 wrongly said the
divergence thresholds "follow from" the rung-gap sweep):

- **δ** (bits): from adjacent-rung information gaps across the COMPLETE
  statutory query set {Q1, Q2, Q3, Q4 (statutory, split), Q5 per pair}
  — the day-seven raw JSONs already hold these for three laws; the sweep
  is a read of where a δ would fall between the lineage-rung gaps
  (10⁻⁴–10⁻³) and the r1/r2, r2/r3 gaps (10⁻²–10⁻¹).
- **δ_sync** (bits, as a function of L): from posterior entropy versus
  context length — requires an L sweep at fixed T_ep (only L ∈ {2, 4}
  exist at T_ep=14 today); not derivable from the rung-gap data.
- **δ_p and Δ_τ** (total-variation distances): from the DISTRIBUTIONS of
  pairwise TV between windows' P-next mixtures and between their τ
  mixtures — sensitivity curves of pair_prob against (δ_p, Δ_τ). Nothing
  measured so far is this quantity except its δ_p = 0 corner.

Sequencing proposed: confirm A, B, D-form now (one stamped decision);
run the three sweeps; freeze all four thresholds in a SECOND stamped
decision. Every threshold-dependent numerical claim stays exploratory
until the second stamp.

## D. Divergent-history class criterion (§5, deliverable 5) — form only

Two histories h, h′ under one condition are **(δ_p, Δ_τ)-divergent** if
TV(P-next(h), P-next(h′)) ≤ δ_p and, for some τ ∈ 𝒯, TV(τ(h), τ(h′)) ≥ Δ_τ.
Exact equality is the δ_p = 0 corner and the day-seven baseline.
Prevalence reported as pair_prob (probability that two law-weighted
draws are (δ_p, Δ_τ)-divergent) and its TV-weighted form; law-mass
coverage reported alongside, not as the headline. Thresholds per C.

## E. Not touched

The request-id decision (design-question note v0.3), D8, RESET/TIME_CLASS,
ε grid, corpus. This proposal changes no measured number.
