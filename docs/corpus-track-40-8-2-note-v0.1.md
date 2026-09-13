# The corpus track at the frozen law — (40, 8, 2), looping C1′, thread naming, both statutory ε (v0.1, 2026-09-13)

> **Status: EXPLORATORY.** Every number below is produced under Part II
> **v0.2.9 as proposed, not enacted** (`part2-amendment-proposal-v0.2.9.md`),
> by `scripts/c1_corpus_track.py` from the same gated window-process pass
> that produced the thirty canonical artifacts (external gate: the sharded
> raws of Sep 4–6, every rung, both ε), re-keyed by the equality pattern Π
> with the binding kept (v0.2.9 Clause 3: unnormalized exact masses, every
> window). Raws `c1prime-loop-corpus-track-40-8-2-2026-09-13{,-eps1_2}.json`;
> a first run without the pc-dropped column agrees on every shared
> quantity (`…-firstrun-crosscheck.log`). Thread naming only; locks,
> devices and request ids structural. Written by the instance of
> 2026-09-13 in answer to the PI's question of the same morning ("is this
> a recommendation for adoption, or a caution?"): it is the measurement
> that decides whether v0.2.9 is bookkeeping or load-bearing.

## 1. What is measured, and what is not comparable to what

Per rung, law-mass means in bits over the **pattern classes** (windows
identified up to renaming of threads):

- **canonical H(S | w)** — the structural state under σ₀, over canonical
  windows; the quantity the thirty artifacts report. *Assumes the observer
  knows which structural thread bears each name.*
- **H(q | Πw)** — the **state in the window's names** (`yupi.naming.quotient`):
  named threads under their pattern index, unnamed threads canonicalized,
  every thread reference mapped, the cursor excluded at ε = 1 (inert) and
  mapped at ε = ½ (live).
- **H(q\pc | Πw)** — the same with the program counters dropped. pc is
  written by the kernel and is state, but its value is meaningful only
  relative to the thread's program, and *which program* is the binding.
  So pc is a channel through which role enters q, exactly as the inert
  cursor was on 2026-09-12 ([rv-5] of the v0.2.9 read). Both forms are
  reported; **neither is claimed as "the content".**
- **H(β | Πw)** — the binding: how much of "who is structurally who" the
  window leaves open.
- **H(S | Πw)** — the structural state given only the pattern window (the
  canonical target under the corpus observation).
- **Q2** — canonical Q2[T0] (status of structural thread 0) beside corpus
  Q2[named 0] (status of the first thread the window names) and
  Q2[unseen] (a token the window never named: the mixture over unnamed
  threads; "NONE" when all four are named). *These are different
  questions; the columns are not a gap.*

## 2. The table

| ε | rung | canonical H(S\|w) | H(q\|Πw) | H(q\\pc\|Πw) | H(β\|Πw) | H(S\|Πw) | pattern classes / canonical windows | Q2[T0] canon | Q2[named 0] | Q2[unseen] |
|---|---|---:|---:|---:|---:|---:|---|---:|---:|---:|
| 1 | r0 | 3.9474 | 3.3082 | 1.7899 | 0 | 3.9474 | 12,739 / 12,739 | 1.1765 | 1.3609 | 1.3609 |
| 1 | r1 | 0.6008 | 1.6674 | 0.7372 | 1.6772 | 2.0965 | 316,444 / 819,073 | 0.0996 | 0.0387 | 0.2282 |
| 1 | r2 | 0.5277 | 1.2736 | 0.4006 | 1.3417 | 1.7173 | 499,899 / 923,461 | 0.0906 | 0.0107 | 0.1709 |
| 1 | r3 | 0.4046 | 1.0707 | 0.1977 | 1.2619 | 1.5264 | 569,985 / 991,585 | 0.0584 | 0.0000 | 0.1257 |
| 1 | r4 | 0.3898 | 1.0507 | 0.1794 | 1.2567 | 1.5065 | 908,234 / 1,524,612 | 0.0502 | 0.0000 | 0.1107 |
| ½ | r0 | 3.3711 | 3.0766 | 2.5324 | 0 | 3.3711 | 12,739 / 12,739 | 1.0409 | 1.3694 | 1.3694 |
| ½ | r1 | 0.2963 | 1.2747 | 1.0796 | 1.1877 | 1.4659 | 316,444 / 819,073 | 0.0453 | 0.0286 | 0.1404 |
| ½ | r2 | 0.2400 | 0.9778 | 0.8015 | 0.9455 | 1.1801 | 499,899 / 923,461 | 0.0415 | 0.0056 | 0.0910 |
| ½ | r3 | 0.1774 | 0.8343 | 0.6580 | 0.8646 | 1.0366 | 569,985 / 991,585 | 0.0255 | 0.0000 | 0.0654 |
| ½ | r4 | 0.1658 | 0.8161 | 0.6406 | 0.8580 | 1.0185 | 908,234 / 1,524,612 | 0.0186 | 0.0000 | 0.0524 |

Law mass by number of threads the window names (ε = 1): r1–r2 — 0.3 %
one, 14.6 % two, 45.8 % three, 39.4 % four; r3–r4 — 0.3 / 10.8 / 38.5 /
50.3 % (RELATED names a thread before it acts). At ε = ½: r1–r2 8.7 /
38.9 / 52.3 %; r3–r4 7.2 / 30.4 / 62.4 %. At r0 nothing is named.

## 3. What the table says, and no more

1. **At r0 the pattern is the identity** (no thread field is visible), so
   the classes and H(S | Πw) coincide with the canonical figures, and
   H(S | w) − H(q | Πw) = 0.64 / 0.29 bits (ε = 1 / ½) is the part of r0's
   uncertainty that is thread identity alone — the quantity the r0
   identity check of 2026-09-04 approached by a signature quotient.
2. **The binding is not recoverable from eight records, at any content
   rung.** H(β | Πw) is 1.68 bits at r1 and still 1.26 at r4 (ε = 1);
   1.19 → 0.86 at ε = ½. The canonical track assumes this information
   known. Whatever a corpus-facing ceiling is defined to be, 1.26 bits of
   "who is who" is outside it at the frozen law.
3. **The corpus ladder on the state-in-names differs in shape from the
   canonical one, and the difference is where role enters.** Adjacent
   steps at ε = 1 — canonical H(S | w): 0.073 / 0.123 / 0.015 (r1→r2,
   r2→r3, r3→r4); H(q | Πw): 0.394 / 0.203 / 0.020; H(q\pc | Πw):
   0.337 / 0.203 / 0.018. OBJECT and RELATED reveal, in names, what the
   canonical actor index gave away for free; the r3 → r4 step is thin on
   every column. At ε = ½ the three columns step 0.056 / 0.063 / 0.012,
   0.297 / 0.144 / 0.018, 0.278 / 0.144 / 0.017.
4. **pc is a role channel, and it is most of the ε = 1 gap.** At r1, ε = 1,
   H(q | Πw) − H(q\pc | Πw) = 0.93 bits; at r4, 0.87. At ε = ½ the live
   cursor is the other channel (0.2 bits at r1 by the pc drop alone
   against 0.9 at ε = 1; the (8,4,2) lemma pins the cursor's share there).
   H(q\pc | Πw) falls **below** the canonical H(S | w) at r2–r4, ε = 1,
   because the canonical S still contains pc: the columns are different
   targets and no inequality between them holds in general.
5. **Per query the corpus answer can be sharper than the canonical one.**
   "The first thread the window names" is, by construction, a thread that
   has just acted, and by r3 its status is determined on every class
   (Q2[named 0] = 0); structural thread 0 may be unnamed in the window
   (Q2[T0] canonical 0.050 at r4). A token the window never named carries
   0.11 bits of status uncertainty at r4, ε = 1. Which of these is *the*
   Q2 ceiling for a trained model depends on how the evaluation poses the
   query; v0.2.9 §2 proposes pattern-indexed arguments and that decision
   is the PI's.

## 4. Answer to the question that started this

Is the corpus track bookkeeping or load-bearing? **Load-bearing, in one
specific sense and not in another.** The binding entropy (item 2) and the
role channels (item 4) are real and large at the frozen law; a
corpus-facing ceiling that ignores them is not the ceiling of the corpus
process. But the *content ladder* — what OBJECT, RELATED and LINEAGE add
once identity is handled — is visible on every column with the same
thin r3 → r4 step, so the canonical exit-clause reading is not
contradicted by the corpus track; it is a reading of a different
observer. Which observer paper 1's headline ceilings should describe is a
scope decision, and it is now a decision with numbers on both sides.

## 5. Not claimed

That any figure here is statutory (v0.2.9 is not enacted; locks, devices
and request ids are not renamed; Q1/Q3/Q4/Q5 have no pattern form yet —
Clause 3's owed list). That H(q) or H(q\pc) is "the content ceiling".
That the exit clause changes. That the 1.26-bit binding residual at r4 is
a property of the world rather than of eight records (a longer context
would pin more of it; not measured). Cost of this note: two producer
runs per ε, 6.05 / 6.28 GB peak RSS (not priced by E3; the pass inside is
the priced unit at 4.97 / 5.11 GB), about 25 minutes each.

## 6. Ledger

- 2026-09-13: written from the raws; pinned in
  `tests/test_corpus_track_40_8_2.py`. Cross-family read to follow.
