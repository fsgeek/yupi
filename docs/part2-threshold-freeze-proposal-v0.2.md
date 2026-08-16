# Proposed second stamped decision (v0.2) — the four Part II thresholds (δ, δ_sync, δ_p, Δ_τ) and two §6 semantics they depend on

**Status: PROPOSAL v0.2, 2026-08-16 (eighth instance; commit time in git). Not binding.
Supersedes v0.1 (retained: `part2-threshold-freeze-proposal-v0.1.md`).** Revised after the
truthsayer round (Codex/ChatGPT via Tony, morning of 2026-08-16): its verdict was *amend, not
confirm*, on five findings; four adopted as stated, one adopted with a correction (finding 2's
"every horizon moves" is five of eight cells). What survived audit unchanged: δ = 0.01;
Δ_τ = 0.01 (with wording); the δ_p axis over a scalar; the v0.2.4 record; byte-for-byte
reproduction of the δ and sync artifacts; independent direct enumeration of all 512 TV-surface
cells at (12,2,2) within float accumulation; suite 101 green.

The three §C sweeps: `c1-delta-sweep-v0.1.md` (14484c7 + appended amendment),
`c1-sync-sweep-v0.1.md` (ff82ce2/971f8bc; v0.1.1 block in this commit),
`c1-tv-sweep-v0.1.md` (5163346/7a18810; v0.1.1 wording in this commit).

Binds when Tony confirms it and the confirmation is stamped. **Item B1 (the synchronization
measure) is not ready to confirm until the per-endpoint run lands** — launched 07:23 PDT
2026-08-16, ~1.6 h; its results will be appended to `c1-sync-sweep-v0.1.md` and B1 completed
in a v0.3 of this document. Everything else can be read now.

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

### B1. The measure the horizon is defined on (PENDING per-endpoint data)

At fixed T_ep with uniform endpoints, windows with T ≤ L are lossless, so the law-mass mean
over L carries lossless fraction (L/2)/7 by construction; the truncation-conditional mean is
exactly ×7/(7 − L/2). At δ_sync = 0.01 the horizons differ between the two in **five of eight**
cells (law-mass 10 → truncation-conditional 12 at ε=1 r1 and ε=½ r1; 8 → 10 at ε=½ r2–r4;
ε=1 r2–r4 stay at 10). Three candidate definitions:

- (a) **law-mass mean** — §6 as written; the learner's own generative process (Part II §2(a)
  derived-prior principle: the ceiling is a ceiling for a learner only under its own law), so
  it is what a trained model at context L actually faces; but its L axis mixes "more context"
  with "more windows that see RESET".
- (b) **truncation-conditional mean** — removes the lossless mass; still mixes U at a given L.
- (c) **per-endpoint at T = T_ep** — the observer's posterior entropy on windows ending at
  the episode's last endpoint, as a function of L: a clean context curve at a fixed point in
  the episode, no endpoint-prior artifact. Data pending (per-endpoint output added to both
  ceilings scripts on 2026-08-16; law-mass outputs verified unchanged on (12,2,2)).

Provisional recommendation, to be confirmed or reversed by the data: **(c) as the frozen
criterion, with (a) co-reported** — because a synchronization horizon is meant to
characterize the interface, and (a)'s dependence on the endpoint prior would make the
horizon move with T_ep at fixed L for reasons unrelated to the interface. If the per-endpoint
curve at T = T_ep is not materially different from (b), (b) may be preferred as the simpler
statement. This is a §6 semantic decision and is written as one.

### B2. The number: δ_sync = 0.01 bits

Under (a): L* = 10 (ε=1 all rungs; ε=½ r1), 8 (ε=½ r2–r4). Under (b): 12 (ε=1 r1; ε=½ r1), 10
(ε=1 r2–r4; ε=½ r2–r4). Under (c): pending. In every measure so far, 0.3 and 0.1 give
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

## F. Confirmation form (after B1 is completed in v0.3)

*"I confirm docs/part2-threshold-freeze-proposal-v0.3.md as written: §6 is amended per A′
(Q4 by gap part) and per B1 (synchronization measure = …); δ = 0.01, δ_sync = 0.01, Δ_τ = 0.01
bind; δ_p is reported as an axis {0, 10⁻⁴, 10⁻³, 10⁻², 3·10⁻²} with the exact anchor. Please
enact it as Part II v0.2.5 and stamp it."*

## G. Attack surface

1. Three 0.01s still look like one number chosen thrice; each has its own evidence, and the
   coincidence is not evidence.
2. The δ_p axis is a refusal to decide; the counter-argument stands (a threshold with no
   plateau is a convention and conventions should be visible).
3. B1's provisional preference for (c) over the statute's (a) trades learner-faithfulness
   for interface-faithfulness; a reader who holds that the ceiling must be the learner's own
   should push back and prefer (a) with (c) co-reported. The per-endpoint data will show
   whether the two disagree materially at T_ep = 14.
4. A′ removes Q4's irreducible term from δ_sync's reach by fiat; the alternative (some
   δ_sync ≥ 0.6) is not seriously arguable, but the amendment should be visible as one.
