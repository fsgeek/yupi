# D1 Falsifier Verdict — Over-Synchronization (v0.1)

**Status: verdict note for deliverable 4's "D1 falsifier verdict" item
(evidence map v3, item 4.4). Part A is adjudicated by theorem and final;
Part B is measured but formally conditional on the second stamped
threshold decision; Part C is a decision put to the PI, not made here.**
Aug 17 2026, ~19:45 PDT, ninth instance. Prompted by external review
(via Tony, Aug 17): a proof satisfied a falsifier that was worded as a
measurement, and the record held a design pivot where an adjudication
should be — this note supplies the adjudication.

## The falsifier as written (Part I, D1)

> "Over-synchronization. Deterministic workloads may make the world too
> inferable — long contexts could collapse every interface to certainty,
> erasing rung differences. M1 must measure posterior entropy vs.
> context length per interface. Contingency: add back the minimal
> workload randomness needed to keep rungs separated … ordering: (1)
> additional scheduler/device entropy, whose consequences the ladder
> differentially reveals; (2) randomized-but-exposable workload branches
> (a field a rung can carry); (3) private workload coins, last resort
> only."

## Part A — verdict at full context: FIRED, by theorem

At L = T_ep (observation from reset), every posterior is a point mass at
every content rung r1–r4, for **every** kernel in the enacted family —
not measured collapse but structural injectivity
(`docs/full-context-injectivity-note-v0.1.md`, commit 0772227, Aug 13;
independently verified by direct path summation, 12590db). "Long
contexts collapse every interface to certainty, erasing rung
differences" is satisfied exactly: all rung differences are zero at full
context, H = 0.

The record's response at the time was the design pivot "truncation is
the only door" — correct in content, but never entered as a D1
adjudication, and the falsifier's contingency ladder was neither invoked
nor declined. A proof slipped past a condition worded for a curve. This
note closes that gap: **the full-context component of the falsifier
fired on Aug 13.**

Scored alongside it: the founding "design constraint with teeth" (b) —
*the sparsest interface produces the fastest posterior-support growth;
the most interesting condition is the most computationally hostile one*
— is **refuted** in this world. Max support 28 against D4's budget of
20,000 (~300× headroom); the sparse interface's hostility was epistemic
for the model, never computational for the oracle. The founding-day risk
ran in the opposite direction: not intractability but legibility.

## Part B — verdict along the L axis: rungs separate at short L, collapse by L* ≈ 8–12; formal adjudication awaits δ

The mandated measurement exists (`c1-sync-sweep-v0.1.md` §2d: adjacent-
rung max statutory gap vs. L at (14,L,2), both ε; per-endpoint reruns
9deff20). Content: r1→r2 and r2→r3 gaps are material at L ≤ 4 (0.06–0.18
bits), decay geometrically, and are exactly zero by L = 12; r3→r4 is
≤ 0.0037 everywhere and zero by L = 12. Under the **proposed** δ = 0.01
(v0.3.1, unstamped) the collapse horizons are L* = 2 (r3→r4), 8 (r2→r3),
10 (r1→r2), both ε. Supporting decomposition: the non-clock component of
window uncertainty is ≈½ of H(S_T|w) at L=2, ⅓ at L=4, ⅙ at L=8
(`c1-offset-vs-state-v0.1.md`).

So the measured answer is: **the falsifier does not fire at L ≤ 4 for
the r1/r2/r3 ladder; it fires along L with horizon ≈ 8–12; and the
lineage rung (r3→r4) is below any plausible δ at every measured L in
this world** — the ordered content ladder's fourth rung carries nothing
a threshold would keep. Formal verdict language ("fired at L ≥ x") binds
only when δ does.

## Part C — the contingency decision (PI's, framed not made)

The falsifier's contingency asks for "the minimal workload randomness
needed to keep rungs separated." The measurements above change the
question: rungs r1/r2/r3 ARE separated in the base world at short L —
the operating regime Part II §2 already made the training condition. The
decision is therefore not "rescue the world" but "which axis next":

- **Option 1 — D8 first (recommended).** Build the shuffled/bucketed
  order mode before touching world entropy. Reasons: (i) it is the one
  manipulation aimed at the injectivity mechanism itself, so it can
  restore interface-driven uncertainty *at long L* without changing the
  world's dynamics — entropy in the channel, on-thesis for a paper about
  observation; (ii) D1's own qualifier warns that added world entropy
  raises the irreducible floor without necessarily increasing what
  richer rungs deliver; (iii) the D1 ladder remains available unchanged
  if D8's separation proves insufficient.
- **Option 2 — invoke D1 step (1) now** (scheduler/device entropy: finer
  ε grid, completion-hazard spread). Defensible if the short-L regime is
  judged too thin a base for training corpora on its own.
- **Option 3 — accept the short-L regime as M1's operating condition
  and proceed to corpus design with L ≤ 4–8**, deferring both levers.
  Cheapest; leaves the lineage rung dead in the ordered channel and the
  long-L regime empty.

These are not exclusive; 1 then 3 is the recommended path. Whichever is
chosen should be recorded as the D1 contingency decision with this note
cited.

## Consequences for the record

- Evidence map v3 item 4.4 splits: Part A DONE (this note); Part B
  AWAITS 2ND STAMP (formal wording only — the curves exist); Part C is a
  PI decision.
- The M1 exit clause "measurably distinct observability regimes across
  rungs" should be read against Part B: demonstrated for r1/r2/r3 at
  short L in the ordered channel; not demonstrable for r3/r4 there at
  any measured L.
- CLAUDE.md's constraint (b) should not be cited as a live design
  constraint for this world without noting its refutation (Part A).

## Caveats

- All Part B numbers are the (14,L,2) family plus (12,2,2)-family notes;
  one T_ep pair, ε ∈ {1, ½}, ordered channel only, D9's ε=1 provisional.
- Part A's theorem is about the enacted kernel family; D8's stochastic
  channel deliberately exits its hypotheses — that is the point of
  Option 1.
