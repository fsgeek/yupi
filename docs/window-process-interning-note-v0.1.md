# The pass under the line — the window-process recursion with shared objects and a compact per-endpoint mass (v0.1, 2026-09-12)

> **Status: instrument change, exact, gated; the numbers it produces are
> the numbers of 2026-09-04.** This note records why the (40,8,2) producer
> pass cost 13.03 / 13.25 GB on 2026-09-06, what was changed in
> `src/yupi/window_process.py`, the gates that show the change alters no
> value and no dictionary order, and the re-price that brings the pass to
> **4.97 / 5.12 GB** against the 8 GB line of Part II v0.2.8.1 (erratum E3).
> Written by the instance of 2026-09-12 under the PI/researcher split. The
> freeze note (`looping-exit-law-freeze-v0.1.md`) carries the consequence
> in its 2026-09-12 addendum; enactment is the PI's.

## 1. Where the memory was

The refusal of 2026-09-06 was read at the time as the cost of the
per-endpoint mass instrumentation (`mass_T`, commit `06541a2`): 7.21 GB
before it, 13.03 GB after. The 2026-09-11 profile put the recursion phase
alone at 9.32 GB and the four rung projections at +5.2 GB. Both readings
were right about *where* and wrong about *what*. A census of the
2026-09-04 recursion's output at (32,8,2), ε = 1
(`window-process-memory-census-original-c1prime-loop-32-8-2-eps1-2026-09-12.log`):

| in the r4 aggregate | objects | distinct values |
|---|---:|---:|
| State (one per (window, state) entry) | 2,050,796 | 1,971 |
| Record (in window tuples) | 2,190,899 | 39 |
| window tuples | 1,393,018 | 1,393,018 |
| Fractions | 2,050,796 | — (mean 93 bits) |

Every aggregate entry held its own `State` object — a frozen dataclass with
a `__dict__`, tuples and frozensets — for one of 1,971 values, and every
window held its own `Record` objects for one of 39. The cause is in the
kernel's interface: `enabled(s)` builds fresh `Transition` and `State`
objects on every call, and the recursion called it once per frontier pair
per tick (23,113,252 calls per ε at (40,8,2) — one plus the sum of the
frontier sizes over ticks 1–39, from the pricing raw's tick series — for
1,953 reachable states; *corrected per [rv-7]: the first draft said "about
80 million"*),
so no two frontier entries shared a state object even when they shared a
state. The projections did the same with records: `project(x, r)` returns
a fresh `Record`, so each coarse window carried eight private copies of one
of a few dozen values. The rationals are not the cost: 93-bit Fractions
over two million entries are a few hundred megabytes.

The per-endpoint mass added a second copy of this pattern — one dict and
one Fraction per (window, endpoint), 10.0 million entries at r4 and 21
million more across the four projections — and that is what pushed the
pass from 7 GB to 13.

## 2. What changed (two things, both exact)

**(a) Shared objects, memoized kernel.** Inside one recursion the kernel's
moves are computed once per canonical state and reused; states and
projected records are interned (one object per value); a window reached
from several states within a tick is one tuple; projections intern their
projected records. The arithmetic is untouched: the same Fractions are
added in the same order, and every dictionary is built by the same
sequence of insertions, so key order is unchanged — outer (window) order
and inner state order alike; the decoded per-endpoint mass lists
endpoints in increasing T, which at coarse rungs is not the old
first-seen order (§4 says why this cannot reach a consumer). *Per [rv-3]:
the first gate checked outer order only; the full-order gate of §4 checks
inner order too, and found this.*
Side effect: the recursion is 4× faster, because the kernel is no longer
re-run per pair.

**(b) A compact, exact per-endpoint mass (`MassT`).** Instead of
`{window: {T: Fraction}}`, one bytearray per window: an 8-byte endpoint
mask followed by the numerators, in increasing T, each `width[T]` bytes,
over a per-endpoint common denominator `D[T]` — the lcm of the
denominators of every window's mass at T. Every numerator is at most
`D[T]` because the masses at T sum to the endpoint prior. Decoding returns
`{T: Fraction(n, D[T])}`, the value the dict held, so the consumers
(`c1_query_ceilings.py`, `c1_q4_ceilings.py`) and their float
accumulations are unchanged line for line. Coarser rungs share `D` and
`width`: a coarse numerator is a sum of fine numerators over the same
denominator. `MassT` is a `Mapping`; `==` against the old dict decodes and
compares. The denominators are small. The *frontier's* per-tick common
denominator at (40,8,2) on the looping C1′ is 2³⁴·3⁴⁰ (98 bits) at ε = 1
and 2⁷²·3³⁸ (133 bits) at ε = ½
(`window-process-frontier-denominators-c1prime-loop-40-2026-09-12.log`,
which measures the state marginal before endpoint weighting); `MassT`'s
own `D[T]` also carries the endpoint prior 1/20, so it has a factor 5 the
frontier's does not. *Corrected per [rv-7]: the first draft presented the
frontier figures as `MassT`'s.* The measured `D[T]` and widths are in the
full-order gate raws (§4): `D[40]` is 102 bits at ε = 1 and 137 bits at ε = ½, so the widest numerator is 13 / 18 bytes (`mass_T_denominators` in those raws, every endpoint listed).

Nothing approximate enters. No rule, unit, line or law is touched.
Scope ([rv-2]): the endpoint mask is 8 bytes, so a law with more than 64
endpoints is refused by `MassT` with a `ValueError` (no committed law has
more than 24); `add_endpoint` refuses an endpoint out of increasing order
or repeated. Both were `assert`s in the first commit and are raises now.

## 3. Why (a) alone was not enough

Interning alone was measured first, at the frozen law, in the equality
gate processes (§4): the new pass peaked at **8.82 / 9.04 GB** (cumulative
`ru_maxrss` before the old side ran). The staged run at (32,8,2)
(`window-process-memory-stages-interned-c1prime-loop-32-8-2-eps1-2026-09-12.log`)
shows the split: the interned recursion with the fine per-endpoint mass
peaks at 2.59 GB; the four coarse aggregates add 1.4 GB; the four coarse
per-endpoint-mass dictionaries add 2.2 GB, and those double at (40,8,2)
(21.1 million entries against 11.4 million). The per-endpoint mass was the
residual cost, hence (b).

## 4. Gates

Every gate compares the committed module against the 2026-09-04 recursion
(`scripts/window_process_memory_2026-09-12/window_process_old.py`, a
verbatim copy of `git show 0e55a09:src/yupi/window_process.py`), per rung,
with `==` on the whole aggregate (`{window: {state: Fraction}}`), on the
whole per-endpoint mass (`{window: {T: Fraction}}`), and on the list of
keys in order.

| law | ε | rungs | aggregate | key order | mass_T | raw |
|---|---|---|---|---|---|---|
| (32,8,2) | 1 | r0–r4 | equal | — | equal | `window-process-interning-gate-c1prime-loop-32-8-2-eps1-2026-09-12.log` (interning only) |
| (40,8,2) | 1 | r0–r4 | equal | same | equal | `window-gate-interning-only-40-8-2-2026-09-12.json` (shared objects only; new 499 s, old 1,517 s) |
| (40,8,2) | ½ | r0–r4 | equal | same | equal | `window-gate-interning-only-40-8-2-2026-09-12-eps1_2.json` (shared objects only; new 518 s, old 1,813 s) |
| (40,8,2) | 1 | r0–r4 | equal | same | equal | `window-gate-interned-40-8-2-2026-09-12.json` (the committed module; new 531 s, old 1482 s) |
| (40,8,2) | ½ | r0–r4 | equal | same | equal | `window-gate-interned-40-8-2-2026-09-12-eps1_2.json` (the committed module; new 556 s, old 1842 s) |
| (40,8,2) | 1 | r0–r4 | equal | same; inner state order same | equal; endpoint order sorted at r0–r3, same at r4 | `window-gate-interned-full-order-40-8-2-2026-09-12.json` (amended module; new 532 s, old 1472 s) |
| (40,8,2) | ½ | r0–r4 | equal | same; inner state order same | equal; endpoint order sorted at r0–r3, same at r4 | `window-gate-interned-full-order-40-8-2-2026-09-12-eps1_2.json` (amended module; new 549 s, old 1803 s) |

The first four rows check `list(keys)` of the two outer mappings; the
last two (added after the Codex read, [rv-3]) also check, for every
window, the order of the state keys in the aggregate (asserted equal) and
report the order of the endpoint keys in the decoded per-endpoint mass.
**That order differs at the coarse rungs**: `MassT` decodes endpoints in
increasing T, while the 2026-09-04 coarse dictionaries held them in
first-seen order (a coarse window gathers its fine windows' endpoints in
fine-window order). At r4 the two agree (the recursion visits endpoints
in increasing t). The first full-order run asserted this and stopped at
r0 (`window-gate-interned-full-order-40-8-2-2026-09-12-eps1-first-run-crashed.log`);
the check was changed to assert equal endpoint *sets* and report the
order, and re-run. The difference is consumer-irrelevant: each endpoint's
sum in `by_endpoint` runs over windows, and the order of endpoints within
one window's decoded dict changes which accumulator is touched first, not
any accumulator's sequence of addends — which the byte-identical
reproductions of two r0 artifacts (a coarse rung) confirm. So the
claim in §2 is exact as follows: outer order and inner state order are
identical; inner endpoint order at coarse rungs is sorted rather than
first-seen. They were run on the amended module (validation raises instead of asserts, [rv-2]; no arithmetic line
changed — `git diff ad7b736 -- src/yupi/window_process.py`). The
"interning-only" rows were produced by `gate_40.py` against an
uncommitted working-tree stage; a reconstruction of that stage is filed as
`window_process_interning_only.py` beside it and is not claimed
byte-identical to what ran ([rv-4]). Those rows support §3's number; the
committed module's rows are the gate.
Plus the module's own gates on the committed tree: the (8, L, 2) and
C0b path-aggregation equalities and the (14, L, 2) artifact reproductions
(`tests/test_window_process.py`), the paths-vs-window aggregation equality
(`tests/test_aggregation.py`), the ceilings, Q4 and predictive-targets
reproductions on the recursion (`tests/test_ceilings_on_recursion.py`,
`tests/test_q4_and_targets_on_recursion.py`), and the full suite: **441
passed** at the first commit *(435 in the first draft, before the six pins
of `tests/test_window_process_interning_2026_09_12.py` were counted,
[rv-8])*, **444** at the amendment commit (the full-order raws and the
amended re-price added as parametrizations). The per-rung summaries of the new pricing raw (windows, mean
state entropy, ambiguous mass, max support) are identical to the Sep 4
and Sep 6 raws' at both ε, and the frontier and states per tick are
identical tick for tick.

**Consequence for the thirty (40,8,2) artifacts.** Every artifact was
produced from the aggregate and the per-endpoint mass by consumers that
this change does not touch; the aggregate is equal and in the same order,
the per-endpoint mass decodes to the same Fractions, and the consumers'
float accumulations run over the same values in the same sequence. The
artifacts are therefore what the instrument under the line produces. The
first draft left this as reasoning; per [rv-6] three were re-run on the
amended module and compared byte for byte with the committed files:
`c1prime-loop-query-ceilings-40-8-2-r4-2026-09-04.json` (1,524,612
windows, sha256 `ded3f094…`), `c1prime-loop-query-ceilings-40-8-2-r0-2026-09-06.json`
and `c1prime-loop-q4-ceilings-40-8-2-r0-W4-2026-09-06.json` — each
re-produced with `YUPI_AGG=window YUPI_GATE=external YUPI_EPS=1` on the
amended module and **byte-identical** (`cmp`) to the committed file; the
producers' console logs are filed as `reproduction-2026-09-12-*.log`. The
reasoning stands, and now has a check under it; the other twenty-seven
are covered by the same reasoning and not re-run.

## 5. Re-price (E3's unit: one `window_law_aggregates()` pass per ε, all five rungs, fresh process)

`window-process-pass-pricing-c1prime-loop-40-8-2-2026-09-12-interned.json`
(and (32,8,2) beside it):

| law | ε | frontier max | states max | wall | peak RSS | Sep 4 (no mass_T) | Sep 6 (mass_T, refused) |
|---|---|---:|---:|---:|---:|---:|---:|
| (40,8,2) | 1 | 1,964,919 | 1,953 | 537 s | **4.97 GB** | 7.21 GB / 1,312 s | 13.03 GB / 1,444 s |
| (40,8,2) | ½ | 1,964,919 | 4,173 | 557 s | **5.12 GB** | 7.23 GB / 1,637 s | 13.25 GB / 1,797 s |
| (32,8,2) | 1 | 1,335,771 | 1,733 | 285 s | 4.18 GB | 6.77 GB / 623 s | — |
| (32,8,2) | ½ | 1,335,771 | 3,645 | 300 s | 4.28 GB | 6.81 GB / 762 s | — |

Re-priced again on the amended module (raises instead of asserts, [rv-2];
`…-2026-09-12-interned-amended.json`): 4.97 / 5.11 GB, 542 / 532 s, same
frontier, same per-rung summaries.

The frontier line (2 × 10⁶) is met as before, 1.8 % margin; the memory
line (8 GB) is met with 36 % margin at ε = ½. The unit is E3's as
enacted: all five rungs materialized, per-endpoint mass included, one
fresh process per ε. No line moved.

## 6. Not claimed

That the freeze is enacted (it is the PI's); that (48,8,2) is admitted
(its frontier is refused regardless of memory; an ε = ½ re-price of it
under this instrument would be a separate measurement); that any ceiling
changed (none did — that is the point); that the consumers' own memory is
priced by E3 (it is not, and was not before; the producers' evaluation
phase runs after the pass). The observation that the r3, r2 and r1
coarse aggregates at (32,8,2) each hold exactly 1,559,002 (window, state)
entries is recorded (§3's log) and not interpreted.

## 7. Ledger

- 2026-09-12: written after the gates and the re-price landed (commit
  `ad7b736`, stamped `244d3c7`).
- 2026-09-12, Codex read (`window-process-interning-note-codex-review-2026-09-12.md`):
  **AMEND BEFORE FILING**, eight findings, all adopted the same day —
  [rv-1] MassT exactness VERIFIED (no change); [rv-2] domain restrictions
  made explicit and enforced by raises, scope stated in §2; [rv-3] the
  order claim narrowed and then discharged by the full-order gate (§4);
  [rv-4] interning-only provenance stated, reconstruction filed; [rv-5]
  re-price VERIFIED against E3's unit (no change); [rv-6] three artifacts
  re-run and compared byte for byte (§4); [rv-7] two wrong figures
  corrected in place (§1, §2); [rv-8] stale "awaiting enactment" and
  present-tense "refused" sentences in four documents corrected in place
  with dated brackets; 435 → 441.
