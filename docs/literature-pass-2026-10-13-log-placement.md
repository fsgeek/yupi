# Literature pass: log placement and telemetry for learned consumers (2026-10-13)

> Scope: the item skeleton v0.5 §1 owes, namely whether the systems literature states a rule for placing trace
> information relative to where it is *consumed*. Method: four web searches and two abstract-page reads. Not
> checked: full texts, citation graphs, AIOps workshop proceedings, the OpenTelemetry design discussions.
> Owning instance.

## Findings

**1. Log20 is the precedent for the figure of merit we call incomplete.** Zhao, Rodrigues, Luo, Stumm, Yuan, Zhou,
"Log20: Fully automated optimal placement of log printing statements under specified overhead threshold", SOSP
'17, pp. 565–581, DOI 10.1145/3132747.3132778. Its abstract page reads: "Guided by information theory, the core of
our algorithm measures how effective each log printing statement is in disambiguating code paths." Placement there
means *where in the code* a statement goes. The objective is how well the resulting log disambiguates the
execution path (identifiability), traded against runtime overhead. This is the extraction decision of §1, done
information-theoretically, at the producer. It is the strongest systems citation for "the classical figure of
merit is identifiability". The exact measure (entropy or otherwise) was not read from the full text and must be
before we cite a formula.

**2. Where-to-log recommenders** (Fu et al. 2014; Zhu et al., LogAdvisor 2015; arXiv 2103.01755; FastLog
arXiv 2311.02862) treat placement as a code-site classification problem, learned from what developers do. These are
producer-side too.

**3. Learned consumers of logs exist, and treat distance as a model problem.** DeepLog (LSTM), LogBERT, LogGPT
(arXiv 2309.14482) and LogNEO (arXiv 2606.08153, unverified preprint) model log sequences. The anomaly-detection
literature names long-range dependency as the difficulty, and answers it with architecture (transformers, longer
context), never with format.

**4. Agent-ready telemetry addresses structure, not sequence placement.** UModel (Pei et al., arXiv 2606.04799,
June 2026) argues that observability data should be re-modelled as linked objects so that LLM agents can relate
signals for root-cause analysis. It is the nearest statement that telemetry should be designed for a learned
consumer, but its abstract is about schema and semantic linkage, not where in the stream information sits.

## What §1 may say

- Producer-side placement is studied, and it is information-theoretic (Log20). Its objective is identifiability
  under cost.
- Learned consumers of logs are studied, and distance is treated there as something the consumer must overcome.
- In this limited search we found no statement that trace information should be placed relative to its point of
  use in the stream, nor any measurement of what such placement buys a learned consumer at a fixed ceiling. §1
  says "we found no", not "there is no", and cites the scope above.
