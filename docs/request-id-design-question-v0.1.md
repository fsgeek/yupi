# The lineage rung's cargo — request-id assignment, a design question (v0.1)

**v0.1 — 2026-08-15 (day seven).** Drafted by the day-seven instance in
response to Tony's correction that this question had been "flagged" twice
(c1-rung-separation-geometry-v0.1.md, Finding 3 and the (14,4,2) v0.3
block) with zero analysis and zero alternatives. Status: **design
question with a recommendation; decision owner Tony (cut/spec).** Not a
measured note — every number below is cited from the day-six notes.
Uncommitted at time of writing.

## What is measured (day six, two-path verified)

At WindowLaw(12,2,2) and (14,4,2), both ε: every r3→r4 split differs only
in lineage fields; the discriminating information is the in-window
IO_ISSUE's request id. Under lowest-free allocation (Part II §1, I4) a
visible id reveals whether another request was already in flight before
the window. Completion-only splits (the causal-matching channel r4 was
named for): **exactly zero** at both laws (121 splits at (14,4,2), all
issue-lineage). Deep-completion habitat (≥2 in flight): 0.05% (ε=1) /
0.002% (ε=1/2) at H=12; ≤0.25% at H=14.

## The bundle, unbundled — two separable facts

1. **The id scheme leaks.** Lowest-free ids are a channel about allocator
   state. At the measured laws this leak is 100% of the r3/r4 gap.
2. **The matching habitat is thin.** Multi-in-flight episodes are rare
   *regardless of id scheme*. Randomizing ids removes (1) and does
   nothing for (2): the result would be r4 ≈ r3 with nothing to carry.

Making causal matching *measurable* needs a workload/hazard lever
(IO-heavier programs, lower completion_p, or a wider device queue), not an
identifier lever. These are different decisions and should not travel
under one label.

## Statute and code touchpoints

- Part II I4: "lowest-free allocation from a pool of size R ≥ 2d" — law.
- Part II §9 witness ctrl-red references lowest-free semantics.
- Part I D3: per-episode identifier pools for threads, locks, devices —
  request ids not mentioned. D3's renaming layer is **not yet built**;
  no corpus exists.
- `kernel.py:_lowest_free_request_id`; `WorldConfig.req_pool` (C1: 4).

## Alternatives

**A. Keep lowest-free; relabel honestly.** r4 = "lineage, lowest-free
(allocator-leaking)". Record "the identifier is a channel" as a finding —
the same phenomenon D3 exists to prevent in entity naming, one level down
in the record schema. Cost: zero. Loss: r4 does not isolate matching, and
we say so.

**B. Extend D3 to request ids at the render layer.** State keeps a
canonical id; rendering applies a per-episode injection into a large
token pool. The exact posterior then needs an equality-pattern likelihood
over per-episode tokens (what an observed token tells you is which other
in-window tokens it equals, plus pool exclusion). **This machinery is
required for thread names anyway** (D3, Q5 held-out binding); done
together, request ids cost ~nothing extra. Done alone, it is new filter
and enumerator surface on both sides of the firewall.

**C. B plus a habitat lever** so matching has mass to carry. Touches
D6/D10 hazard audit and program shapes; changes throughput, not just
information (Part I v0.2.2 warns of exactly this).

**D. Diagnostic only** — measure r4 under both schemes at one law. Not
needed: the day-six decomposition already gives the leak share (100%) and
the matching share (0%) at the measured laws.

## Recommendation

A now; fold request ids into D3 when the renaming layer is built (B at
zero marginal cost); pull C only if Paper 1 wants a *matching* claim on
r4 — which the cut argues against (causal-matching-as-cargo is a
paper-2/3-shaped question; Paper 1's r4 can be "lineage field exposed"
with its measured cargo reported). Deadline for the decision: before
corpus generation. What needs Tony: only whether Paper 1 claims matching.
Everything else is implementation-time and rides on D3.

## What this note does not do

It does not change statute, code, or any measured number. If the
recommendation is taken, the concrete edits are: a one-line
relabel in the two day-six notes, and a D3 amendment ("identifier pools
apply to request ids") in Part I v0.3.

---

## v0.2 — 2026-08-15 (same session; Tony's ⅓-probability exploration)

Generated alternatives below the v0.1 floor, each ~⅓ as conventional as
the last, stopping at the first that changed the view (Tony's rule).
Sequence: (5) id scheme as a crossed interface factor — sharpens B, no
change; (6) hazard reshaping — rejected by Part I v0.2.2's throughput
audit, no change; (7) demote lineage from rung to query Q6 "which issue
does this completion match?" — writing out Q6's answer produced (8).

**(8) — the matching channel is structurally empty under I5, at every
rung, law, and habitat.** ACTOR is present at r1–r4 (`interfaces.py`);
I5 (Part II §1) allows at most one request in flight per thread;
IO_COMPLETE's ACTOR is the issuing thread (Part II §2). Hence every
completion is matched to its issue by ACTOR alone — including in the
deep-completion habitat, where the two in-flight requests belong to two
different threads. Consequences:

- The lineage field's only possible cargo in this world is allocator
  state (lowest-free) or nothing (random ids ⇒ r4 ≡ r3 exactly).
- v0.1's fact (2) is corrected: thickening the habitat (alternative C)
  cannot create matching cargo — it creates more allocator-leak splits.
  C is impossible as stated, not merely expensive.
- The day-six note's stated "structural reason" for the completion-
  matching zero (habitat thinness) is the wrong cause; the zero is
  I5 + always-visible ACTOR. Erratum line owed to
  `c1-rung-separation-geometry-v0.1.md` v0.3.
- Q3 ("which requests are outstanding, in what order") is thread-
  identified under I5.

Only two routes create a genuine matching channel: relax I5 (asynchronous
I/O, multiple outstanding per thread — Part II §2 world change; R ≥ 2d no
longer suffices) or mask ACTOR on completions (breaks the ladder's
monotone nesting). Both are cut territory and paper-2-shaped.

**Recommendation, sharpened not flipped:** A now, with r4 relabeled as
the *allocator rung* (that is its cargo here); B when D3 is built, at
which point r4 collapses into r3 and the ladder honestly has three
informational rungs plus a control; matching filed as "requires I5
relaxation," not "requires more habitat." What needs Tony: whether
Paper 1 wants a matching claim at all (recommendation: no).
