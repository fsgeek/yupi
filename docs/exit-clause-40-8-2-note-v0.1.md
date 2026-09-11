# The exit clause at the frozen law — (40, 8, 2) on the looping C1′, both statutory ε (v0.1, 2026-09-11)

> **Status: EXPLORATORY reading of a gated measurement.** Every number
> below comes from the thirty producer artifacts at (40, 8, 2) that are
> pinned in `tests/test_c1prime_loop_ceilings.py`, each produced under the
> external gate: all ten (rung, ε) pairs r0–r4 have every window's posterior
> exact through `filter_window` (8,542,940 windows, zero mismatches,
> `tests/test_window_gate_full.py`). The numbers cannot change. Their
> *status* can: the freeze note that chose this law
> (`looping-exit-law-freeze-v0.1.md`) is not enacted, because the producer
> pass is **refused on memory** by the D4 erratum E3 as the instrument runs
> today (13.03 / 13.25 GB against 8 GB; frontier 1,964,919, admitted). Until
> the pass is brought under the line by exact means and the freeze is
> enacted, this note is a reading, not a verdict. Written by the instance
> of 2026-09-11 under the PI/researcher split; reviewed cross-family (see
> the ledger at the end).

## 1. What the clause says, and how it is read here

Part I (`yupana-m1-spec-draft.md`, "Deliverables and exit criteria"):

> M1 succeeds if the report shows measurably distinct observability
> regimes across rungs within tractable support bounds, **and** exhibits
> history classes where immediate predictions agree but longer-horizon
> distributions differ (deliverable 5).

Three readings are fixed before the numbers are looked at:

- **"Measurably distinct"** is the v0.2.5 criterion (Part II §6, enacted
  2026-08-21): an adjacent pair is collapsed at context $L$ iff the maximum
  over the complete statutory query set of the coarser rung's mean
  conditional entropy minus the finer rung's is below **δ = 0.01 bits**;
  distinct otherwise. The statutory set is every query the ceilings
  artifact carries except the Q4 proxies and `Q3thr[D0]`: Q1[L0], Q1[L1],
  Q2[T0..T3], Q3[D0], the twelve Q5 pairs, Q5joint (the pin test's own
  definition). The predictive side — the Q4 gap at $W = 4$, the next-2-kind
  gap, the P-next gap — is reported beside, not in the maximum.
- **"Across rungs" means the content ladder r1–r4.** The clause was
  written for that ladder; r0 (kind-only) was added by Part II v0.2.7.1
  (enacted 2026-09-11) for the D2 witness and the identity result, and the
  same amendment revises D1's falsifier to "every content rung r1–r4". The
  r0 → r1 step is reported **beside** the ladder, never inside the
  maximum. This was the PI's decision under v0.2.7.1 Clause 4; on
  2026-09-06 the PI placed it with the researcher ("this is your project,
  it is your decision to make"), and the researcher decided it that day,
  before writing this note, with the reasons in §5. The "three rungs
  distinct" phrasing in `d1-falsifier-verdict-v0.1.md` is a gloss, not
  statute, and is not used.
- **"Within tractable support bounds"** is E3: the pass that produced these
  numbers must be admitted. It is not, today (§2). The clause's first
  condition therefore cannot be called satisfied by this note, whatever
  the gaps say.

## 2. The law, the gate, and the pass

(T_ep, L, B) = (40, 8, 2) on `c1prime-loop` (four contention roles kept
alive indefinitely, v0.2.8.1), chosen by the freeze note on 2026-09-04
under the admitting rule, before any ceiling existed at it.

| | ε = 1 | ε = ½ |
|---|---|---|
| windows per rung r4 / r3 / r2 / r1 / r0 | 1,524,612 / 991,585 / 923,461 / 819,073 / 12,739 | same (the window set does not depend on ε) |
| gate: windows exact through the filter | 4,271,470, **0 mismatches** | 4,271,470, **0 mismatches** |
| pass frontier $\max_t \lvert\mathrm{frontier}_t\rvert$ | 1,964,919 (admitted, 1.8 % margin) | 1,964,919 |
| pass peak RSS, Sep 4 instrument | 7.21 GB (admitted) | 7.23 GB |
| pass peak RSS, instrument of Sep 6 (per-endpoint mass instrumentation, `06541a2`) | **13.03 GB (refused)** | **13.25 GB (refused)** |

The producers ran on the Sep 6 instrument. The frontier line binds the
world's cost and is met; the memory line binds the implementation's and is
not. The freeze note's addendum records the researcher's path (profile,
exact-only reduction, bit-for-bit gate against the current recursion at
this law, re-price) and the commitment that the line is not moved to admit
the law.

## 3. The reading on the content ladder

Adjacent-pair maxima over the statutory set (coarser minus finer, bits),
with the query that carries each:

| pair | ε = 1 | × δ | ε = ½ | × δ |
|---|---|---|---|---|
| r1 → r2 | **0.0477** (Q1[L1]) | 4.8 | **0.0366** (Q1[L1]) | 3.7 |
| r2 → r3 | **0.1100** (Q1[L0]) | 11.0 | **0.0523** (Q1[L0]) | 5.2 |
| r3 → r4 | **0.0142** (Q3[D0]) | 1.4 | **0.0113** (Q3[D0]) | 1.1 |
| r1 → r4 (range) | 0.1439 (Q1[L0]) | 14.4 | 0.0764 (Q1[L0]) | 7.6 |

**Every adjacent content pair is above δ at both statutory ε.** The r3 → r4
step is thin — 1.42× δ at ε = 1 and 1.13× δ at ε = ½ — and is reported as
thin: a δ of 0.015 would collapse it at ε = ½, a δ of 0.02 at both. δ was
frozen on 2026-08-21 from the three sweeps, before the looping world
existed; the thinness is a fact about lineage at context 8, not about the
threshold's placement. The other two steps are comfortably clear.

The state-entropy ladder $H(S \mid \text{window})$, law-mass mean: 0.6008 →
0.5277 → 0.4046 → 0.3898 bits at ε = 1 (steps 0.073 / 0.123 / 0.015);
0.2963 → 0.2400 → 0.1774 → 0.1658 at ε = ½ (0.056 / 0.063 / 0.012). The
predictive side moves in the same places: the Q4 gap 0.1281 → 0.1086 →
0.0795 → 0.0761 (ε = 1), next-2-kinds 0.1858 → 0.1572 → 0.1239 → 0.1191,
P-next 0.1503 → 0.1346 → 0.1060 → 0.1026; monotone at both ε.

## 4. What each field buys, read off the carrying queries

- **OBJECT (r1 → r2)** resolves the owner of lock 1 (Q1[L1], 0.048 / 0.037)
  and, with it, the thread-pair relations that run through that lock (every
  Q5 pair moves 0.003–0.011). The lock-0 owner barely moves (0.034 / 0.024
  on Q1[L0]) — lock 0's contention pattern is already legible from actors.
- **RELATED (r2 → r3)** resolves the owner of lock 0 (Q1[L0], 0.110 / 0.052,
  the largest content step at both ε) and the thread statuses (Q2[T0..T2]
  each 0.02–0.03 at ε = 1). This is the step the live world makes large:
  from reset at (14, L, 2) it collapsed by L = 8.
- **LINEAGE (r3 → r4)** resolves the device's in-flight request (Q3[D0],
  0.014 / 0.011 — the whole step) and thread 3's status (Q2[T3], 0.0045 /
  0.0028; thread 3 is the double-issuer). Nothing else moves by more than
  0.001. At context 8 in a live world, lineage buys the device and almost
  nothing about locks or threads.

## 5. The r0 → r1 step, beside the ladder

| quantity | ε = 1 | ε = ½ |
|---|---|---|
| max statutory gap r0 → r1 | **1.0769** (Q2[T0]) | **0.9957** (Q2[T0]) |
| Q1[L0] / Q1[L1] | 0.834 / 0.513 | 0.730 / 0.460 |
| H(S) step | 3.3465 | 3.0748 |
| Q4 gap / next-2-kinds / P-next steps | 0.575 / 0.569 / 0.292 | 0.646 / 0.682 / 0.332 |

The naming step is an order of magnitude larger than the whole content
ladder. It is not counted toward the clause, for four reasons recorded when
the decision was taken (2026-09-06):

1. The clause predates r0 and was written for the ladder r1–r4; r0 entered
   by amendment for the D2 witness and the identity result.
2. r0 → r1 is the step that reveals *who*; every other step reveals *what*
   about the world. The naming bridge (v0.2.6 Clause 2′) is about to
   separate those axes, and the exit clause is not the place to mix them.
3. v0.2.7.1 itself treats r0 as outside the content rungs (D1's revised
   falsifier); the exit reading matches the statute it accompanies.
4. Direction of bias: counting r0 adds an adjacency that passes by a
   hundred δ and can only make the clause easier. Excluding it is the one
   choice that hindsight cannot have favoured, and it means a contested
   r3 → r4 step cannot be rescued by r0.

What the step *is*: per the identity-residual check
(`r0-identity-residual-14-2-2026-09-04.json`, v0.2.7.1 statement 2), about
four fifths of r0's ambiguous mass at ε = 1 sits in supports whose states
differ even under a coarse thread-signature quotient. The residual is
attribution of visible actions to role-asymmetric threads, not a relabeling
orbit; the identity-entropy decomposition remains open.

## 6. From reset versus mid-episode

The committed evaluations of the clause are from-reset statements on C1 at
horizon 14 (`d1-falsifier-verdict-v0.1.md` Part B, corrected kernel):
collapse horizons $L^* = 10$ (r1 → r2), $8$ (r2 → r3), $2$ (r3 → r4) at both
ε, every statutory gap exactly 0 at $L = 12$ and $14$. In that world, by
context 8, only the object step survived, and lineage never separated at
any measured context.

At (40, 8, 2) mid-episode the same three steps are 4.8× / 11× / 1.4× δ
(ε = 1). The interface did not change; the window's starting prior did. A
from-reset window at (14, 8, 2) sees a world eight to ten records from
birth, with most of its threads' futures determined by their programs; a
mid-episode window at (40, 8, 2) sees a world that has been contending for
up to thirty-two records, whose lock owners and device state are live
questions. The deep-truncation census at (32, 8, 2) found the same at ε = 1
with two steps at threshold at ε = ½ (0.009, 0.010); at (40, 8, 2) both ε
clear δ on every pair. The exit clause, read in a world that stays alive,
comes out the other way from the world that dies.

## 7. The corrected §6 conditional at this law

v0.2.7.1 Clause 2 replaces $E[H \mid U > 0] = H_{law}/\Pr(U>0)$ by
$(H_{law} - H_{U=0})/\Pr(U>0)$. At (40, 8, 2), $\Pr(U > 0) = 4/5$:

| rung | ε | $H_{law}$ | $H_{U=0}$ | corrected $E[H \mid U>0]$ | v0.2.5 closed form |
|---|---|---|---|---|---|
| r0 | 1 | 3.9474 | **0.5395** | **4.2598** | 4.9342 |
| r0 | ½ | 3.3711 | **0.5551** | **3.5200** | 4.2138 |
| r1 | 1 | 0.6008 | 0 (exactly) | 0.7510 | 0.7510 |
| r1 | ½ | 0.2963 | 0 (exactly) | 0.3703 | 0.3703 |

Clause 2 bites at r0 only, by 0.67 / 0.69 bits; for every content rung the
two forms agree exactly, as the injectivity theorem requires. (Computed
with `yupi.sync.conditional_from_by_endpoint` on the pinned ceilings
artifacts; the r1 rows are the regression.)

## 8. Deliverable 5 — history classes that agree now and diverge later

Law mass in divergent pairs under the frozen criterion (v0.2.4 §D form;
field `divergent.mass` of the predictive-targets artifacts):

| ε | r0 | r1 | r2 | r3 | r4 |
|---|---|---|---|---|---|
| 1 | 0.2018 | 0.6085 | 0.6377 | 0.7113 | 0.6698 |
| ½ | 0.2024 | 0.6598 | 0.6902 | 0.7642 | 0.7184 |

Between three fifths and three quarters of the law's mass at every content
rung lies in pairs that agree on the immediate prediction and diverge at
the horizon: the raw material of the exposure experiments is abundant
mid-episode, at every ε. At r0 it is a fifth — kind-only histories mostly
cannot be told apart even at the horizon.

## 9. Reading, and what would reverse it

**Subject to the freeze being enacted and its pass admitted:** the clause's
first condition holds at (40, 8, 2) on the content ladder at both statutory
ε — every adjacent pair measurably distinct, the lineage step thin — and
its second condition holds by measurement. Nothing here is a verdict until
§2's refusal is resolved.

Reversed by: any mismatch in the bit-for-bit gate of the memory-reduced
recursion against the current one (then these artifacts are void, not
merely exploratory); a re-freeze to a law at which r3 → r4 falls under δ
(then the ladder is three distinct regimes plus a collapsed lineage rung,
and the clause is re-read there); a change to δ (not proposed; it was
frozen before this world existed). Not reversed by the PI counting r0 —
that can only add.

## 10. Statutory after the fact — the disclosure

The thirty artifacts were produced before the freeze note was enacted and
before the pass was re-priced. The order of fixing, from the stamps: the
budget line (v0.2.8, `a73ece8`, 2026-09-03 19:37) → the law (freeze note,
`b7adebe`, 2026-09-04 15:56) → the gate and the producers (Sep 4–6) →
v0.2.8.1 and v0.2.7.1 enacted (Sep 6, Sep 11) → the re-price refusing the
pass (Sep 6). δ (v0.2.5, 2026-08-21) and the statutory query set predate
all of it. The one decision made with these numbers in hand is the r0
reading (§5), and it resolved in the direction that cannot have been
favoured by seeing them. The researcher's decision of 2026-09-06 (enact
with disclosure; no re-run of exact arithmetic to launder a timestamp; the
primary law not kept exploratory forever) stands, and (48, 6, 2) — priced
and admitted with a factor of five to spare — remains the post-enactment
control whose every antecedent is post-enactment, to be run as the
horizon-versus-context replication if the primary's verdict is contested.

## 11. Not claimed

That the clause is satisfied (§2); any statutory gap; that these numbers
are random-naming ceilings (every one is a canonical-track quantity under
v0.2.6 Clause 2′; the r0 caveat is the sharpest); that the identity-only
share is an entropy fraction; that lineage would stay above δ at a deeper
context or a different B; that deliverable 5's mass measures anything
beyond the frozen §D criterion.

## Provenance

Artifacts: `docs/c1prime-loop-{query-ceilings, q4-ceilings…-W4,
predictive-targets}-40-8-2-<rung>-<date>[-eps1_2].json`, thirty files,
listed one by one with a regeneration snippet in
`docs/exit-clause-tables-40-8-2-2026-09-11.md` (the full per-query tables
at both ε, from which §3–§8 are read). Pins:
`tests/test_c1prime_loop_ceilings.py` (every adjacent maximum, both
all-pairs tests, the thirty-artifact test), `tests/test_window_gate_full.py`
(the ten gates). Pricing: `docs/window-process-pass-pricing-c1prime-loop-40-8-2-2026-09-04.json`
(Sep 4) and `…-2026-09-06-reprice.json` (Sep 6, refused). Tables for this
note were extracted by a Sonnet subagent on 2026-09-11 from the artifacts
alone and checked against the pin test's asserted values (all match).

## Review ledger

*(cross-family read requested 2026-09-11; findings folded in here.)*
