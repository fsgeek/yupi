# Literature pass for §4a and §5 (2026-10-09)

> Scope: item 2 of "Before external review" in `paper1-skeleton-v0.4.md`. Method: web search, arXiv abstract pages,
> and one full-text read (Someya et al., extracted from the PDF). Everything else comes from abstracts or snippets.
> Not checked: OpenReview, Alignment Forum or LessWrong, and Semantic Scholar citation graphs. Not committed.

## Q1. Novelty of §4a (relocation with the ceiling held fixed)

**Closest prior work: Someya, Svete, DuSell, O'Donnell, Giulianelli, Cotterell, "Information Locality as an
Inductive Bias for Neural Language Models", ACL 2025 (long), arXiv:2506.05136.**
https://arxiv.org/abs/2506.05136 · https://aclanthology.org/2025.acl-long.1357/
- *Experiment 1:* they apply length-preserving bijections to an English corpus (reversal, deterministic shuffles,
  k-local shuffles). The paper says these transformations preserve global entropy and next-symbol entropy "by design"
  while changing m-local entropy. Next-symbol cross-entropy rises close to linearly with m-local entropy, with
  R² ≈ 0.92 at m = 4 for both the LSTM and the Transformer. **In effect, this is an intervention that relocates
  information while holding the Bayes-optimal loss fixed, with learner shortfall measured against it.** That shortfall
  follows the move monotonically.
- *Experiment 2 (PFSAs):* the m-local entropy and the true next-symbol entropy are exact, and the metric is D_KL
  (cross-entropy minus true entropy). It is **correlational across random automata**, though, not an intervention
  on a fixed generator.
- *How §4a differs:* (i) In Exp. 1 the ceiling is fixed only in aggregate, and its value is unknown on natural text.
  Yupi's ceiling is exact and identical **class by class**. (ii) Their perturbations scramble the whole sequence.
  The relay *adds* a near copy and leaves the far source in place. (iii) Their result says shortfall tracks locality
  monotonically. **§4a reports the opposite shape:** the gain does not follow the move, is V-shaped in Δι at
  5 epochs, and flattens at 15. Someya et al. should be cited as the baseline expectation that §4a fails to confirm.
  This contrast makes §4a stronger, provided it is framed that way.

**Other neighbours (none pre-empts §4a):**
- Kallini et al., "Mission: Impossible Language Models", ACL 2024, arXiv:2401.06416, https://arxiv.org/abs/2401.06416.
  Word-order perturbations of English and GPT-2 perplexity. No exact ceiling, and the comparison is qualitative
  (possible vs impossible). Someya et al. position themselves against it.
- Borenstein, Svete, Chan, Valvoda, Nowak, Augenstein, Chodroff, Cotterell, "What Languages are Easy to
  Language-Model?", ACL 2024, arXiv:2406.04289, https://arxiv.org/abs/2406.04289. They train about 15k RNN and
  Transformer LMs on 2,100 random PFSAs and estimate KL against the exact automaton. Correlational, with no relocation.
- Abbe, Bengio, Lotfi, Sandon, Saremi, "How Far Can Transformers Reason? The Globality Barrier and Inductive
  Scratchpad", NeurIPS 2024, arXiv:2406.06467, https://arxiv.org/abs/2406.06467. Theory: learnability is governed by
  "globality", and an educated scratchpad helps if it breaks globality at each step. A scratchpad changes the target
  sequence, so the ceiling is not held fixed. This is the nearest theoretical frame for "relay as locality aid", and
  §4a's result is in mild tension with a naive reading of it.
- Pfau, Merrill, Bowman, "Let's Think Dot by Dot", arXiv:2404.15758, https://arxiv.org/abs/2404.15758. Uninformative
  filler tokens improve learnability on synthetic tasks. This bears on §5's move-vs-bind confound (C3): extra tokens
  can help without moving any information.
- Siems et al., "Learning State-Tracking from Code Using Linear RNNs", arXiv:2602.14814,
  https://arxiv.org/abs/2602.14814. State reveals interleaved in REPL traces, framed as a PFSA with deterministic
  reveals. Reveals change what is observable, so the ceiling moves. Closest to an "interface" axis, and not a
  relocation study.
- Induction-head formation: Aoyama and Wilcox, arXiv:2511.16893 (formation predicted from batch and context size);
  "Evolution of Statistical Induction Heads", NeurIPS 2024. These cover formation timing, not ceiling-fixed relocation.
- Belief-geometry line (Shai et al. 2405.15943; 2602.02385; MetaOthello 2602.23164; Brenner et al. 2603.16689;
  Markovian Circuit Tracing 2605.20824). None intervenes on the *position* of information. **New since the
  August review:** Balcells, Lee, Rastogi, Riechers, Shai, Poncini, "Large Language Models Develop Belief State
  Geometry In-Context", arXiv:2609.17376 (15 Sep 2026), https://arxiv.org/abs/2609.17376. It uses pretrained LLMs
  prompted with 40 HMMs, has no relocation, and does not threaten paper 1. **Flag for paper 3:** Li, Zheng, Wu, Chen,
  "Erased, Rerouted, or Rescaled? Post-Training and the Causal Quotient of a Language Model's Belief State",
  arXiv:2610.05292 (4 Oct 2026). It separates information that is represented from information used in decisions,
  inside belief-state models. This is exposure/use-gap territory. Read it before gap 3 is framed.

**Verdict.** The claim needs **qualification. It is not pre-empted.** "Relocating information while holding the
Bayes loss fixed and measuring learner shortfall" was done by Someya et al. (ACL 2025): the global ceiling was held
fixed, the information was relocated by bijection, and the shortfall tracked locality. Paper 1 therefore cannot
claim the intervention *type* as new. What survives, as far as this pass found: (a) the ceiling is held identical
**class by class** and computed **exactly** for a stated observer, in a structured world; (b) the intervention
*adds* a relay and keeps the source, so it is not a scrambling bijection; (c) the **finding** runs against the
established monotone-locality result: the gain does not follow the move. Recommended framing: "Prior work finds
learner difficulty tracks information locality at fixed global entropy (Someya et al. 2025). With the ceiling exact
and fixed per class, we find that moving information closer does not relieve the shortfall in proportion." Before
any priority claim, one residual risk needs closing: Someya et al.'s full PFSA appendix and their follow-ups
(Cotterell/Svete group, 2025–26) were not exhaustively searched.

## Q2. Citation verification (all four verified)

1. **Jonas, E. & Kording, K. P. (2017).** "Could a Neuroscientist Understand a Microprocessor?" *PLOS Computational
   Biology* 13(1): e1005268. https://doi.org/10.1371/journal.pcbi.1005268. They apply neuroscience analyses (lesions,
   tuning curves, connectomics, and others) to a simulated MOS 6502 and find that the naive methods fail to recover
   its known mechanism. The claimed use is correct.
2. **Geiger, A., Lu, H., Icard, T., & Potts, C. (2021).** "Causal Abstractions of Neural Networks." *NeurIPS 2021*.
   https://proceedings.neurips.cc/paper/2021/hash/4f5c422f4d49a5a807eda27434231040-Abstract.html. It aligns neural
   representations with variables of an interpretable causal model and verifies the alignment with **interchange
   interventions**. The case study is BERT and LSTM on MQNLI. The claimed use is correct.
3. **Méloux, M., Maniu, S., Portet, F., & Peyrard, M. (2025).** "Everything, Everywhere, All at Once: Is Mechanistic
   Interpretability Identifiable?" *ICLR 2025*; arXiv:2502.20914, https://arxiv.org/abs/2502.20914. It finds
   **systematic non-identifiability**: several circuits replicate a behaviour, a circuit has several
   interpretations, several algorithms align with the network, and one algorithm aligns with several subspaces.
   The claimed use is correct. (The same first author has a later related paper, "The Dead Salmons of AI
   Interpretability", arXiv:2512.18792, which was not read.)
4. **Sutter, D., Minder, J., Hofmann, T., & Pimentel, T. (2025).** "The Non-Linear Representation Dilemma: Is Causal
   Abstraction Enough for Mechanistic Interpretability?" *NeurIPS 2025* (spotlight); arXiv:2507.08802,
   https://arxiv.org/abs/2507.08802. Their Theorem 1: with arbitrarily complex alignment maps, any network can be
   perfectly aligned with any algorithm under mild assumptions, so unrestricted causal abstraction is trivial. The
   claimed use ("vacuous with unrestricted alignment maps") is correct. Their word is "trivial/uninformative", so
   quote that rather than "vacuous" if quoting.

## Q3. Excess loss against exact ceilings, per observation interface

**No prior work found that varies the observation interface over a fixed generator and measures excess loss against
the exact per-interface ceiling.** The closest work falls into three groups:
- **Exact ceilings with no interface axis.** Borenstein et al. 2024 (KL to the exact PFSA, across automata); Someya
  et al. 2025, Exp. 2 (exact D_KL, across automata); Markovian Circuit Tracing, arXiv:2605.20824
  (https://arxiv.org/abs/2605.20824), which reports excess loss over Bayes of 0.0138 across six HMM families,
  including an "ambiguous-emission" family. That family varies the HMM itself, not the view of a fixed one, though
  it is the nearest gesture toward an interface axis. The Bayesian wind-tunnel papers (2512.22471, 2607.19379) remain
  exact-posterior studies with no interface variation, per the August review.
- **An interface-like manipulation with no exact ceiling.** Siems et al. 2602.14814 (density of state reveals).
- **Locality manipulation with the ceiling fixed in aggregate.** Someya et al. 2025, Exp. 1, which is closer to
  Yupi's §4a than to §3.

The August verdict stands for Q3: interface-as-variable with exact per-interface ceilings is unclaimed as of this
pass. This rests on abstracts and search snippets, not full texts.

## Not verified / open
- The full text of 2605.20824, and its authorship, is still unverified (carried over from August).
- The Alignment Forum and LessWrong were not searched (for Simplex previews).
- Follow-ups citing Someya et al. 2506.05136 were not traced. **This is the highest-value remaining check for §4a.**
