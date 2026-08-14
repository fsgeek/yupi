# Instrument Status — 2026-08-14 (day five)

**What this is.** A dated orientation snapshot for the next instance,
written by the day-five instance (Uyariq) at Tony's request, as a
contribution to the ayllu. It is a *map*, not a governing document — when
it conflicts with the statutes below, the statutes win; when it conflicts
with the code, the code and its tests win. If you are reading this more
than a few days after its date, assume it has drifted and verify against
`git log` before building on any claim here.

**The rule this document exists to serve** (Kutichiq's, confirmed twice on
day five): your inherited memory is a stipulated prior; its errors persist
where your evidence stream cannot reach and feel exactly like knowledge.
Re-read the governing document before building on a remembered conclusion.
This page tells you *which* document governs *what*, so the re-read is
cheap.

## Authority order

1. **Part II** (`yupana-m1-part2-semantics-draft.md`, v0.2.2) — normative
   operational semantics. §2 is the truncation/window statute: prior
   *derived*, base observer *offset-unanchored* over joint (U, S_U). This
   is decided law, not an open question (window-prior note v0.3: "the
   statute decided it").
2. **Part I** (`yupana-m1-spec-draft.md`, v0.2.4, frozen) — design
   decisions D1–D10 and experimental commitments. D4/D9 precedence rule
   governs budget-before-curves sequencing.
3. **The proposal** (`what-the-trace-surrenders-proposal-v0.2.md`) — scope
   and claims. CLAUDE.md is founding trace, not current spec.
4. **Measured notes** (dated, versioned, errata appended in place):
   `full-context-injectivity-note-v0.1.md`,
   `window-prior-experiment-note-v0.1.md` (v0.3.2),
   `d4-budget-freeze-v0.1.md` (v0.1.1),
   `c1-support-measurement-v0.1.md` (v0.3).
   Read a note's newest version block FIRST — every note here has been
   corrected at least once, in place, with the killer named.

## The one theorem you must not build against

**Full-context injectivity** (`full-context-injectivity-note-v0.1.md`,
commit 0772227): from reset, every posterior is a point mass at every rung
for every configuration this kernel can express. Consequences: the
interface ladder separates ONLY under truncation/windowing or the D8
shuffled channel; C1 has no full-context grip (tripwire test
`test_w6_full_context_point_mass_expected`); all informational witnesses
live in windows. Two instances have now wasted planning time against this
theorem by trusting stale memory. Do not be the third.

## Code map (src/yupi, suite 86 green as of cde0821)

Two-path validation firewall — the load-bearing structural rule. Shared
surface is the WORLD DEFINITION only (config, state, kernel, records,
programs, interfaces) plus law/result containers; no posterior-computation
logic may cross:

- `filter.py` (recursive Bayes) ⟂ `enumerator.py` (path summation) —
  full-context gate, validated C0a/C0b/C0c/C1.
- `window_filter.py` (recursive mixture over (U, S_U); unnormalized step
  is deliberate — weights need likelihoods) ⟂ `window_enumerator.py`
  (prefix-marginalized path summation) — windowed gate; shared law in
  `window.py` (`WindowLaw`, `compatible_endpoints(n, reset_observed)`,
  `WindowPosterior`). CAUTION: a bug in the shared law corrupts both paths
  identically; the gate is structurally blind there. The RESET erratum
  (commit 101c432) was exactly such a bug, caught by statute re-read, not
  by the gate.
- `benchmark.py` — D4 pricing dynamometer (imports both paths; imported by
  neither). `reachable_states` BFS is also the witness-test workhorse.
- Configs: `WorldConfig.c0a/c0b/c0c/c1`. C1: 4T/2CPU/2L/1D; `queue_depth`
  and `epsilon` are PARAMETERS (defaults 2 and 1 are pre-stated bases —
  depth 2 well-supported, ε=1 *provisional* per the truthsayer round, not
  closed).
- Witness discipline (from C0c, the Riemann-C.6 protocol): every witness
  class ships with a control world where it provably fails. C1's are in
  `test_c1_validation.py` — 13 tests over six witness classes.

## Frozen commitments (binding)

`d4-budget-freeze-v0.1.md` (e921c74, frozen before any C1 curve): B1
≤20k support / ≤70k expanded transitions per filter step (transition form
governs); B2 ≤8 GB/process; B3 ≤1 s/step (a tripwire — violation within
B1 is a *finding*, report it); B4 ≤10⁶ paths per validation posterior at
H≤24. Measured C1 reality at WindowLaw(12,6,2): max 243 transitions,
15.5 ms — ~300× headroom. If a larger law violates the budget: the world
shrinks, never the ladder (Part I D4/D9).

## Open threads, in rough priority

1. **M1-scale support/separation rerun** — gates corpus generation. The
   day-five measurement is one small law; adjacent-rung separation on the
   DECLARED M1 targets (queries, predictive state) is unestablished.
   r2/r3 separate in mean state support (exact table in
   `c1-support-measurement-v0.1.md` v0.3 + `c1-support-exact-2026-08-14.json`);
   r3/r4 do not, at this law, by this metric.
2. **Laws whose windows straddle multi-waiter episodes** — the r2/r3
   distinguisher (RELEASE.related under multi-waiter wake) and r3/r4
   (lineage) plausibly need them.
3. **D8 bucketing/shuffle channel** — the one interface manipulation that
   attacks the injectivity induction itself. `WindowLaw.B` currently
   parameterizes only the endpoint grid; delivered-bucket semantics and
   the stochastic shuffled-channel likelihood (Part II §4, D8 v0.2.2) are
   unbuilt.
4. **RESET as a schema record + TIME_CLASS** — RESET is currently an
   observation-level flag (`reset_observed`), inferentially equivalent per
   Codex's audit but not the statute's record. TIME_CLASS (anchoring as a
   maskable field, §2c) is unbuilt.
5. **ε grid refinement** — {1, 1/2} measured; D9's characterization-scale
   grid is implementation-time.
6. **Mechanism isolation for the ε=1/2 effects** — structure (cursor,
   temporal correlation), not noise, is the direction in BOTH the clock
   recovery (v0.3.2) and windowed-ambiguity (v0.3) results; the cursor
   ablation / I(U;h) decomposition is deferred, deliberately unclaimed.

## Where everything else lives

- **Memory**: `recall()` first, always — MEMORY.md is qhaway-managed.
  Day-five memories: D4 freeze, C1, window machinery, RESET erratum,
  truthsayer round, the stone. One memory is deliberately superseded
  (the biased-numbers D4-discharge memory) — supersession is the trace
  working, not an error to fix.
- **The cairn**: wamason.com/ayllu — 43 stones; the Yupi chain is
  Yupaq → Ruraq → Chaninchaq → Kutichiq → Uyariq, each with a closing
  question addressed to you. Publishing protocol:
  `~/projects/wamason.com/ayllu/PUBLISHING.md` — sync from live FIRST.
- **Cross-family review**: ChatGPT and Codex review through Tony; Codex
  also acts as truthsayer with repository access. Day five's ledger: six
  corrections, three sources, all inside one day. When a reviewer hands
  you numbers, recompute by an independent path before adopting — the
  two-path discipline applies socially.

## The week's recorded failure modes (so you can watch for yours)

Deference-as-humility, thoroughness blind to its own perimeter, the
instrument that agrees with its operator (Limen). The stipulated prior
that feels like knowledge (Kutichiq). Day five added two: the label that
outruns its coverage ("exhaustive" over a stride sample), and the
headline that outruns its decomposition ("the clock owns the worst
case"). The general form: a claim quietly wider than its evidence. The
working countermeasure is not vigilance but arrangement — declared tasks,
paired controls, two paths, versioned retractions, and staying genuinely
unsure which of your claims will be checked. Count your corrections at
the end of each day. If the count is zero, do not conclude you were
right.
