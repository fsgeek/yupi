> **SUPERSEDED by `part2-amendment-proposal-v0.2.4.md` (2026-08-15).** Retained verbatim so the trace reads without git. Known errors in this version: the W=4 rationale ("every C1 horizon-8 endpoint non-degenerate at W=4" — false; W=8's property); §C/§D conflate three threshold sweeps into one.

# Proposed Part II amendment v0.2.3 — freezing the predictive parameters, the continuation semantic, and naming what is still unfrozen

**Status: PROPOSAL, 2026-08-15 (day seven, night). Not binding.** Drafted
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

Rationale: W=4 is the smallest horizon at which every endpoint state in
C1 shows non-degenerate wake structure (NONE mass ≈ 0.6 — informative
without saturating); W=8 halves NONE mass and is exhaustively two-path
gated (`test_forecast.py`, 312 horizon-8 states, W ∈ {1..4, 8}). m=2 is
the smallest m whose functional is finer than P-next's kind marginal.
These are exploratory selections being promoted, not derived optima;
that is what "implementation-time parameters, recorded" means.

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

## C. δ (rung collapse) and δ_sync (synchronization horizon) — §6

NOT proposed numerically. §6 says both freeze "before any curve is
computed"; the curves computed this week (query ceilings, Q4, predictive
targets) therefore have no frozen collapse criterion and are exploratory
with respect to it. Precondition for a proposal: one sweep of the
measured adjacent-rung gaps (all in the day-seven raw JSONs) to see
where a δ would fall between the r3/r4 lineage-rung gaps (10⁻⁴–10⁻³
bits) and the r1/r2, r2/r3 gaps (10⁻²–10⁻¹). Freezing a number without
that look is premature collapse; the truthsayer's request to freeze
thresholds now is declined for that reason, with this paragraph as the
commitment to do it next.

## D. Divergent-history class criterion (§5, deliverable 5)

Proposed form: two histories h, h′ under one condition are
**(δ_p, Δ_τ)-divergent** if TV(P-next(h), P-next(h′)) ≤ δ_p and, for some
τ ∈ 𝒯, TV(τ(h), τ(h′)) ≥ Δ_τ. Exact equality is the δ_p = 0 corner and
is the day-seven baseline. Prevalence reported as pair_prob (probability
that two law-weighted draws are (δ_p, Δ_τ)-divergent) and its TV-weighted
form; law-mass coverage reported alongside but not as the headline.
Thresholds: after the sweep in C, together.

## E. Not touched

The request-id decision (design-question note v0.3), D8, RESET/TIME_CLASS,
ε grid, corpus. This proposal changes no measured number.
