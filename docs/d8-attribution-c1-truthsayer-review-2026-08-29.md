# D8 attribution C1 truthsayer review — 2026-08-29

> **Status: independent review of `docs/d8-attribution-c1-note-v0.1.md`
> §§0–6 at repository head `aa6ad4b`.** This artifact was written by the
> Codex instance asked to perform the outstanding truthsayer pass. It is a
> review, not a governing document, and is deliberately left uncommitted for
> Tony and the authoring Claude instance to inspect. No measurement artifact,
> code, threshold, witness status, or evidence-map entry is changed here.

## Verdict

**P3b survives the pass.** The v0.3 measurement supports the note's central
cross-world statement: at C1 `(T_ep,L,B) = (12,12,2)`, `epsilon = 1`, r1–r3
have positive anchored and unanchored loss, the loss is entirely in REQ under
the anchored semantic chain, Shapley value, and envelope, and r4 removes it
exactly. The unanchored attribution agrees to the stored float tolerance and
has an exactly zero offset term.
The effect is informative but collapsed under `delta = 0.01`. Its prevalence,
observation count, and per-observation `h(1/4)` structure independently
recompute.

The note is **not clean as written**, however. The preregistered per-endpoint
reporting functions pool endpoints that share offset `U = 0` and then label
the pooled value as the value at each endpoint. This invalidates every
`per_endpoint_an` and `per_endpoint_un` field for an endpoint `T <= L` when
more than one endpoint shares that offset. It also makes the note's claimed
equality across full-context endpoints an implementation artifact. Correct
endpoint conditioning resolves, rather than merely confirms, the two
unexplained law-level regularities highlighted in §§3 and 6.

Recommended disposition: **accept P3b and the law-level attribution result;
correct the per-endpoint implementation and artifacts; revise the endpoint
narrative and the two “unexplained” regularities; repair the minor precision
and gate-6 wording below.** Witness 7's evidence-map status remains for Tony
and Claude to adjudicate after this review, as requested.

## Scope and evidence

Reviewed:

- Preregistration `d8-attribution-prereg-v0.1.md` at `a39f555`.
- C1 grid freeze v0.2 at `d46a6b9` and extension freeze v0.3 at `133df92`.
- C1 artifacts `d8-attribution-c1-2026-08-27.{jsonl,json}` (716 cells) and
  `d8-attribution-c1-v0.3-2026-08-28.{jsonl,json}` (173 cells).
- C0b attribution artifact for the stated cross-world controls.
- Prediction specification and the v0.3 score artifact; the checker was also
  rerun from the current tree.
- `attribution.py`, `d8_measure.py`, both window filters, the measurement and
  benchmark runners, and the relevant attribution/channel tests.
- Commit contents and ordering through `4de799f`, its stamp `feb27b2`, and
  the OTS-upgrade commit `aa6ad4b`.

Independent checks included exact freeze/artifact membership, uniqueness and
cross-grid disjointness; cost-only benchmark key scans; aggregate assertions
over every committed C1 cell; a fresh construction of the 1,771,884-visible-
observation P3b table at r1; and fresh endpoint-conditioned constructions at
`(6,6,2)`, `(10,10,2)`, and `(9,9,3)`.

## Finding 1 — per-endpoint values are pooled by offset, not conditioned on endpoint

**Severity: major for the per-endpoint fields and their interpretation; no
effect on the primary law-level estimands or P3b verdict.**

The preregistration §7 requires, for each endpoint `T`, the anchored and
unanchored gain restricted to windows generated at that endpoint. The shipped
functions do not implement that restriction:

- `attribution.per_offset_anchored` iterates over `T`, computes
  `u = law.offset(T)`, and selects every table entry with that `u`.
- `d8_measure.per_offset_unanchored` does the same.
- Neither function also selects the observation length
  `n = T - u`, even though `(u, n)` identifies `T` under the statutory law.

For `T > L`, positive offsets are unique and the selection happens to identify
the endpoint. For every `T <= L`, `u = 0`. All reset-visible endpoints up to
`L` are therefore pooled. The same pooled result is emitted once under each
such endpoint label. In a full-context law, every endpoint has `u = 0`, so all
reported endpoint values are copies of the law-level value.

The existing regression in `test_attribution.py` checks only that the mean of
the reported endpoint values equals `delta_an`. The erroneous pooling preserves
that mean because endpoints have equal prior mass, so the test cannot detect
the defect.

### Corrected values for the two reported regularities

Endpoint restriction by both `u` and observation length gives:

1. C1 `epsilon = 1/2`, `B = 2`, full-context r4:

   - At `(6,6,2)`, the artifact reports the same `0.1933278055410727` at
     endpoints 2, 4, and 6. Correct values are
     `{2: 0.5799834166232182, 4: 0, 6: 0}`; their mean is the committed
     law-level delta, modulo the last float bit.
   - At `(10,10,2)`, the artifact reports the same
     `0.11599668332464363` at all five endpoints. Correct values are
     `{2: 0.5799834166232181, 4: 0, 6: 0, 8: 0, 10: 0}`.
   - The same endpoint-2-only structure yields the committed `(8,8,2)` and
     `(12,12,2)` values. Hence

     ```text
     delta(T_ep) = 0.5799834166232181 / (T_ep / 2),
     ```

     because the law uniformly averages over `T_ep / 2` endpoints. The
     reported prevalence `2/T_ep` is the same fact in mass form. The
     regularity is not unexplained after correct endpoint conditioning.

   A direct enumeration at endpoint 2 gives the compact entropy expression

   ```text
   C = (7/16) h(1/21)
     + (1/8)  h(1/6)
     + (5/24) h(1/5)
     + (3/16) h(4/9)
     + (1/24) h(1/2)
     = 0.5799834166232181 bits,
   ```

   where `h` is binary entropy. The weights are the exact law masses of the
   five shuffled-posterior shapes at `T = 2`; the ordered full-context
   posterior is a point mass.

2. C1 `epsilon = 1`, `(9,9,3)`, r4 (and equivalently r1–r3 at the law-level
   result):

   - The artifact reports `1/108` at endpoints 3, 6, and 9.
   - Correct endpoint deltas are `{3: 0, 6: 0, 9: 1/36}`.
   - Uniform averaging over three endpoints gives `1/108`. The informative
     endpoint-9 mass is `1/36`, and each informative observation loses one
     bit. This explains both the exact delta and exact prevalence.

### Consequences and repair

- The law-level `delta_an`, `delta_un`, offset term, coordinate attribution,
  prevalence, per-observation gains, collapse labels, prediction scores, and
  complete-census two-path gates do not call the per-endpoint functions and
  are unchanged.
- The note's §3 statement that per-endpoint anchored values are equal across
  endpoints is false and should be withdrawn.
- The §3/§6 `delta * T_ep/2` regularity and the exact `1/108` result should be
  described by the endpoint-localized derivations above, not as unexplained.
- Both per-endpoint functions should select by `u` **and** visible/latent
  observation length, or the tables should carry `T` explicitly.
- Add a regression whose expected corrected output at `(6,6,2)`, r4,
  `epsilon = 1/2` is `{2: C, 4: 0, 6: 0}`. Checking only the endpoint mean is
  insufficient.
- Regenerate the `per_endpoint_an` and `per_endpoint_un` fields in the C0b
  and C1 artifacts, then audit any downstream reader that consumed them.

## Finding 2 — two “last stored digit” claims remain false

**Severity: minor precision/wording; no qualitative or threshold effect.**

Section 6 says `(12,10,2)`, `epsilon = 1`, r1–r3 carry the same loss as
`(12,12,2)` “to the last stored digit.” The stored artifact values are:

```text
L = 10: delta_an = 0.00013796312384252267
L = 12: delta_an = 0.00013796312384252272
```

The difference is one floating-point unit at this scale. Their stored
`max_g` values likewise differ (`0.8112781244591329` versus
`0.8112781244591328`). They agree at the note's displayed precision, and
their exact prevalence and mechanism agree, but not to the last stored bit
or digit. The provenance paragraph already records the associated
`-5.421010862427522e-20` rho residue at `L = 10`; the earlier sentence should
use “to the displayed precision.”

Similarly, at `(12,12,2)`, `epsilon = 1/2`, the REQ semantic-chain term and
REQ Shapley value differ by about `3.35e-18`, while the envelope width is
`6.690713250361718e-18`. “Agreeing to the last digit” is not true of the
stored floats; “agreeing to the displayed precision” is.

## Finding 3 — preregistered gate 6 is recorded, not executed per measured law

**Severity: procedural deviation / documentation ambiguity; no evidence of
a numerical failure.**

Preregistration §5 gate 6 says ordered mode equals identity serialization of
the per-record filter “at every measured law.” `d8_measure.measure_cell` does
not execute `test_ordered_bucket_equals_per_record_filter`; it writes the
test's name into each artifact cell and sets `all_passed = true` after the
other gates pass. The named suite test covers C0b stochastic, one selected
four-record path, and rungs r1/r4. It is not parameterized over the measured
grid.

The result risk is low for a specific reason: `step_ordered_bucket` is
literally a loop over `filter.step`, while the attribution measurement's
ordered path calls `filter_window`, whose update is also one recursive
per-record step at a time. In addition, every ordered observation is compared
against independent path summation in the uncapped two-path gate. I found no
counterexample or alternate ordered implementation that could diverge.

Nevertheless, “every §5 gate passed at every cell” is not a literal account
of the enacted gate-6 procedure. Either record this as a preregistration
deviation justified by construction, or replace the string marker with an
executable identity assertion at the appropriate abstraction boundary.

## Finding 4 — bijection totals count repeated cell-state checks

**Severity: terminology only.**

The note reports a Gate-F bijection on 642,762 “distinct `(U,S_T)`” pairs in
v0.2 and 301,695 in v0.3. These numbers are sums of each cell's independently
deduplicated `bijection_n`. The same pair is checked again across rungs and
overlapping laws; for example, the four `(12,12,2)` rungs each report the
same 636 pairs. The totals are valid cumulative **cell-state checks**, not
globally distinct pairs. The gate itself is unaffected.

## Claims independently confirmed

### Freeze and provenance

- The v0.2 artifact contains exactly the 716 v0.2-admitted cells; the v0.3
  artifact contains exactly the 173 v0.3-admitted cells; keys are unique and
  the two sets are disjoint.
- The v0.3 benchmark contains exactly the 628 v0.2-refused cells. Its 173
  admitted and 455 refused records reproduce the v0.3 freeze.
- Both benchmark JSONLs contain cost fields only under a scan for result-
  shaped keys (`delta`, entropy, Shapley, prevalence, offset, chain, envelope).
- Commit `94699fd` contains the v0.3 JSONL/JSON, prediction score, and loader
  change, but no C1-note change. Commit `4de799f` adds §6 and records the
  failed pre-commit assertion and mismatched earlier commit message. The
  provenance paragraph is accurate on these points; history was not rewritten.

### Gates and aggregate readings

- v0.2: 716 cells; 15,888,849 shuffled and 10,134,321 ordered cell-observation
  checks; 642,762 per-cell bijection checks; all artifact `all_passed` flags
  true; 146 informative and 138 not collapsed.
- v0.3: 173 cells; 41,409,418 shuffled and 18,724,170 ordered
  cell-observation checks; 301,695 per-cell bijection checks; all artifact
  `all_passed` flags true; 41 informative and 27 not collapsed; measured wall
  sum 55.131 CPU-hours; longest cell 3422.524 seconds.
- The v0.2 headline counts, full-context/truncation split, offset-term counts,
  rung-difference counts, maxima, and collapse counts recompute from the
  consolidated artifact.
- The v0.3 §6 counts, maxima, offset statements, and collapse counts recompute.

### Predictions and P3b structure

A fresh prediction-checker run gives P1 PASS, P1-mechanism PASS, P2 FAIL
4/36 (preserved), P3a PASS 6/6, P3b PASS 3/3, and P4 NO_CHECK, with no unknown
artifact families.

At C1 `(12,12,2)`, `epsilon = 1`:

- r1–r3 each have
  `delta_an = delta_un = 0.00013796312384252272`, offset term zero,
  anchored semantic-chain REQ equal to the full loss, anchored Shapley REQ
  equal to the full loss, and zero-width REQ envelope; r4 is exactly zero.
- Exact prevalence is `241/1417176`; 3,328 of 1,771,884 visible observations
  are informative.
- An independent rebuild of the r1 table found exactly one gain among all
  informative observations: `0.8112781244591328 = h(1/4)`. Pushing each
  informative posterior onto REQ produced exactly one shape as well:
  `(1/4, 3/4)` in all 3,328 cases. This validates the 3:1 two-labeling
  account at the measured law.
- C0b `(12,12,2)` is exactly zero at both disciplines and all four rungs.
- The measured C1 effect is about 72.5 times below `delta = 0.01`, hence
  informative and collapsed. Calling it roughly three orders of magnitude
  below the C0b B=3 range is fair at the precision used in the note.

## Evidence-map input, without adjudication

P3b is a genuine positive existence result, not a numerical zero rounded up:
its exact informative mass and per-observation posterior structure are
nonempty. It is also decisively below the frozen collapse threshold. Those
two statements should remain separate when witness 7's C1 status is decided.
This review does not choose whether the statutory witness requires existence
alone or non-collapse; it supplies the verified facts for that decision.

## Suggested correction order

1. Fix and regression-test endpoint conditioning.
2. Regenerate only the derived per-endpoint fields, verifying that all
   law-level fields remain bit-for-bit unchanged.
3. Amend the C1 note: withdraw endpoint equality, replace the two regularity
   paragraphs with the endpoint-localized derivations, and change “last stored
   digit” to “displayed precision.”
4. Record or execute gate 6 according to the preregistration's literal scope.
5. Rename the summed Gate-F totals as cell-state checks.
6. Then adjudicate witness 7 in the evidence map.

## Verification at handoff

`uv run pytest -q` at `aa6ad4b` completed with **202 passed in 52.70 s**.
The only working-tree change is this uncommitted review artifact.
