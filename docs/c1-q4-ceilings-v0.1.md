# C1 Statutory Q4 — the first ceiling that is not zero at full context (v0.1)

**v0.2 — 2026-08-15 (same night, truthsayer round on the forecast layer).**
Codex verified every (12,2,2), W=4 value by independent explicit
continuation, the conservation identities, and the W/L flip; and
refuted three things this note said. Corrections (v0.1 text preserved
below the rule):

1. **Finding 2's ranking is withdrawn — it was false.** "Q4's gap term is
   larger than every state-predicate query's total ceiling except
   Q4proxy[L0] and Q1[L0]" — at (12,2,2), ε=1, r4 the Q4 gap is 0.2648
   bits while Q2[T0] = 0.6161, Q5joint = 0.5170, Q2[T3] = 0.5007 (and
   others) exceed it; and it compared a gap term to totals. The
   defensible statement: **Q4 carries a substantial observation-induced
   gap of ~0.11–0.40 bits under the measured windowed laws.** No ranking.
2. **Finding 5's heading "W matters to the irreducible term, not to the
   ordering" is rewritten**: W demonstrably changes which content rung
   dominates the gap term (owner at W=4/L=2, object at W=8 — the flip
   the P5 paragraph itself reports). W raises the irreducible term AND
   changes the ordering.
3. **W=8 gate**: caveat 1 is discharged — the committed test now checks
   forward sum against explicit W=8 enumeration exhaustively over every
   horizon-8 endpoint state, both ε (312 states, ~6 s, zero mismatches),
   in addition to W ≤ 4. Codex had independently checked six
   structurally selected states at W=8; the exhaustive check subsumes it.
4. **Decision (i) (continuation past T_ep)** — Codex recommends the same
   reading (§2's T_ep is the generated-record horizon, not the world's
   end) but it is an unstated semantic decision affecting a third or
   more of endpoint conditions. It is now written up as an explicit
   proposed Part II amendment (`docs/part2-amendment-proposal-v0.2.4.md`)
   and these numbers are **exploratory until the amendment is confirmed
   and stamped**. Likewise W itself: Part II §5 says W is frozen with the
   §7 budgets, and the D4 freeze does not include it — the "W = 4
   primary, W = 8 secondary" choice here is an exploratory selection, not
   a freeze.

---

**v0.1 — 2026-08-15 (day seven, evening).** Drafted by the day-seven
instance. Status: **measured note; statutory Q4 (Part II §5, item 9)
implemented and measured** — the last of Q1–Q5 to exist. Code:
`src/yupi/forecast.py` (absorbing recursive forward sum, memoized) ⟂
`src/yupi/forecast_paths.py` (explicit continuation enumeration); gate in
`tests/test_forecast.py` — every endpoint state of every C1 path to
horizon 8, both ε, W ∈ {1..4}, Fraction-exact agreement. Script:
`scripts/c1_q4_ceilings.py T_ep L B W`. Predictions below written before
the first run.

## Definition (statute) and two recorded decisions

Q4 = the thread DIRECTLY woken by the first wake-causing transition in
(t, t+W]: a COMPLETION wakes its issuer (the transition's actor); a
RELEASE-with-waiter wakes the handed-off head (`related`). Secondary
wakes excluded. Value ∈ threads ∪ {NONE_WITHIN_W}. Decisions: (i) the
forward sum runs the kernel past T_ep (the law governs record delivery,
not world termination; the kernel is time-homogeneous); (ii) a completion
whose issuer terminates still counts as waking the issuer.

Per window w with belief b_w: **total** H(Q4 | w) = H(Σ_s b_w(s) f(s));
**irreducible** = Σ_s b_w(s) H(f(s)); **gap** = total − irreducible =
I(S_T; Q4 | w). Part I D1: both terms reported. Law-mass-weighted means.

## Predictions (pre-stated; W = 4 primary, W = 8 secondary)

- **P1 (theorem, sharpened):** at the full-context law (12,12,2), the
  mean total is **strictly positive**, identical across rungs, and equal
  to the irreducible term (gap = 0 exactly). The first non-zero
  full-context ceiling in the project.
- **P2 (conservation):** at every law, the mean irreducible term is
  **identical across all four rungs** (it is Σ_s P(s) H(f(s)), an
  expectation over the endpoint state marginal, untouched by any
  interface). The ladder acts on the gap term only. If this fails, the
  script is wrong, not the world.
- **P3 (ε):** the irreducible term is larger at ε=1 than at ε=½ (ε=1 is
  uniform-among-candidates scheduling — more dynamics randomness — per
  `_epsilon_policy`).
- **P4:** the gap term's r3→r4 movement is ≤ 0.001 bits at every law.
- **P5 (following the proxy, falsifiable):** for the gap term, the
  r1→r2 drop ≥ the r2→r3 drop at (12,2,2) — Q4proxy was object-rung
  dominated; I predict statutory Q4 is too. (Stated with the day's
  record on such predictions in mind.)

---

## Results (raw: `c1-q4-ceilings-<law>-W<W>-raw-2026-08-15.json`)

Law-mass-weighted means in bits. **irr** = irreducible term, **gap** =
I(S_T; Q4 | w). n_states = distinct endpoint states forecast per ε.

| law | W | ε | rung | total | irr | gap | none mass |
|---|---|---|---|---|---|---|---|
| (12,12,2) | 4 | 1 | r1 | 0.6676 | 0.6676 | 0.0000 | 0.6358 |
| (12,12,2) | 4 | 1 | r2 | 0.6676 | 0.6676 | 0.0000 | 0.6358 |
| (12,12,2) | 4 | 1 | r3 | 0.6676 | 0.6676 | 0.0000 | 0.6358 |
| (12,12,2) | 4 | 1 | r4 | 0.6676 | 0.6676 | 0.0000 | 0.6358 |
| (12,12,2) | 4 | 1/2 | r1 | 0.5870 | 0.5870 | 0.0000 | 0.6379 |
| (12,12,2) | 4 | 1/2 | r2 | 0.5870 | 0.5870 | 0.0000 | 0.6379 |
| (12,12,2) | 4 | 1/2 | r3 | 0.5870 | 0.5870 | 0.0000 | 0.6379 |
| (12,12,2) | 4 | 1/2 | r4 | 0.5870 | 0.5870 | 0.0000 | 0.6379 |
| (12,2,2) | 4 | 1 | r1 | 0.9714 | 0.6676 | 0.3038 | 0.6358 |
| (12,2,2) | 4 | 1 | r2 | 0.9623 | 0.6676 | 0.2948 | 0.6358 |
| (12,2,2) | 4 | 1 | r3 | 0.9325 | 0.6676 | 0.2649 | 0.6358 |
| (12,2,2) | 4 | 1 | r4 | 0.9323 | 0.6676 | 0.2648 | 0.6358 |
| (12,2,2) | 4 | 1/2 | r1 | 0.8562 | 0.5870 | 0.2692 | 0.6379 |
| (12,2,2) | 4 | 1/2 | r2 | 0.8496 | 0.5870 | 0.2626 | 0.6379 |
| (12,2,2) | 4 | 1/2 | r3 | 0.8334 | 0.5870 | 0.2465 | 0.6379 |
| (12,2,2) | 4 | 1/2 | r4 | 0.8334 | 0.5870 | 0.2464 | 0.6379 |
| (12,2,2) | 8 | 1 | r1 | 1.3532 | 0.9784 | 0.3748 | 0.2779 |
| (12,2,2) | 8 | 1 | r2 | 1.3245 | 0.9784 | 0.3461 | 0.2779 |
| (12,2,2) | 8 | 1 | r3 | 1.2976 | 0.9784 | 0.3192 | 0.2779 |
| (12,2,2) | 8 | 1 | r4 | 1.2974 | 0.9784 | 0.3190 | 0.2779 |
| (12,2,2) | 8 | 1/2 | r1 | 1.1057 | 0.7810 | 0.3246 | 0.2502 |
| (12,2,2) | 8 | 1/2 | r2 | 1.0826 | 0.7810 | 0.3015 | 0.2502 |
| (12,2,2) | 8 | 1/2 | r3 | 1.0613 | 0.7810 | 0.2802 | 0.2502 |
| (12,2,2) | 8 | 1/2 | r4 | 1.0613 | 0.7810 | 0.2802 | 0.2502 |
| (14,2,2) | 4 | 1 | r1 | 1.0928 | 0.6926 | 0.4002 | 0.6041 |
| (14,2,2) | 4 | 1 | r2 | 1.0774 | 0.6926 | 0.3848 | 0.6041 |
| (14,2,2) | 4 | 1 | r3 | 1.0430 | 0.6926 | 0.3504 | 0.6041 |
| (14,2,2) | 4 | 1 | r4 | 1.0424 | 0.6926 | 0.3498 | 0.6041 |
| (14,2,2) | 4 | 1/2 | r1 | 0.9587 | 0.6003 | 0.3584 | 0.5987 |
| (14,2,2) | 4 | 1/2 | r2 | 0.9465 | 0.6003 | 0.3462 | 0.5987 |
| (14,2,2) | 4 | 1/2 | r3 | 0.9163 | 0.6003 | 0.3160 | 0.5987 |
| (14,2,2) | 4 | 1/2 | r4 | 0.9163 | 0.6003 | 0.3160 | 0.5987 |
| (14,4,2) | 4 | 1 | r1 | 0.8737 | 0.6926 | 0.1811 | 0.6041 |
| (14,4,2) | 4 | 1 | r2 | 0.8563 | 0.6926 | 0.1637 | 0.6041 |
| (14,4,2) | 4 | 1 | r3 | 0.8410 | 0.6926 | 0.1484 | 0.6041 |
| (14,4,2) | 4 | 1 | r4 | 0.8406 | 0.6926 | 0.1480 | 0.6041 |
| (14,4,2) | 4 | 1/2 | r1 | 0.7326 | 0.6003 | 0.1323 | 0.5987 |
| (14,4,2) | 4 | 1/2 | r2 | 0.7241 | 0.6003 | 0.1238 | 0.5987 |
| (14,4,2) | 4 | 1/2 | r3 | 0.7135 | 0.6003 | 0.1132 | 0.5987 |
| (14,4,2) | 4 | 1/2 | r4 | 0.7135 | 0.6003 | 0.1132 | 0.5987 |
| (14,4,2) | 8 | 1 | r1 | 1.1701 | 0.9544 | 0.2157 | 0.2546 |
| (14,4,2) | 8 | 1 | r2 | 1.1370 | 0.9544 | 0.1826 | 0.2546 |
| (14,4,2) | 8 | 1 | r3 | 1.1173 | 0.9544 | 0.1629 | 0.2546 |
| (14,4,2) | 8 | 1 | r4 | 1.1171 | 0.9544 | 0.1627 | 0.2546 |
| (14,4,2) | 8 | 1/2 | r1 | 0.8895 | 0.7437 | 0.1458 | 0.2260 |
| (14,4,2) | 8 | 1/2 | r2 | 0.8677 | 0.7437 | 0.1241 | 0.2260 |
| (14,4,2) | 8 | 1/2 | r3 | 0.8527 | 0.7437 | 0.1090 | 0.2260 |
| (14,4,2) | 8 | 1/2 | r4 | 0.8527 | 0.7437 | 0.1090 | 0.2260 |

### Predictions scored

- **P1 held**: full context (12,12,2), W=4 — total = irreducible = 0.6676 (ε=1) / 0.5870 (ε=½), gap exactly 0.0, identical across rungs, strictly positive. Check: True. The first non-zero full-context ceiling in the project: what remains when the trace surrenders everything is the world's own randomness about who wakes next.
- **P2 held (conservation)**: the irreducible term is identical across all four rungs at every law, W, and ε (float-identical). Check: True. The interface ladder acts only on the gap term.
- **P3 held**: irreducible term larger at ε=1 than at ε=½ at every law and W (ε=1 is uniform-among-candidates scheduling). Check: True.
- **P4 held**: max r3→r4 movement of the gap term over all laws/W/ε = 0.00053 bits (≤ 0.001). The lineage rung carries nothing for Q4 either.
- **P5 REFUTED at its stated cell, and the general claim is MIXED**: at
  (12,2,2), W=4, ε=1 the gap term's r1→r2 drop is 0.0090 vs r2→r3
  0.0299 — owner-dominated, the opposite of Q4proxy. But across all ten
  windowed (law, W, ε) cells r1→r2 ≥ r2→r3 in exactly five: L=2 laws at
  W=4 are owner-dominated (both ε, both horizons); W=8 at (12,2,2) and
  (14,4,2), and (14,4,2) W=4 at ε=1, are **object**-dominated (narrowly
  at W=8/(12,2,2): 0.0287 vs 0.0269). Which rung "Q4 lives on" depends
  on the forecast horizon and the window length. I predicted from
  analogy with the proxy and was wrong at the named cell; I then nearly
  wrote "owner-dominated" as a finding over a table that says otherwise
  in half its rows — caught before commit this time, by subtracting my
  own numbers.

## Findings (v0.1)

1. **Statutory Q4 exists, is two-path gated (W ≤ 4, exhaustive over
   horizon-8 endpoint states), and is the first M1 target with a
   strictly positive full-context ceiling**: 0.6676 bits (ε=1) / 0.5870
   (ε=½) at W=4; 0.95 / 0.74 at W=8 for the horizon-14 states.
2. **The split works and obeys its conservation law.** Irreducible term
   invariant across rungs at every law; the observation-gap term is what
   the interface moves — 0.26–0.36 bits at L=2 laws, 0.11–0.15 at L=4.
   Q4's gap term is *larger* than every state-predicate query's total
   ceiling except Q4proxy[L0] and Q1[L0]: the predictive target is the
   most-hidden thing the trace has, at these laws.
3. **Which content rung Q4 loads on depends on W and L** — owner
   (r2→r3) at L=2/W=4, object (r1→r2) at W=8 and at L=4 for ε=1; no
   single-rung story survives the table. r3→r4 ≤ 0.0006 bits everywhere.
4. **Geometry over content, again**: L=2→4 at T_ep=14, W=4, r4 lowers
   the gap term 0.3498→0.1480 (ε=1); the whole content ladder at L=4
   moves it 0.0331. Same scope caveat as before: C1, these laws.
5. **W matters to the irreducible term, not to the ordering**: W=8
   raises irreducible from 0.69 to 0.95 (more chances for a stochastic
   wake) while the gap term at (14,4,2) moves 0.18→0.22; NONE mass
   0.64 at W=4 (most windows end with no wake within four ticks).

## Caveats

1. Two-path gate for the forward sum is exhaustive only at W ≤ 4 over
   horizon-8 endpoint states; W=8 runs rely on the same algorithm being
   correct at larger W (structurally the same recursion; not
   independently enumerated at W=8 — 8-step explicit enumeration is
   ~10⁵–10⁶ paths per state).
2. The forward sum runs past T_ep (decision (i)); if the statute is read
   as terminating the world at T_ep, endpoint-T windows would have
   NONE mass 1 and the numbers change. Flagged for the truthsayer.
3. Float sums of exact-Fraction distributions, as before.
4. Predictive-state targets P-next / P-horizon (Part II §5) share this
   machinery and are NOT yet computed; divergent-history search likewise.

---

*2026-08-15 ~20:40 PDT — status pointer, appended:* the amendment
`part2-amendment-proposal-v0.2.4.md` was confirmed by Tony and enacted as
Part II v0.2.4 (§A m/W/𝒯 frozen; §B continuation past T_ep; §D criterion
form; §C: thresholds unfrozen pending three sweeps and a second stamp).
Every number in this note precedes that stamp and remains **exploratory**;
nothing above is changed by the enactment.
