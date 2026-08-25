# D8 order-mode attribution — C0b reading note v0.1

> **Status (2026-08-25 11:33 PDT): measured under preregistration
> `d8-attribution-prereg-v0.1.md` (commit a39f555, stamped before any
> attribution quantity existed) and grid freeze
> `d8-attribution-grid-freeze-v0.1.md` (C0b, commit 31f0632, blind by
> cost). Artifact: `d8-attribution-c0b-2026-08-25.json` (1344 cells; raw
> append-only JSONL alongside), commit 48200e0 (stamped deb5ca8). Predictions
> scored by `scripts/check_predictions.py` on
> `d8-attribution-predictions-v0.1.json`. Truthsayer pass owed.
> Canonical-naming track (Part II v0.2.6 Clause 2′): nothing here is a
> random-naming ceiling. C1 is not measured yet (its benchmark is running;
> separate freeze).**

## 0. Headline, stated first

**In C0b the shuffled channel's loss is the allocator, and nothing else,
wherever it is large.** At $B = 3$, rungs r1–r3, every one of the 84 cells
is informative and **not** collapsed ($\Delta_{an}$ from 0.050 to 0.170
bits), and the loss is attributed to REQ (request identity — allocator
labels) with the chain order, the Shapley value, and the min/max envelope
all agreeing: **envelope width exactly 0 at every full-context $B = 3$ cell
— the attribution is order-independent there.** r4 (lineage exposed)
removes it: every full-context r4 cell is exactly zero. What survives at
$B = 2$, and at r4 under truncation, is real but tiny (≤ 0.0017 bits,
all collapsed under δ = 0.01) and lives in device-queue order (DQ) with
REQ and ρ perfectly redundant to it. Every structural zero held exactly.
One of two scorable predictions failed, on the generalization from
"from reset" to "truncated" — the week's error class, caught by the
checker this time rather than by a reviewer.

## 1. Gates (prereg §5) — all passed, uncapped

Two-path on **every** distinct observation of both channels: 731,258
shuffled observations and 406,014 ordered windows across the 1344 cells,
posterior AND law mass bit-for-bit (recursive filter vs. aggregated path
table under a literal permutation count). Gate F bijection on 56,384
distinct $(U, S_T)$. Full-coordinate identity (all-six subset entropy ==
joint entropy, same floats). Nonnegativity, chain-sum, Shapley-sum, and
envelope-containment identities in every cell (tolerance 1e-9 on fsum'd
floats). **Z1** (κ term ≡ 0 at ε = 1): exact 0 under every prefix in every
cell. **Z2** (WQ term ≡ 0 in C0b): exact 0 under every prefix in every
cell. **Z3** (B = 1 is the identity channel): all 968 B = 1 cells have every
loss exactly 0.0. Gate 6 recorded by construction + suite witness. Cost:
max support 7 states, max frontier 43, total gate-2 wall 1130 s; the run
took 5 min 21 s on 24 workers (11:22:32–11:27:53 PDT).

## 2. Predictions (prereg §6), scored as written

| | as written | verdict | reading |
|---|---|---|---|
| P1 | $\Delta_{an} > 0$ at C0b (6,6,3), r1–r3, both disciplines | **PASS** 6/6 | 0.170 (FIFO) / 0.120 (stochastic) bits, identical across r1–r3 |
| P1-mech | REQ-or-ρ share nonzero there | **PASS** | REQ = 100 % of the loss; ρ = 0 (split not predicted; now measured) |
| P2 | $\Delta = 0$ at every C0b r4 cell, $T_{ep} \le 8$, $B \in \{2,3\}$ | **FAIL** 4/36 | (8,2,2) r4, both disciplines: $\Delta_{un} \approx 0.0009$, $\Delta_{an} \approx 0.00045$ bits |
| P3a/P3b | C1 cells | NO_CHECK | no C1 artifact yet |
| P4 | — | NO_CHECK (as preregistered) | source condition below the grid |

**P2's failure, preserved.** The source test
(`test_c0b_shuffled_channel_is_null_at_r4_only`) is a from-reset,
full-context statement; I scoped P2 to "every C0b r4 cell with
$T_{ep} \le 8$", which includes truncated windows the test never examined.
The full-context r4 cells passed (all exactly 0, every $T_{ep}$). The
failing cells are one-bucket windows ($L = 2$) at (8,2,2); per-endpoint
attribution puts the whole gain on windows generated at $T = 8$ (offset
$u = 6$; 0.0018 bits there, 0 at $T \in \{2,4,6\}$). Under the semantic
chain the loss is 100 % DQ; under Shapley it is DQ/REQ/ρ = 0.00015 each, and
DQ's envelope is $[0, 0.00045]$ — the three coordinates are **perfectly
redundant** at these cells (any one of them resolves the ambiguity, so
whichever comes first in the order takes it). The chain-order narrative is
exactly what the prereg said it was: one predeclared story, reported next
to the order-free values. The mechanism (which records the bucket holds) is
not identified here and is **not** asserted.

## 3. What the channel hides in C0b, by cell class

- **$B = 1$ (968 cells):** exactly nothing — Z3.
- **$B = 3$, r1–r3 (84 cells): all informative, none collapsed.** Full-context
  $\Delta_{an}$: FIFO 0.170 / 0.147 / 0.118 / 0.096 and stochastic
  0.120 / 0.104 / 0.083 / 0.068 at $T_{ep}$ = 6 / 9 / 12 / 15 — falling
  with horizon (the absorbing-IDLE tail dilutes the law mass, as in the D10
  verdict). REQ share = 1.000 and envelope width 0 at every $L \ge 2B$; at
  the one-bucket truncation $L = 3$ the REQ share drops to 0.968–0.984 with
  envelope width ≤ 0.0019, i.e. a small DQ/ρ-redundant component appears
  only when the window is a single bucket. Prevalence (exact law mass of
  informative observations) from 10/81 to 1,783,582/7,971,615; max per-
  observation gain 0.985 bits at FIFO (6,3,3). **r1, r2, and r3 are
  identical to every stored digit in all 672 cell-pairs** — the ACTOR /
  OBJECT / RELATED masking of the lower rungs does not move the D8 loss in
  this world; only LINEAGE does.
- **$B = 3$, r4 (28 cells):** 12 informative, all collapsed (≤ 0.0017 bits),
  DQ-dominated; every full-context cell exactly 0.
- **$B = 2$ (264 cells):** 120 informative, all collapsed ($\Delta_{an}
  \le 0.0006$); dominant coordinate DQ or REQ, with a single ρ-dominant cell
  at stochastic r1–r3. The allocator bucket barely fits a $B = 2$ window in
  this world.
- **Offset term** $I(U; O_{ord} \mid O_{shuf})$: positive in 141 cells —
  120 at $B = 2$ (max 0.00059 bits) and 21 at $B = 3$ (max 0.000037 bits,
  only at the truncated windows $(12,3)$, $(15,3)$, $(15,6)$); **exactly 0.0
  at every full-context $B = 3$ cell and at every $B = 3$ cell with
  $T_{ep} \le 9$.** (A first draft of this note said "exactly 0 at every
  $B = 3$ cell"; the pre-write check refuted it — see §5.) **No cell has
  $\Delta_{an} = 0$ with a positive offset term**: the "order hides only
  window placement" row of the prereg's reading table is empty in C0b.

## 4. What this does and does not say

- It says the D8 manipulation is, in C0b, a clean allocator-label eraser at
  $B = 3$, with an order-independent attribution — the cleanest single-
  coordinate result the instrument has produced. It does not say anything
  about C1, where WQ (lock wait-queue order) and κ (ε < 1) become live and
  where the D8 note's coarse-rung allocator bucket needs $H \ge 12$.
- "Collapsed" and "informative" are different words (D10 verdict): 216 of
  1344 cells are informative; 84 are not collapsed. Numbers below δ are
  reported as measured, not rounded to zero.
- The chain-order attribution is one story; where coordinates are
  redundant it is order-dependent by construction, and the envelope says
  so. Nothing in §3 relies on the chain order except the sentence that
  names it.

## 5. Deviations and provenance

- Benchmark output files were created under a 2026-08-24 date by the
  instance (session crossed midnight); renamed to 2026-08-25 before commit.
- The stage-A benchmark refusal (estimate-before-visible-table) was added
  after C0b was fully priced under stage-B code; it affects only the C1
  benchmark. The field was first named a "lower bound" and renamed an
  "estimate" when a test showed the timing samples do not order.
- **Mislabeled commit a51613a (stamped d588032).** The first attempt to
  write this note ran an exact-claim check before writing; the check
  failed on two sentences (the offset-term claims above), the note was
  not written, but the commit step in the same command ran anyway and
  committed a 29-record snapshot of the *in-progress* C1 benchmark JSONL
  under a message describing this note. That commit's message is wrong;
  its content is harmless (append-only cost records, superseded by later
  commits of the same file). Recorded here and in the corrective commit's
  message; history not rewritten (the stamp stands).
- The measurement runner refuses cells outside the freeze; the C1 candidate
  cells were listed as "not in freeze, NOT run" in its log.
- Predictions were checked by the script, not by recollection; P2's failure
  was found by the checker's first run on the artifact.
