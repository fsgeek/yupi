# r0 — a kind-only rung below the statutory ladder: range at every context, at trivial cost, and what the range is made of

**v0.1 — 2026-09-03.** Exploratory. Instance following the map-v4 author;
same day as `c1-residual-ambiguity-census-v0.1.md`, whose §5 named this as
the cheapest non-inferior Part C option and whose order of work put it
first. `interfaces.project` gains `"r0"` (EVENT_KIND only; actor, object,
related, lineage all MASKED) — an instrument extension, **not a Part II
rung**: the statutory ladder (§4, proposal §6.1) is unchanged, and no
committed number changes. Producer `scripts/r0_ladder_census.py`
(enumerator side, ungated except for a timed two-path sample); raws
`r0-ladder-census-14-{2,…,14}-2-2026-09-03.json`; pins
`tests/test_r0_ladder.py`. Corrected kernel, canonical track, both
statutory ε. Numbers copied from the raws in-session.

## 1. Result

Law-mass means at (14, L, 2). `gap` = observation-gap part of the split
(rung-comparable; the irreducible part is rung-invariant).

| L | ε | H(S) r0 / r1 / r4 | next-2-kinds gap r0 / r1 / r4 | r0 − r1 | r1 − r4 | Q1[L0] r0 / r1 | max support r0 / r1 |
|---|---|---|---|---|---|---|---|
| 2 | 1 | 5.397 / 3.341 / 3.018 | 1.154 / 0.852 / 0.773 | 0.303 | 0.079 | 1.199 / 0.713 | 218 / 138 |
| 4 | 1 | 4.132 / 1.344 / 1.098 | 0.879 / 0.388 / 0.311 | 0.491 | 0.076 | 0.912 / 0.247 | 175 / 87 |
| 6 | 1 | 3.325 / 0.487 / 0.364 | 0.694 / 0.160 / 0.112 | 0.534 | 0.048 | 0.756 / 0.069 | 119 / 54 |
| 8 | 1 | 2.869 / 0.152 / 0.109 | 0.582 / 0.058 / 0.035 | 0.523 | 0.023 | 0.673 / 0.016 | 64 / 28 |
| 10 | 1 | 2.656 / 0.032 / 0.025 | 0.521 / 0.016 / 0.009 | 0.505 | 0.007 | 0.626 / 0.001 | 39 / 8 |
| 12 | 1 | 2.577 / 0.001 / 0.001 | 0.488 / 0.000 / 0.000 | 0.488 | 0.000 | 0.609 / 0.000 | 33 / 2 |
| 14 | 1 | **2.577** / 0.000 / 0.000 | **0.488** / 0.000 / 0.000 | 0.488 | 0.000 | 0.609 / 0.000 | 33 / 1 |
| 14 | ½ | **2.375** / 0.000 / 0.000 | **0.512** / 0.000 / 0.000 | 0.512 | 0.000 | 0.500 / 0.000 | 36 / 1 |

(ε = ½ rows at every L are in the raws; they are uniformly a little lower
in H(S) and a little higher in the kinds2 gap, with the same shape.)

Three things the table says:

1. **The interface axis has dynamic range at every context, including
   full context**, once r0 is on it. The r0 → r1 step is 0.49–0.60 bits on
   next-2 kinds at every L ≥ 4 and does not decay; the r1 → r4 ladder is
   0.08 at L = 2 and gone by L = 12, as measured before.
2. **r0 is not injective at full context.** H(S) at r0 plateaus at 2.577
   bits (ε = 1) / 2.375 (ε = ½) from L = 12 on, L = 14 included. The
   full-context injectivity theorem (`full-context-injectivity-note-v0.1.md`)
   is stated for r1 and rests on ACTOR; r0 is the first interface in the
   instrument for which the trace does not determine the state even from
   reset. The ambiguous law mass at r0 is 0.97–1.00 at every L.
3. **It costs nothing that matters.** r0 windows are fewer (195 at L = 4
   against 3489 at r1) with larger supports (max 282 at L = 2 falling to
   33–36 at L ≥ 12; at L ≥ 8 the modal support is 6 and no support exceeds
   64). The timed two-path sample — the 20 largest r0 supports at each L,
   filter against path aggregation — passed with zero mismatches at every
   L and both ε in 0.1–3.8 s total. The full gate was not run; nothing here
   is a statutory ceiling until it is.

## 2. What the r0 range is made of

The r0 residual census (fields on which the r0 support disagrees; whether
r1 splits the window) at L = 12, ε = 1: `status`+`running` 0.334 of law
mass, `pc`+`status`+`running`+`lock_owner` 0.276,
`pc`+`status`+`running`+`lock_owner`+`lock_wq` 0.259,
`status`+`running`+`lock_wq` 0.064, `lock_wq` 0.025 — and **r1 splits every
one of them** (100 % of windows in every signature at L ≥ 8; at L = 4 all
but a handful). Support sizes at L ≥ 8 cluster on 6, 12 and 18.

So the r0 residual at long context is **thread identity**: with only
EVENT_KINDs visible, the observer cannot tell which thread acted, and
threads whose programs are kind-permutations of each other (threads 0 and
2 share the multiset {ACQUIRE, STEP, RELEASE, IO_ISSUE}; thread 1 is the
double-acquirer, thread 3 the double-issuer) stay confounded for the whole
episode. The 2.4–2.6-bit plateau is a permutation entropy over
kind-indistinguishable roles, and every fact query that names a thread —
all of Q1, Q2, Q5 — inherits it (Q1[L0] ≈ 0.6 bits at full context: "some
thread holds lock 0" is known, "which" is not).

This is the naming question in structural clothing. Part II v0.2.6 Clause
2′ says every committed number is a structural-characterization quantity
under a canonical injection σ₀, and that a surface name's answer
distribution is a mixture over its possible bindings (the C1 tick-4 Q2
counterexample: 1.208 bits for a uniformly bound name against 1.000 /
1.483 structural). r0 makes that mixture *the observer's own* posterior:
at kind-only, the trace binds no name to any role, so the r0 ceiling on a
thread-naming query is close to what the random-naming corpus process
would show at r1 without a bridge. That is either a confound or an
instrument — I record it as both until the naming bridge (§2 of Part II)
is built. What it is *not* is a rescue of the r1–r4 ladder: the ladder's
collapse is unchanged, and r0's range lives in a coordinate the ladder was
never about.

## 3. Consequences for the Part C decision (researcher's reading)

- r0 gives M2's interface axis a rung with range at every context for the
  price of one projection. It should be on the axis, and I will propose it
  as a Part II amendment (a fifth rung below r1, with r0's non-injectivity
  and its identity-residual stated) — an amendment, because the ladder is
  statute and this changes what "interface" ranges over in the paper.
- It does not remove the need for the workload pilot. The r1–r4 ladder
  measures object / owner / lineage information; r0 measures identity.
  If the paper's claim is about the former, C1 still has no range there
  past eight records, and the nonterminating-contention pilot is next.
- The naming bridge moves up the list. With r0 on the axis, the
  structural-vs-random-naming question stops being paper-gating only and
  becomes part of the interface variable itself.

## 4. Not claimed

That r0's plateau is exactly a permutation entropy (support sizes and
signatures say so; no proof); that r0 ceilings are statutory (ungated);
anything at other horizons or worlds; that the exploratory r0 → r1 gap
figures survive the naming bridge unchanged.

## 5. Cost

Enumerator side, one core: 1.0 → 7.4 min per L, peak RSS 1.0 → 4.4 GB
(L = 14). The r0 filter sample is negligible at every L.
