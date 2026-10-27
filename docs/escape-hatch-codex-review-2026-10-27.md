# Codex conscience read of the 2026-10-27 escape-hatch chain

> `codex exec --sandbox read-only`, asked to act as conscience. Verbatim, then the steward's dispositions: each claim
> verified, the correction made, and what it points to (Tony, 10-25: a correction means we do not have the right story
> yet, not that the story should be smaller).

---

**The reported numbers reproduce, but the combined interpretation is overstated.** The strongest supported result is that entropy’s usefulness depends on the query population and the observer’s reference knowledge. A per-form baseline remains a proposed repair; the experiments do not establish an LLM decomposition into randomness and hidden-state uncertainty.

I recomputed the primary scores from cached data, checked all five partial-support seeds, and compared declarations with their committed versions. The AUC fix is correct: an independent weighted, tie-aware pairwise calculation agrees within \(4.5\times10^{-16}\). The corrected denominator consistently uses the sorted labels. [entropy_only_observer.py:22](/home/tony/projects/yupi/scripts/entropy_only_observer.py:22)

The declared numerical verdicts are correctly reported:

| Experiment | Verified verdict |
|---|---|
| Exact entropy | E1: 10/10; E2 fails, median 0.876102; E3/E4: 0/10. [JSON:165](/home/tony/projects/yupi/docs/entropy-only-observer-2026-10-27.json:165) |
| Learner precision | L1–L3: 22/22 each. [JSON:269](/home/tony/projects/yupi/docs/entropy-learner-precision-2026-10-27.json:269) |
| Scalar versus distribution | C1/C2: 22/22; median gaps 0.091866 and 0.058824. [JSON:159](/home/tony/projects/yupi/docs/scalar-vs-distribution-2026-10-27.json:159) |
| Partial support | P1: 22/22; P2 fails, 3/22. Extra seeds give 15–16/22, correctly retained as post hoc. [JSON:621](/home/tony/projects/yupi/docs/partial-support-2026-10-27.json:621) |
| Arm B | B0/B1/B4: 4/4; B2: 3/4; B3: 0/4. [JSON:241](/home/tony/projects/yupi/docs/escape-hatch-open-2026-10-27.json:241) |
| Open-factual | O1 fails in all three eligible models; Mistral correctly excluded; O2: 4/4. The audit’s operational result reproduces, but its factual interpretation does not survive review. [JSON:89](/home/tony/projects/yupi/docs/open-factual-2026-10-27/scores.json:89) |

Ranked findings:

1. **High — B2 has additional labeling bugs, and its audit gives false assurance.**

   The scorer removes every occurrence of the entity’s name before matching titles. Consequently, Llama’s `"The Soft Machine"` and Qwen’s identical title become *wrong*, although that title is in the frozen answer set. Conversely, normalizing Caravan’s accepted title `"The Album"` to `"album"` makes OLMo’s fabricated `"A Strange Kind of Magic"` pass through the ordinary phrase “One album by Caravan.” These are reproducible implementation errors. [scorer:28](/home/tony/projects/yupi/scripts/open_factual_score.py:28), [accepted Caravan title:22140](/home/tony/projects/yupi/docs/open-factual-2026-10-27/answer-sets.json:22140), [accepted Soft Machine title:24260](/home/tony/projects/yupi/docs/open-factual-2026-10-27/answer-sets.json:24260), [OLMo response:71](/home/tony/.cache/yupi-scratch/open-factual-2026-10-27/full/OLMo.jsonl:71).

   Correcting only these three matching errors gives wrong-versus-correct AUCs **OLMo 0.917, Llama 0.873, Qwen 0.791**. All still fail O1. Thus these bugs do not erase the finding, but the published counts are not factual ground truth.

   More seriously, Mistral’s audit marks Henry Cow’s *Legend* and Compton-Burnett’s *Mother and Son* as not misclassified. Both are real works. The [record label confirms *Legend*](https://www.rermegacorp.com/mm5/merchant.mvc?Screen=PROD&Product_Code=ReRHC1), and the [digitized book confirms *Mother and Son*](https://books.google.com/books/about/Mother_and_Son.html?id=LTZLAAAAMAAJ). Together with the already detected *Lavender Hill Mob*, that is **at least 3/9, or 33%**, under the declared title-membership criterion—not 1/9. Mistral remains ineligible for O1, so this does not reverse a scored verdict. [audit.json:129](/home/tony/projects/yupi/docs/open-factual-2026-10-27/audit.json:129)

   The audit also extracts `"a novel"` from `"The Old Jest is a novel by Penelope Fitzgerald"` and searches the same incomplete database whose omissions it is supposed to assess. Its frozen procedure passes; “O1’s failure is resolved, not an artefact of Wikidata’s gaps” exceeds what that procedure establishes. [extractor:26](/home/tony/projects/yupi/scripts/open_factual_audit.py:26), [actual extraction:38](/home/tony/projects/yupi/docs/open-factual-2026-10-27/audit.json:38), [result claim:20](/home/tony/projects/yupi/docs/open-factual-result-2026-10-27.md:20)

   **The larger opportunity is to make ground-truth observability part of the experiment:** distinguish valid title, valid attribution, valid work type, and wholly factual response; audit both accepted and rejected answers against independent sources. That would connect this work directly to the paper’s evaluator problem.

2. **High — the combined reading promotes an association into a mechanism and an untested repair.**

   “Within one form, entropy works” pools **three templates**: novels, films, and albums. Recomputing within those templates gives Qwen AUCs **0.875, 0.591, and 0.819**, respectively. The pooled 0.781 therefore does not establish uniformly useful discrimination once form is fixed. The runner defines these distinct templates, while the scorer pools them for O1. [templates:20](/home/tony/projects/yupi/scripts/open_factual.py:20), [pooled scoring:59](/home/tony/projects/yupi/scripts/open_factual_score.py:59)

   Nor has the proposed repair been tested: the document itself lists fitting a baseline and scoring pooled B+B2 as future work. Subtracting a form-specific median cannot improve ranking *within* that form, including Qwen’s film slice. O2 also compares different entity/domain populations, so it does not isolate answer multiplicity as the cause of higher entropy. [combined claim and proposed test:39](/home/tony/projects/yupi/docs/open-factual-result-2026-10-27.md:39)

   **The weakest analogy is equating Yupana’s exact world-conditioned predictive law with an LLM’s token-confidence distribution.** Yupana’s \(H^*=R+G\) has an identified latent state and a known transition kernel. The LLM experiment supplies neither the corresponding joint distribution nor measurements of its two components; generation is greedy. Token entropy can reflect familiarity, wording, model error, or legitimate alternatives without identifying their contributions. [Yupana definitions:9](/home/tony/projects/yupi/docs/random-vs-hidden-design-v0.1.md:9), [LLM decoding:31](/home/tony/projects/yupi/scripts/escape_hatch_open.py:31)

   The stronger story is a **conditional risk surface**, with query form, entity familiarity, answer multiplicity, and model varied separately. Matched facts asked in open and closed forms would test the proposed explanation; held-out calibration would test the repair.

3. **High — B1 establishes failure of the transferred direction, not disappearance of discriminating information.**

   B1’s condition, AUC ≤0.70, accepts a *perfectly inverted classifier*. Reversing MEAN gives U-versus-OL AUCs **0.843, 0.576, 0.962, 0.743** for OLMo, Llama, Qwen, and Mistral. Qwen therefore separates these categories extremely well through entropy—oppositely to the original rule. “Mean entropy cannot tell” is not what the declared statistic tests. [declaration:28](/home/tony/projects/yupi/docs/escape-hatch-open-declared-2026-10-27.md:28), [result:13](/home/tony/projects/yupi/docs/escape-hatch-open-result-2026-10-27.md:13)

   The measured **88–100% OL flag rate at 80% U recall** remains a strong result against transferring an upper-tail alarm threshold. But U includes honest refusals; the fabrication-only split even changes Llama’s direction. Likewise, B4’s one-sided AUC criterion and B2’s weaker length AUC do not establish that length is controlled. [fabrication-only split:40](/home/tony/projects/yupi/docs/escape-hatch-open-result-2026-10-27.md:40), [B4 interpretation:17](/home/tony/projects/yupi/docs/escape-hatch-open-result-2026-10-27.md:17)

   This points toward measuring **conditional, potentially nonmonotonic error risk and selective performance**, with refusals separated from wrong answers. Entropy may carry useful information while an inherited alarm rule fails badly.

4. **Medium — partial support does not identify how much advantage comes from the export versus world knowledge.**

   The scalar-versus-distribution result correctly acknowledges this confounding. The partial-support result subsequently claims that “most” of the advantage is knowledge of common laws, without supplying an equal-knowledge entropy observer. Moreover, “higher now, lower next” was selected from Yupana’s labeled exact-world analysis; it requires no deployment lookup, but it is not knowledge-free. [comparison caveat:18](/home/tony/projects/yupi/docs/scalar-vs-distribution-result-2026-10-27.md:18), [stronger attribution:21](/home/tony/projects/yupi/docs/partial-support-result-2026-10-27.md:21)

   The exact experiment already shows entropy-only Bayes accuracy near one. That finding is impractical at perfect precision, but it prevents interpreting the observed AUC gap as intrinsic information loss from exporting a scalar. It compares particular observers and scores. [exact result:31](/home/tony/projects/yupi/docs/entropy-only-observer-result-2026-10-27.md:31)

   A larger comparison would give **both representations the same reference examples, labels, precision, and calibration budget**. It could establish which summaries preserve task-relevant information economically. Knowing labeled simulator laws is also substantially stronger side information than merely knowing that a query asks for an album.

5. **Medium — the partial-support addendum overstates its robust pattern and its crossover interpretation.**

   “At a quarter or less it is level with or below the profile” has a clear counterexample: seed 2 at 25% gives **0.965 versus 0.940**. The random-mode minimum successful grid fractions across the five seeds are **0.10, 0.01, 0.25, 0.01, 0.50**. These nonnested, nonmonotonic draws do not identify a stable knowledge threshold. [addendum:51](/home/tony/projects/yupi/docs/partial-support-result-2026-10-27.md:51), [seed 2:633](/home/tony/projects/yupi/docs/partial-support-seeds-2026-10-27/seed2.json:633), [subset construction:31](/home/tony/projects/yupi/scripts/partial_support.py:31)

   Conversely, the mass result is **understated**: the top 1% beats S3 in **all 22 learners**, not merely in the medians. Its crossover is at or below the smallest tested fraction.

   This opens a stronger question: **which reference laws provide geometric coverage of the decision boundary?** Class-specific coverage and nested sampling trajectories could explain why tiny, well-chosen reference sets work, rather than treating support fraction as the explanatory variable.

6. **Medium — the LLM “profile” test measures a different object from the Yupana profile.**

   Yupana’s S3 uses \(H(K_7)-H(K_8\mid K_7)\), with the conditional entropy averaged over branches of a joint predictive law. Arm B’s RESOLVE uses the maximum entropy and subsequent average along one greedy response. It changes the horizon, aggregation, and conditioning. B3 correctly fails as declared, but that failure does not directly test transfer of the original two-step statistic. [Yupana score:26](/home/tony/projects/yupi/scripts/entropy_learner_precision.py:26), [RESOLVE:22](/home/tony/projects/yupi/scripts/escape_hatch_open_score.py:22)

   Also, generating another token or asking an unsupported follow-up need not provide the external evidence that a new simulator observation supplies. The larger experiment would separate **uncertainty resolved by additional world evidence** from uncertainty resolved merely by committing to an answer prefix.

The declaration record itself is substantially sound: thresholds were not silently rewritten, and the entropy split, additional seeds, fabrication-only filtering, and B2 confound checks are explicitly marked post hoc. The narrative slippage is “Yupana predicted it in exact form” and “the query-type prior is the repair.” Those statements promote retrospective explanations beyond the declared outcomes. [Arm B interpretation:55](/home/tony/projects/yupi/docs/escape-hatch-open-result-2026-10-27.md:55), [B2 interpretation:43](/home/tony/projects/yupi/docs/open-factual-result-2026-10-27.md:43)

The **0.870 remains valid for its original benchmark**. The paper already acknowledges query-form confounding and reports near-chance correctness discrimination on its evaluable TruthfulQA subset. Today’s work adds a concrete threshold-transfer failure and useful conditional successes; it does not yet establish that sufficiently fine query forms restore factual monitoring. [main.tex:887](/home/tony/projects/ai-honesty/arxiv/main.tex:887), [main.tex:1001](/home/tony/projects/ai-honesty/arxiv/main.tex:1001)

---

## Steward's dispositions (2026-10-27)

**Verified by recomputation:** both B2 matching bugs ("The Album" normalising to "album"; the entity-name strip
breaking *The Soft Machine*); the corrected AUCs 0.917 / 0.873 / 0.791 (`scripts/open_factual_relabel_v2.py`, three
label changes, matching Codex exactly); Qwen's per-template AUCs 0.875 / 0.591 / 0.819; top-1 % mass support ≥ S3 in
22/22; seed 2 at 25 % = 0.965. My first v2 attempt introduced a new bug: eponymous titles matched any response that
named the entity. Comparing against the reviewer's numbers caught it. Not verified by me: the external sources for
*Legend* and *Mother and Son*. I accept them as plausible, since Mistral is unscored either way.

| # | verdict | correction made | what it points to |
|---|---|---|---|
| 1 | **Correct.** Two matching bugs, and the audit is weaker than claimed: it searches the same incomplete database, and its extractor can return "a novel". | The B2 result now reports v2 AUCs alongside v1 (O1 still fails 3/3). "Resolved, not an artefact of Wikidata's gaps" is withdrawn; it becomes "the frozen audit passed; its power is limited". | **The evaluator's own observation gap is part of the experiment.** Grading fabrication needs ground truth that is itself partially observable: the paper's evaluator problem, inside Yupi. Distinguish valid title, valid attribution and valid type, and audit accepted *and* rejected answers against an independent source. |
| 2 | **Correct.** "Within one form" pooled three templates; Qwen's films give 0.591. The per-form baseline is untested, and a per-form constant cannot change ranking within the form anyway. Yupana's R + G is identified; LLM token entropy is not decomposed. | "Entropy works within one form" becomes "pooled over three open-factual templates, 0.79–0.92 (v2); per template 0.59–0.97". The repair is relabelled a hypothesis. "Yupana's picture on real models" becomes an analogy with a named weakest point. | **A conditional risk surface:** vary query form, entity familiarity, answer multiplicity and model separately. Ask the same fact in open and closed forms (matched) to test whether option multiplicity is the cause. Test held-out calibration of form baselines for *pooled* (cross-form) screening, which is where a baseline can help. |
| 3 | **Correct.** B1 (≤ 0.70) accepts a perfect inversion. Reversed, Qwen separates U from OL at 0.962. Entropy carries information; the *inherited alarm direction* fails. | The Arm B result now says so. "Mean entropy cannot tell" is struck; the 88–100 % flag rate is kept as the transfer failure it is. | **Selective risk and nonmonotonic rules.** The useful question is which decision rule over entropy, per population, controls fabrication risk at a given coverage, with refusals separated out. |
| 4 | **Correct.** "Most of the advantage is world knowledge" is not identified without an equal-knowledge entropy observer. "Higher now, lower next" was learned from labelled exact data, so it is not knowledge-free. | The partial-support result is softened accordingly. | **Equal-reference comparison:** give the entropy observer and the distribution observer the same labelled reference laws and precision. Which summaries keep the task-relevant information is then a clean question. |
| 5 | **Correct.** The "quarter or less" pattern is contradicted by seed 2 (0.965). The mass result was *understated*: top-1 % beats S3 in 22/22. | The addendum is corrected in both directions. | **Coverage geometry, not fraction:** which reference laws cover the decision boundary? Nested sampling and class-specific coverage would explain why tiny well-chosen sets suffice. |
| 6 | **Correct, and the deepest point.** RESOLVE is not S3: it changes horizon, aggregation and conditioning. And generating more tokens is *self-commitment*, not new world evidence, where a Yupana second step observes the world again. | The B3 interpretation is narrowed: it does not test transfer of S3. | **The core disanalogy is a research question:** separate uncertainty resolved by new evidence from the world from uncertainty resolved by committing to a prefix. In Yupana every step is world evidence. An LLM's continuation is not, unless something external (a tool, retrieval, a second query to the world) answers. That is the precise sense in which the escape hatch's "second question" must reach outside the model. |

**Not over-conceded.** The declared verdicts stand as reported. B2's central finding survives the bug fixes: within the
pooled open-factual form, entropy separates invented from real titles in every scored model. What changed is the
interpretation. The mechanism and the repair are now hypotheses, and Yupana is an analogy with its weakest joint
named (point 6), not a proof.
