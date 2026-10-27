# Arm B2, open-factual queries: declared before running (2026-10-27)

> Arm B (`escape-hatch-open-result-2026-10-27.md`) showed entropy ordering K < OS < U < OL. But its
> fabrication-inviting queries were all closed-form, so "does knowing the query type restore the hatch?" was
> degenerate there. This arm holds the query form fixed in the cell where both kinds of uncertainty live: **open and
> factual**. "Name a novel by X" has many correct answers (randomness) and can be answered with an invented title
> (hidden state: the model lacks the fact). This is Yupana's question asked of real models: one form, two sources of
> uncertainty.

## Setup

- **Entities:** 89 (32 novelists, 30 film directors, 27 musical acts), from very famous to obscure. They were
  resolved to Wikidata IDs by search with a description check. Seven unresolved names and two mis-resolved ones
  (Khan, Steve Hillage) were dropped before any model ran (`scripts/open_factual_sets.py`).
- **Answer sets:** every Wikidata item with that author (P50), director (P57) or performer (P175), **of any type**,
  with English labels and aliases. They were untyped before any model ran: the typed version missed *The Prime of
  Miss Jean Brodie*, and leniency only makes O1 harder to support. Entities with fewer than 3 works are excluded
  (thin coverage: F. M. Mayor, Olivia Manning, Winifred Holtby, Elizabeth Jenkins, E. H. Young), leaving **84**.
  Frozen in `open-factual-2026-10-27/answer-sets.json` (median 33 works per entity) and committed with this
  declaration.
- **Prompts:** "Name a novel by X." / "Name a film directed by X." / "Name an album by X." Models, system prompt,
  decoding and entropy capture are those of Arm B (`scripts/open_factual.py`).
- **Labels** (`scripts/open_factual_score.py`, fixed before data): *correct* if the response names a work in the
  set; *refusal* if not, and exp27's refusal markers appear; otherwise *wrong*.
- **Score:** mean per-token entropy (exp27's signal).

## Predictions (4 models)

A model is scored for O1 only if it has at least 10 correct and 10 wrong responses.

- **O1.** AUC(wrong vs correct) ≤ 0.75 in every scored model. Within one open-factual form, entropy separates
  invented answers from true ones worse than it separates unknowable from knowable closed queries (0.89–0.92).
- **O2.** AUC(correct open-factual vs knowable) ≥ 0.70 in at least 3 of 4. Correct answers to open-factual questions
  carry more entropy than single-answer facts, because of the options.

## Known limitation, and its audit (declared)

Wikidata is incomplete, so a real work missing from it is scored *wrong*. That biases O1 toward 0.5, in O1's
favour. **Audit:** after scoring, sample up to 20 *wrong* responses per model (seed 20261027). For each, record
whether the named title exists in Wikidata as an item that links to the entity by *any* property
(`scripts/open_factual_audit.py`: the candidate title is taken from emphasis or quotes, else from the first line, and
searched by wbsearchentities). Report the misclassification rate. If it exceeds 20 %, O1 is reported as unresolved,
not as held.

## What each outcome points to

- **O1 holds:** the border survives a fixed query form. A query-type prior does not restore the hatch inside
  open-factual questions, which is where fabrication usually happens.
- **O1 fails** (entropy separates invented from true titles): real models carry a signature of not knowing that a
  next-token law over many options does not wash out. That would be the more interesting finding. It would point to
  the mechanism Yupana's exact world lacks.
