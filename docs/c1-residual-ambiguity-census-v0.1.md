# Residual-ambiguity census — what an r1 observer still doesn't know at context L, and which rung field can reach it

**v0.1 — 2026-09-03.** Exploratory diagnostic run for the Part C
intervention discussion, same session as `w11-predictive-rung-search-v0.1.md`
and `partition-identity-note-v0.1.md`. Producer
`scripts/c1_residual_ambiguity_census.py`; raws
`c1-residual-ambiguity-census-14-{4,8,10}-2-2026-09-03.json`; pins
`tests/test_residual_ambiguity.py`. Corrected kernel, canonical track,
(14, L, 2), both statutory ε. No ceiling, posterior or verdict is changed.
Numbers copied from the raws in-session.

## 1. Question

D1 Part B says the ordered ladder collapses under δ by L\* = 8 (r2→r3) and 10
(r1→r2). The collapse could have several mechanisms: threads finishing their
programs so the trace runs dry; the world synchronizing so fast that nothing
is left to resolve; or ambiguity surviving but of a kind no rung field can
reach. These have different interventions. The census separates them.

For every r1 window with posterior support > 1, record the set of state
fields in which the support states differ (`pc`, `status`, `running`,
`lock_owner`, `lock_wq`, `dev_q`, `rr_cursor`), its law mass, and whether
the r2, r3, r4 refinements split it. Aggregate by field signature.

## 2. Exhaustion is not the mechanism (checked first)

Expected number of TERMINATED threads at T = 14: 0.04 (ε = 1), 0.00 (ε = ½);
no path has all four terminated; no IDLE record occurs. C1's four-instruction
programs do not run out within 14 records (each instruction costs a DISPATCH
record and blocking stretches it further). At M1 scale — episodes of many
tens of records — they will, since the programs carry 16 instructions in
total; that is a separate reason to want nonterminating workloads, not the
reason the ladder collapses here.

## 3. Census

`amb` = law mass on r1 windows with support > 1. `reachable` = mass of those
windows that some rung refines (split by r4, which refines every other
rung); `unreachable` = mass of those windows no rung splits. Signatures
shown are the three largest plus the ones that carry the argument.

| L | ε | amb | reachable | unreachable | `pc` only (split by any rung?) | `pc`+`lock_owner` (r2 splits / windows) | `status`+`lock_wq` (split?) |
|---|---|---|---|---|---|---|---|
| 4 | 1 | 0.670 | 0.350 | 0.164 | 0.055 (no) | 0.100 (108 / 539) | 0.014 (no) |
| 4 | ½ | 0.668 | 0.285 | 0.223 | 0.107 (no) | 0.100 (108 / 539) | 0.033 (no) |
| 8 | 1 | 0.165 | 0.057 | 0.088 | 0.069 (no) | 0.050 (1871 / 3353) | 0.010 (no) |
| 8 | ½ | 0.145 | 0.049 | 0.088 | 0.059 (no) | 0.044 (1871 / 3353) | 0.028 (no) |
| 10 | 1 | 0.040 | 0.011 | 0.026 | 0.024 (no) | 0.010 (1788 / 1888) | 0 |
| 10 | ½ | 0.020 | 0.008 | 0.012 | 0.012 (no) | 0.008 (1788 / 1888) | 0 |

(reachable + unreachable < amb because a window some rung splits is counted
as reachable even when the split leaves part of the ambiguity in place.)

## 4. Reading

1. **The world synchronizes fast.** Ambiguous mass falls from 0.67 at L = 4
   to 0.04 (ε = 1) / 0.02 (ε = ½) at L = 10. By ten visible records an r1
   observer knows the state on 96–98 % of law mass. This is the D1
   falsifier's "over-synchronization," measured as a fraction rather than an
   entropy.
2. **What survives is mostly out of every rung's reach.** The dominant
   surviving signature at L ≥ 8 is program-counter ambiguity alone — a
   COMPUTE step in the dropped prefix that no later record reveals — and it
   is split by no rung at any L (0 / 4185 windows at L = 8, 0 / 4091 at
   L = 10). Wait-queue order with status (`status`+`lock_wq`) is likewise
   never split. The unreachable share of residual ambiguity rises with L:
   24 % at L = 4, 53 % at L = 8, 64 % at L = 10 (ε = 1).
3. **The only rung-reachable residual that matters is lock ownership.** The
   `pc`+`lock_owner` signature is what r2 and r3 act on (OBJECT of a visible
   ACQUIRE/BLOCK; RELATED = owner on BLOCK), and its mass is the r1→r2 gap's
   scale: 0.010 at L = 10, where D1 Part B's Q1 gap is 0.0066 bits. It decays
   because an unobserved ACQUIRE's owner is revealed the moment that thread
   RELEASEs (a visible actor) — the r2/r3 information has a half-life of one
   lock hold.
4. **Device-queue ambiguity is reached only by lineage** (r4 splits
   `pc`+`status`+`dev_q` windows: 50 / 481 at L = 8, 72 / 445 at L = 10), on
   small mass — the C1 form of the D10 lineage effect.
5. **ε = ½ has less ambiguity than ε = 1 at every L** (round-robin makes
   dispatch predictable). Scheduler randomness is already at its maximum at
   ε = 1; it is not a lever that can be turned further, and the reachable
   share it buys is small (0.057 vs 0.049 at L = 8).

## 5. What this says about the Part C candidate set (evidence, not a choice)

- **Structured nonterminating workloads with recurring lock contention** act
  on the one rung-reachable residual there is: ownership ambiguity survives
  only while holds are unobserved and unreleased, so recurring acquisition
  (loops) and longer or nested holds extend its half-life along L. This is
  also required at M1 scale for the exhaustion reason in §2. Cost: reachable
  state space and D4 pricing must be redone; periodic loops could make the
  posterior periodically resolvable — a pilot census on the variant world
  answers that before any freeze.
- **Exposable workload branches over the lock or device chosen** would make
  OBJECT informative in its own right (today OBJECT is a function of
  (thread, pc), so r2 only ever resolves pc). That is a direct r1→r2 lever
  at every L, and the branch outcome is exposed by the ACQUIRE/IO_ISSUE
  record itself. Branches over private computation add `pc`-only ambiguity,
  which no rung reaches — the wrong kind.
- **Scheduler/device entropy:** contra-indicated as a rung-separation lever
  by item 5; it raises H(S) without raising the reachable share.
- **Rung redesign / window law:** the only levers at U ≤ 2
  (`partition-identity-note-v0.1.md`), which is near-full-context and
  irrelevant at M1 scale.
- **Bound on interface value:** `pc`-only and queue-order ambiguity are
  unreachable by any field in the current record schema; whatever
  intervention is chosen, that share of the observation gap is not the
  ladder's to recover. TIME_CLASS does not reach it either (timing exposes
  order, not private computation).

The selection is the PI's. This note supplies the mechanism the choice
should be made against; it does not make it.

## 6. Not claimed

Anything beyond C1 at T_ep = 14; that the same shares hold at other
horizons (the (16, ·, 2) held-out artifacts could be censused the same way
— not done here); that a nonterminating variant will behave as §5 argues (a
pilot would show it).

## 7. Addendum (2026-09-03 11:15 PDT, same instance) — the exposure-side range check

The first of the "options I failed to mention" in the Part C discussion was
to question the metric: the ladder collapses on Q1–Q5 fact posteriors, but
M2 trains on next-record prediction, so the goal-relevant range is on the
predictive targets. Checked on rung-independent targets (next-2 kinds,
time-to-next-wake ≤ 4, next-completion lineage ≤ 4; observation-gap part of
the split, which is rung-comparable) from
`c1-predictive-targets-14-{2,4}-2-corrected-2026-08-20.json` and four runs
made for this section, `c1-predictive-targets-14-{6,8,10,12}-2-corrected-2026-09-03.json`
(same producer, corrected kernel, both statutory ε):

| L | ε | kinds2 gap r1 / r4 (r1 − r4) | ttw4 gap r1 / r4 (r1 − r4) | P-next gap r1 |
|---|---|---|---|---|
| 2 | 1 | 0.852 / 0.773 (0.079) | 0.324 / 0.290 (0.034) | 0.764 |
| 4 | 1 | 0.388 / 0.311 (0.076) | 0.155 / 0.128 (0.027) | 0.263 |
| 6 | 1 | 0.160 / 0.112 (0.048) | 0.065 / 0.048 (0.017) | 0.081 |
| 8 | 1 | 0.058 / 0.035 (0.023) | 0.023 / 0.013 (0.010) | 0.021 |
| 10 | 1 | 0.016 / 0.009 (0.007) | 0.007 / 0.002 (0.004) | 0.003 |
| 12 | 1 | 0.000 / 0.000 (0.000) | 0.000 / 0.000 (0.000) | 0.000 |

(ε = ½ is uniformly smaller: kinds2 r1 − r4 = 0.049, 0.041, 0.028, 0.015,
0.005, 0 at the same L.) Reading: the exposure-side ceilings collapse on the
**same horizon** as the fact ladder — the interface's share of the predictive
gap is under δ = 0.01 bits by L = 10 and exactly zero by L = 12 — and the
*whole* predictive observation gap is 0.003 bits at L = 10. The interface is
a larger *fraction* of what remains at long context (9 % of the kinds2 gap at
L = 2, 40 % at L = 8) but the remainder is vanishing. So the metric is not the
problem: C1 synchronizes for every target, and a transformer with ten or
more records of context would see no interface effect on any objective. The
"question the metric" option is closed; the intervention is needed for the
exposure experiments as much as for the ladder. The four new artifacts are
committed; the lineage target's gap is ≤ 0.003 bits at every L ≥ 4 and is
not tabulated.
