# Rung degeneracy by truncation depth — the ladder is partition-identical whenever the observer dropped at most two records

**v0.1 — 2026-09-03.** Instance following the map-v4 author; same session as
`w11-predictive-rung-search-v0.1.md`, which found the mechanism at one law.
This note is the census across every law we have measured, plus a C0b check
run for it. Exploratory (no prereg); every count below is copied from the
named artifact or from the enumeration script pinned in
`tests/test_partition_identity.py`. No ceiling, posterior or verdict is
changed by this note.

## Claim (measured, every committed law)

Let `n_r(T_ep, L, B)` be the number of distinct (RESET-observed, r-projected
window) classes under the window law — the `n_windows` field of every
`c1-query-ceilings-*.json`. Because each rung only adds fields
(`interfaces.project`), the r4 partition refines the r1 partition, so
`n_1 ≤ n_2 ≤ n_3 ≤ n_4`, with equality iff the partitions coincide — iff every
rung holds the same belief on every window, and every functional of the
belief (Q1–Q5, P-next, every τ ∈ 𝒯) is rung-invariant bit for bit.

**Across all 98 (artifact, ε) rows in the 49 committed C1 ceilings files
and 20 rows enumerated here, `n_1 = n_4` iff `U = T_ep − L ≤ 2`.** No
exception in either direction.

| world | T_ep | B | laws with U ≤ 2 (all EQUAL) | laws with U ≥ 3 (none EQUAL; r1 → r4 at the smallest U) | source |
|---|---|---|---|---|---|
| C1 | 12 | 2 | L = 12 (U 0) | L = 2 (U 10): 186 → 287 | corrected + raw, both ε |
| C1 | 14 | 2 | L = 12 (U 2): 239799; L = 14 (U 0): 394824 | L = 10 (U 4): 146926 → 149183 | corrected, raw, held-out ε ∈ {¼, ⅝} |
| C1 | 14 | 1 | L = 13 (U 1): 585840 | L = 11 (U 3): 342872 → 346192 | held-out F3′ |
| C1 | 16 | 2 | L = 14 (U 2): 1051282 | L = 12 (U 4): 676929 → 678688 | held-out F1 |
| C1 | 10 | 1 | L = 8, 9, 10 (U 2, 1, 0): 17624, 24700, 24878 | L = 7 (U 3): 12471 → 13090 | enumerated here, ε = ½ |
| C0b fifo | 8 | 1 | L = 6, 7, 8 (U 2, 1, 0): 102 | L = 5 (U 3): 100 → 102 | enumerated here |
| C0b stoch. | 8 | 1 | L = 6, 7, 8 (U 2, 1, 0): 142 | L = 5 (U 3): 134 → 142 | enumerated here |

(The buggy-kernel raw rows differ in count from the corrected rows at the
same law — 239111 vs 239799 at (14, 12, 2) — and satisfy the same rule; the
rule is about which records are dropped, not about the tick-11 fix.)

## Why (argument for C1; consistent-with for C0b; not a theorem)

A truncated window drops the first U records from reset. Higher-rung fields
of the *visible* suffix are deterministic functions of the history
(`full-context-injectivity-note-v0.1.md`, proof sketch): OBJECT is the
program instruction at the thread's pc; RELATED is the lock owner or the
FIFO head; LINEAGE is the lowest-free request id. The only way a masked
suffix field can carry information the r1 suffix does not is through the
dropped prefix — the prefix must contain an event whose identity the r1
suffix leaves open and on which a later masked field depends.

- **C1 (two CPUs, dispatch prioritized over execution, §3.1):** from reset the
  first two records are always DISPATCH, DISPATCH (enumerated: every path's
  first three kinds are (DISPATCH, DISPATCH, X) with X ∈ {ACQUIRE, IO_ISSUE,
  STEP}). DISPATCH carries no OBJECT, RELATED or LINEAGE, and which thread
  it dispatched is recoverable from the suffix's actors. So with U ≤ 2 the
  prefix has no masked content and the partitions coincide. At U = 3 the
  dropped third record can be an ACQUIRE whose actor is not fixed by the
  suffix at r1, and a later BLOCK's RELATED (the owner) then splits the
  window — exactly the r2/r3 information the ladder is built on.
- **C0b (one CPU):** the first two records are DISPATCH, IO_ISSUE, and the
  issue's OBJECT (the only device) and LINEAGE (request id 0, lowest-free
  from an empty pool) are forced. So the two-record prefix again has no
  masked content, though for a different reason than in C1. I have not
  proved that no C0b path at U = 3 could also be fieldless; the census says
  the partitions split there, and the mechanism is the same genus.

The threshold 2 is therefore not "the number of CPUs" (C0b has one CPU and
the same threshold); it is the length of the *fieldless prefix* from reset
in each world, which happens to be two in both. A world whose third record
were also fieldless would move the threshold to 3; a world with a
first-record ACQUIRE would move it to 0.

## What it changes

1. **D1 Part B's exact zeros at L ≥ 12 are structural, not δ-effects.** The
   collapse horizons L\* = 2 / 8 / 10 are threshold verdicts on real but
   sub-δ gaps; the exact degeneracy two ticks before full context is the
   fieldless prefix. Both are true; they should not be read as one curve.
2. **Constraint on the Part C intervention.** Any intervention meant to keep
   the rungs distinct at U ≤ 2 must change what the first records from
   reset carry — a scheduler rule, a rung redesign, or a window law that
   drops more — because no workload change can put masked content into a
   DISPATCH. Workload-side candidates (exposable branches, structured
   nonterminating workloads) can only act at U ≥ 3. Recorded as a constraint
   on the candidate set; the selection remains the PI's.
3. **Witness 11's region** is fixed by the same fact: the search space for
   clause (b) is U ≥ 3, and the note above found candidates only at the
   deepest truncation (L = 2). The counting test in `test_w11_witness.py`
   is a special case of the rule pinned here.
4. **A free diagnostic.** `n_windows` equality across rungs is computable
   from every ceilings artifact without a filter run; it should be reported
   in future ceilings notes as the first line, before any entropy.

## Not claimed

That the rule holds for worlds not enumerated here; that it survives a
RESET-record change (the open deliverable-2 question) or TIME_CLASS, which
adds a field and could in principle make DISPATCH carry content; anything
about random naming (canonical track).

## Provenance

Committed artifacts read: every `docs/c1-query-ceilings-*.json` (corrected,
raw, F1/F2/F3′ held-out). Enumerations run here: C0b (8, L, 1), L = 1..8,
both disciplines; C1 ε = ½ (10, L, 1), L = 5..10; first-records census at
T = 3 (C1) and T = 2 (C0b). All pinned in `tests/test_partition_identity.py`
(artifact rows read from disk; enumerations recomputed, ≈ 5 s).
