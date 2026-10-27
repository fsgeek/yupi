# Arm B2, open-factual queries: result (2026-10-27)

> Declared in `open-factual-declared-2026-10-27.md` (stamped a3f1017 before running). Scores in
> `open-factual-2026-10-27/scores.json`, audit in `open-factual-2026-10-27/audit.json`. Post hoc checks are in
> `scripts/open_factual_posthoc.py`. Data: `~/.cache/yupi-scratch/open-factual-2026-10-27/full/`.

## Declared verdicts

| | OLMo | Llama | Qwen | Mistral |
|---|---|---|---|---|
| correct / wrong / refusal (84 entities) | 35 / 48 / 1 | 61 / 23 / 0 | 37 / 45 / 2 | 75 / 9 / 0 |
| **O1** AUC(wrong vs correct) ≤ 0.75 | 0.902 | 0.873 | 0.781 | not scored (9 wrong) |
| **O2** AUC(correct open-factual vs knowable) ≥ 0.70 | 0.742 | 0.841 | 0.841 | 0.766 |
| audit: sampled "wrong" that is a real work | 0 / 20 | 1 / 20 | 2 / 20 | 1 / 9 |

- **O1 failed in all 3 scored models.** Within one open-factual form, mean per-token entropy separates invented
  titles from real ones at 0.78–0.90. That is close to how well it separates unknowable from knowable closed
  queries (0.89–0.92).
- **O2 held (4/4).** Correct answers to open-factual questions carry more entropy than single-answer facts.
- **The audit passed** (0–11 %, under the declared 20 %). *Corrected after review:* that audit searches the same
  incomplete database and can mis-extract titles. Codex found Mistral's true rate is at least 3/9. "Resolved, not an
  artefact of Wikidata's gaps" is withdrawn; the frozen audit passed, but its power is limited.
- **Corrected labels (post hoc, after review):** two matching bugs are fixed in `scripts/open_factual_relabel_v2.py`
  (three label changes). AUCs are 0.917 (OLMo), 0.873 (Llama), 0.791 (Qwen); O1 still fails 3/3. Per template
  (novel / film / album): OLMo 0.945 / 0.847 / 0.938; Llama 0.836 / 0.972 / 0.836; Qwen 0.875 / **0.591** / 0.836.

## Post hoc checks (not declared)

| | AUC length | AUC, committed fabrications only (titled, no hedge) | AUC, entropy of first 12 tokens |
|---|---|---|---|
| OLMo | 0.690 | 0.905 | 0.812 |
| Llama | 0.543 | 0.896 | 0.880 |
| Qwen | 0.739 | 0.781 | 0.798 |

- The separation is not hedged refusals labelled "wrong": committed fabrications alone give the same AUCs.
- It is not mainly length: length is weaker in every model.
- Known label leaks, left as frozen: substring matches let a few fabrications pass as correct (OLMo named *The
  Bookshop on the Corner* for Penelope Fitzgerald), and some hedges count as wrong. Both pull AUC toward 0.5, so the
  true separation is, if anything, higher.

## What B and B2 say together

> *Corrected after review (See `escape-hatch-codex-review-2026-10-27.md` for the review and dispositions.):* the mechanism and the repair below are
> **hypotheses**, not findings. LLM token entropy is not decomposed into randomness and hidden state the way Yupana's
> H = R + G is. "Within one form" pooled three templates, and Qwen's films give 0.591. A per-form constant cannot
> change ranking within a form; it can only help pooled screening across forms, which is untested. The weakest joint
> in the analogy: a Yupana second step observes the world again, while an LLM's continuation is self-commitment.

- **Across query forms, entropy fails.** Correct creative answers carry the most entropy of anything (Arm B: K <
  OS < U < OL), so no single threshold catches fabrication.
- **Within one form, entropy works.** Invented titles carry more entropy than real ones (0.78–0.90), even though
  correct answers there also carry option entropy (O2).
- **This is Yupana's picture, on real models.** Entropy is randomness plus a hidden-state contribution. The hidden
  state's part is visible only against the right baseline for randomness. In Yupana, the observer who knew the
  common laws kept the full advantage (`partial-support-result-2026-10-27.md`). Here, the analogue is knowing the
  query's form. The "query-type prior" I first called degenerate is the repair, once the form is fine enough to
  include open-factual questions.
- **My prediction was wrong in the more interesting direction.** I expected option entropy to wash out the signal
  of not knowing, as a next-event law over many options would. It did not. The signal of not knowing survives the
  options.

## What it points to

1. **A form-conditioned monitor.** Threshold entropy relative to the query form's own baseline, the per-form median
   on correct answers. Score it on B and B2 pooled. Declare first, with the form taxonomy fixed in advance.
2. **Why does not-knowing survive option entropy in LLMs?** Yupana's one-step law mixes the two. A candidate:
   invented titles are generated token by token with fresh uncertainty, while real titles, once begun, are
   memorised and resolve. The per-token profile (Arm B's RESOLVE) failed on B, but B2 is the place to test it, since
   here hidden state should *persist*. A sign flip relative to Yupana's would itself be a finding.
