# Proposed second stamped decision (v0.3.1) — the four Part II thresholds (δ, δ_sync, δ_p, Δ_τ) and two §6 semantics they depend on

**Status: PROPOSAL v0.3.1, 2026-08-16 (eighth instance; commit time in git). Not binding. Ready
for confirmation or amendment.** Supersedes v0.3 (second truthsayer round, four corrections
below), v0.2, v0.1 (all retained). **v0.3.1 corrections (Codex/ChatGPT via Tony, all verified
against the artifacts):** (1) §G's T_ep direction was backwards — under uniform endpoints and
lossless U=0 windows, H_law = Pr(U>0)·H_trunc = (1 − L/T_ep)·H_trunc, so (a) and (b) *converge*
as T_ep grows at fixed L; the disagreement is largest at small T_ep, i.e. exactly at the
scale we can afford. (2) B1's normative formula hard-coded T_ep = 14, B = 2; generalized to
E[H | U > 0] = H_law / Pr(U > 0), with L = T_ep treated as the full-context control. (3) "Per-
endpoint entropies vary mildly … mixing U costs almost nothing" was a sentence wider than its
cells (the ±6% was one cell, ε=1 r1 L=2); the spread over truncated endpoints at fixed
(ε, rung, L) reaches 46% excluding the U=2 corner (ε=1 r3/r4, L=8) and 67% (ε=½ r4, L=6);
only the 7/8 horizon agreement is claimed. (4) Provenance: the sync-note blocks are v0.1.1
(0632368) and v0.1.2 (9deff20). The truthsayer's earlier "every horizon" overstatement and my
correction of it both remain in the trace, as they asked. Revised after the
truthsayer round (Codex/ChatGPT via Tony, morning of 2026-08-16): its verdict was *amend, not
confirm*, on five findings; four adopted as stated, one adopted with a correction (finding 2's
"every horizon moves" is five of eight cells). What survived audit unchanged: δ = 0.01;
Δ_τ = 0.01 (with wording); the δ_p axis over a scalar; the v0.2.4 record; byte-for-byte
reproduction of the δ and sync artifacts; independent direct enumeration of all 512 TV-surface
cells at (12,2,2) within float accumulation; suite 101 green.

The three §C sweeps: `c1-delta-sweep-v0.1.md` (14484c7 + appended amendment),
`c1-sync-sweep-v0.1.md` (ff82ce2/971f8bc; v0.1.1 block 0632368; v0.1.2 block 9deff20),
`c1-tv-sweep-v0.1.md` (5163346/7a18810; v0.1.1 wording in this commit).

Binds when Tony confirms it and the confirmation is stamped. All items are complete; B1 was
completed with the per-endpoint run (launched 07:23, landed 09:01 PDT 2026-08-16; law-mass
values byte-identical to the 2026-08-15 artifacts).

## A. δ = 0.01 bits (Part II §6, rung collapse) — unchanged from v0.1

Evidence: at L ∈ {2, 4} the eighteen per-cell maxima are bimodal with an empty band
(0.003728, 0.049943); 0.01 is inside it, one significant figure. On the L axis at T_ep = 14 the
object- and related-rung maxima decay ×0.3–0.45 per bucket through the band; under δ = 0.01
the collapse horizons are L* = 2 (r3→r4), 8 (r2→r3), 10 (r1→r2) at both ε, ±1 bucket per ×2–3
change in δ, one knife-edge cell ((14,8,2) ε=1 r2→r3 = 0.00999). What is frozen is the number
the curves are compared against, before any confirmatory curve.

## A′. §6 semantic amendment — Q4 enters the synchronization criterion by its gap part (NEW)

Part II §6 says the synchronization horizon is the smallest L at which "a rung's posterior
entropy on a query" falls below δ_sync. For Q4 that reads as the total entropy of the
forecast, which decomposes as irreducible + gap (Part I D1; measured 0.6926 / 0.6003 at
T_ep = 14 for the irreducible term, at every L and rung). Under the total, Q4 can never
synchronize below its irreducible term, so any δ_sync < 0.6 makes the criterion vacuous for
Q4. The sync sweep used the gap part; **the truthsayer correctly identified this as a
semantic amendment, not a threshold choice.** Proposed §6 text:

> *For queries with an irreducible term under exact state knowledge (Q4 statutory, and any
> predictive target), the synchronization criterion applies to the observation-induced
> component H_total − H_irr; the irreducible term is reported alongside and is not subject to
> δ_sync.*

Rejected alternative: apply δ_sync to the total (Q4 never synchronizes; the horizon for the
statutory bundle would be ∞ at every rung and L — a criterion that cannot fire is not a
criterion). Effect: none on any number already reported; the sync-sweep tables already used
the gap part and say so.

## B. δ_sync — two decisions, one pending

### B1. The measure the horizon is defined on — a §6 semantic decision (COMPLETE)

At fixed T_ep with uniform endpoints, windows with T ≤ L are lossless, so the law-mass mean
over L carries lossless fraction (L/2)/7 by construction. Four measures were computed
(`c1-sync-sweep-v0.1.md` v0.1.2 block; per-endpoint artifacts `…-2026-08-16-perT.json`):

| ε | rung | (a) law-mass (§6 as written) | (b) truncation-conditional | (c) per-endpoint T = T_ep | worst truncated endpoint |
|---|---|---|---|---|---|
| 1 | r1 | 10 | **12** | 12 | 12 |
| 1 | r2–r4 | 10 | **10** | 10 | 12 |
| ½ | r1 | 10 | **12** | 10 | 12 |
| ½ | r2–r4 | 8 | **10** | 10 | 10 |

(L*(all statutory) at δ_sync = 0.01, Q4 by gap part.) (b) and (c) agree in 7 of 8 cells; (a)
differs from (b) in 5 of 8, entirely from the lossless mass. The per-endpoint entropies at
fixed (ε, rung, L) are *not* uniform across truncated endpoints — spread (max/min − 1) up to
0.46 excluding the U=2 corner (ε=1 r3/r4, L=8; ε=½ up to 0.67 at L=6) and up to 1.85 including
it — so (b) genuinely averages over U; what is claimed is only that the coarse horizon
verdict agrees with the single-endpoint one in 7 of 8 cells.

**Proposed §6 text:** *"The synchronization horizon is evaluated on the mean posterior
entropy conditional on truncation, E[H | U > 0] = H_law / Pr(U > 0), where H_law is the
law-mass mean and Pr(U > 0) the law's mass on windows with U > 0; since full-context windows
are lossless at every rung this identity is exact. Under uniform endpoints at multiples of B,
Pr(U > 0) = 1 − L/T_ep (present law: 7/(7 − L/2) = 14/(14 − L)). L = T_ep has Pr(U > 0) = 0 and
is the full-context control, not a point on the synchronization curve; if no L < T_ep crosses
δ_sync the rung is reported as not synchronized within the truncated domain. The law-mass mean
(the learner's own law) and the per-endpoint curve at T = T_ep are reported alongside."*

Reasons for (b) over (a): a synchronization horizon characterizes what context does for an
observer who lost something; diluting it with windows that lost nothing scales the curve by
Pr(U > 0) = 1 − L/T_ep, which is small exactly at the small T_ep the budget allows (0.14 at
L = 12 here) — the two measures converge as T_ep grows, so (a) is most contaminated where we
measure. Over (c): (c) discards six of seven endpoints and rests on one T; its horizons agree
with (b) in 7 of 8 cells. The v0.2 provisional preference for (c) is withdrawn by the data. The
learner-faithful reading of (a) is preserved as a co-report — it is what a trained model at
context L actually faces, and both numbers belong in the M1 report.

Under (b), δ_sync = 0.01 gives L* = 12 for r1 and 10 for r2–r4 at both ε: the actor-only rung
needs one more bucket than every finer rung, at every ε — the cleanest rung structure any of
the four measures shows.

### B2. The number: δ_sync = 0.01 bits

Under (b) (proposed): L* = 12 (r1, both ε), 10 (r2–r4, both ε). Under (a): 10 (ε=1 all
rungs; ε=½ r1), 8 (ε=½ r2–r4). Under (c): 12 (ε=1 r1), 10 (all else). In every measure so far, 0.3 and 0.1 give
structureless horizons (4, 6 everywhere), 0.001 leans on the L = 12 cliff, and 0.01 sits in
the informative decade with ±1-bucket sensitivity to ×2–3 in δ_sync. Same number as δ by
convenience of units, not derivation.

## C. Δ_τ = 0.01 (Part II §5 deliverable 5, total variation) — wording amended

Evidence: at δ_p = 10⁻² the pair_prob surface over Δ_τ ∈ [10⁻³, 3·10⁻²] is exactly flat in
twelve L = 2 cells, within 4% in the other four, and within 30% at (14,4,2); a near-duplicate
shelf below 10⁻³; falls in every cell above 0.1. **This is a broad stability region with
reported sensitivity, not a flat band** (truthsayer wording, adopted). 0.01 is inside it, one
significant figure, 10× above the shelf.

## D. δ_p — freeze an axis, not a scalar; axis gains 10⁻⁴

Evidence: pair_prob is non-decreasing in δ_p in every cell with **no common stable plateau
on the sampled grid**; pair_prob(δ_p)/pair_prob(0) at Δ_τ = 10⁻² spans 1.36–85.5 at 10⁻²,
1.59–4954 at 3·10⁻², 3.3–61114 at 0.1; the largest single departure from exact equality,
65.9× at (12,2,2) ε=½ r2, occurs already at **δ_p = 10⁻⁴**. At full context pair_prob is
δ_p-invariant up to 0.1 in every cell.

Proposal: Part II §5 reports the divergent class and its prevalence (pair_prob and the
TV-weighted form) at **δ_p ∈ {0, 10⁻⁴, 10⁻³, 10⁻², 3·10⁻²}**, δ_p = 0 the exact anchor that
discharges the existence deliverable (non-empty in every windowed cell). If the statute must
name one δ_p for the class *definition* used in later exposure experiments, 0.01 is the least
bad scalar; this proposal recommends the axis.

## E. What this does not touch

m, W, 𝒯, continuation past T_ep (v0.2.4 §A/§B); request-id; D8; RESET/TIME_CLASS; ε grid;
corpus. No measured number changes.

## F. Confirmation form

*"I confirm docs/part2-threshold-freeze-proposal-v0.3.1.md as written: §6 is amended per A′
(Q4 enters by its gap part) and per B1 (synchronization horizon on the truncation-conditional
mean, law-mass and per-endpoint co-reported); δ = 0.01, δ_sync = 0.01, Δ_τ = 0.01 bind; δ_p
is reported as an axis {0, 10⁻⁴, 10⁻³, 10⁻², 3·10⁻²} with the exact anchor. Please enact it as
Part II v0.2.5 and stamp it."*

## G. Attack surface

1. Three 0.01s still look like one number chosen thrice; each has its own evidence, and the
   coincidence is not evidence.
2. The δ_p axis is a refusal to decide; the counter-argument stands (a threshold with no
   plateau is a convention and conventions should be visible).
3. B1 chooses (b) over the statute's (a): interface-faithfulness over learner-faithfulness
   as the *criterion*, with (a) co-reported. A reader who holds that the ceiling must be the
   learner's own should push back and invert the roles. The data show they disagree by one
   bucket in five of eight cells at T_ep = 14; since H_law = (1 − L/T_ep)·H_trunc the two
   converge as T_ep grows, so the disagreement is a small-T_ep effect — a defender of (a) may
   say it will wash out at scale; the reply is that M1's exact ceilings live at small T_ep by
   construction, so the criterion must be right there. *(v0.3 said the disagreement grows
   with T_ep; that was backwards — truthsayer round 2.)*
4. A′ removes Q4's irreducible term from δ_sync's reach by fiat; the alternative (some
   δ_sync ≥ 0.6) is not seriously arguable, but the amendment should be visible as one.
