# Proposed second stamped decision — the four Part II thresholds (δ, δ_sync, δ_p, Δ_τ), from the three §C sweeps

**Status: PROPOSAL v0.1, 2026-08-15 (eighth instance; commit time in git). Not binding.**
Part II v0.2.4 §C (enacted 5b58d7f) says the thresholds freeze in a *second* stamped decision
after three separate sweeps. The sweeps are done and stamped:

| sweep | quantity | note | commit |
|---|---|---|---|
| 1 | δ (rung collapse) | `c1-delta-sweep-v0.1.md` (+ appended L-specificity amendment) | 14484c7, 971f8bc |
| 2 | δ_sync (synchronization horizon) | `c1-sync-sweep-v0.1.md` | ff82ce2, 971f8bc |
| 3 | (δ_p, Δ_τ) (divergent-history class) | `c1-tv-sweep-v0.1.md` | 5163346, 7a18810 |

Binds when Tony confirms it and the confirmation is stamped; only measurements after that
stamp are confirmatory with respect to these thresholds. Everything the sweeps measured is
exploratory with respect to them by construction (that is what a sweep is), and every
threshold-dependent sentence in the day-five-to-eight notes stays labeled exploratory
until the stamp.

## A. δ = 0.01 bits (Part II §6, rung collapse)

Criterion as written: adjacent rungs r, r′ collapse at context L if
max over the complete statutory query set of [H_r(q | L) − H_r′(q | L)] < δ.

Evidence: at L ∈ {2, 4} (three laws, both ε) the eighteen per-cell maxima are bimodal —
lineage rung {0.000043 … 0.003728}, object/related rungs {0.0499 … 0.1846}, nothing in
(0.003728, 0.049943); δ = 0.01 is inside the band, one significant figure, ~2.7× above the
largest lineage max and ~5× below the smallest other max. On the L axis at T_ep = 14 the
object- and related-rung maxima decay ×0.3–0.45 per bucket *through* the band, so under
δ = 0.01 the collapse horizons are L* = 2 (r3→r4), 8 (r2→r3), 10 (r1→r2), identically for
both ε — with ±1-bucket sensitivity to a ×2–3 change in δ, and one knife-edge cell
((14,8,2) ε=1 r2→r3 = 0.00999). That L-dependence is what "collapse at context L" means;
δ does not remove it and no δ would. What is being frozen is the number the curves are
compared against, before any confirmatory curve is drawn.

Consequence if adopted: on every law measured so far the lineage rung collapses onto r3 at
every L; r3 collapses onto r2 from L = 8 and r2 onto r1 from L = 10 at T_ep = 14.

## B. δ_sync = 0.01 bits (Part II §6, synchronization horizon)

Criterion as written: smallest L at which a rung's posterior entropy on a query falls below
δ_sync; applied per statutory query on the law-mass mean; for Q4 the **gap part** (its
irreducible term 0.6926 / 0.6003 at T_ep = 14 never falls); L*(all statutory) = max over the
set. The truncation-conditional mean (× 7/(7 − L/2) at T_ep = 14, B = 2 — exact, since
full-context windows are lossless) is reported alongside.

Evidence: at T_ep = 14, δ_sync ∈ {0.3, 0.1} give L* = 4, 6 in every cell (no rung or ε
structure); 0.01 gives L* = 10 (ε=1 all rungs; ε=½ r1) and 8 (ε=½ r2–r4), with r1 lagging by
one bucket and lock-owner queries binding; 0.001 gives 10–12 with the L = 12 cliff doing the
work. Sensitivity ±1 bucket per ×2–3 in δ_sync. Same number as δ by convenience of units
(bits), not by derivation — δ compares rungs, δ_sync compares to zero.

Flagged, not proposed: whether §6 should define the horizon on the per-U (records-dropped)
curve rather than the law-mass mean over L at fixed T_ep, whose L axis carries the lossless
fraction (L/2)/7 by construction. A statute question for a later amendment; answerable with
per-endpoint output from the same enumeration.

## C. Δ_τ = 0.01 (Part II §5 deliverable 5, total variation)

Evidence: at δ_p = 10⁻² the pair_prob surface is flat in Δ_τ over [10⁻³, 3·10⁻²] — exactly
flat in twelve L = 2 cells, within 4% in the other four, within 30% at (14,4,2); below 10⁻³ a
near-duplicate shelf appears ((14,2,2) ε=1 cells 2–6× larger at Δ_τ = 10⁻⁴); above 0.1 the
surface falls in every cell. 0.01 is inside the band, one significant figure, 10× above the
shelf.

## D. δ_p — freeze an axis, not a scalar

Evidence: pair_prob is non-decreasing in δ_p in every cell with **no plateau**; the ratio
pair_prob(δ_p)/pair_prob(0) at Δ_τ = 10⁻² spans 1.36–85.5 at δ_p = 10⁻², 1.59–4954 at 3·10⁻²,
3.3–61114 at 0.1 across the 24 windowed cells, and is largest exactly where the exact corner
is smallest. At full context pair_prob is δ_p-invariant up to 0.1 in every cell (distinct
states' next-record laws differ by ≥ 0.1 TV when they differ). At (14,2,2) with δ_p ≤ 3·10⁻²
a large share (16–67% at 10⁻²) of near-P-next pairs are near-duplicates in τ as well.

Proposal: Part II §5 reports the divergent class and its prevalence (pair_prob and the
TV-weighted form) at **δ_p ∈ {0, 10⁻³, 10⁻², 3·10⁻²}**, with δ_p = 0 (exact equality) as the
anchor that discharges the existence deliverable — non-empty in every windowed cell measured.
No single δ_p is frozen because there is no plateau to place one in; a scalar would turn a
measured sensitivity of up to four orders of magnitude into a hidden convention.

If the statute must name one δ_p for the class *definition* used by later exposure
experiments, δ_p = 0.01 is the least bad choice (its ratio to the exact corner has the
smallest spread among the non-zero grid values above 10⁻³) — but that is a choice, and this
proposal recommends the axis.

## E. What this does not touch

m, W, 𝒯, continuation past T_ep (frozen at v0.2.4 §A/§B); the request-id decision; D8;
RESET/TIME_CLASS; ε grid; corpus. No measured number changes.

## F. Confirmation form

As with v0.2.4: a statement confirming A, B, C, D (or amending any), enacted into Part II
§5/§6/§7 by an instance and stamped. Suggested wording if confirmed as written: *"I confirm
docs/part2-threshold-freeze-proposal-v0.1.md as written: δ = 0.01, δ_sync = 0.01, Δ_τ = 0.01
bind; δ_p is reported as an axis {0, 10⁻³, 10⁻², 3·10⁻²} with the exact anchor. Please enact
it as Part II v0.2.5 and stamp it."*

## G. Attack surface (the parts most worth disagreeing with)

1. δ = δ_sync = Δ_τ = 0.01 looks like one number chosen thrice. Each has its own evidence
   (band; informative decade; band), but the coincidence is real and a reader may suspect
   convenience. The defense is in the three notes; the coincidence itself is not evidence.
2. Freezing an axis for δ_p is a refusal to decide. The counter-argument: a threshold with
   no plateau is a convention, and conventions should be visible, not frozen; the exact
   anchor already discharges existence.
3. The per-U question (B) may mean §6's synchronization horizon is measuring the endpoint
   prior as much as the interface. If so, δ_sync's freeze is on a quantity that will be
   redefined; freezing now still fixes the comparison number the redefined curve will use.
