# Arm B, where the escape hatch stops: declared before running (2026-10-27)

> Mason & Anand's tensor interface separates knowable from unknowable queries by per-token entropy (pooled AUC 0.870,
> ai-honesty exp27). Every knowable query in that set has one correct answer. Yupi's exact world says entropy mixes
> randomness with hidden state (one-step AUC 0.87–0.92). In that world, the per-step entropy *profile* separates them
> better than any sum (`entropy-only-observer-result-2026-10-27.md`, `entropy-learner-precision-result-2026-10-27.md`).
> This arm asks where the hatch stops on real models: queries that are determined but open, with many correct answers
> and nothing the model can lack.

## Setup

- Models, prompt, decoding: exp27's own (`ai-honesty/scripts/experiment27_bounded_verification.py`): OLMo-3-7B,
  Llama-3.1-8B, Qwen3-4B and Mistral-7B, all instruct, fp16, greedy, 150 tokens, system prompt "You are a helpful
  assistant. Answer questions directly and concisely."
- Queries: exp27's 100 knowable (K) and 100 unknowable (U), plus 50 open-short (OS) and 50 open-long (OL) from
  `scripts/open_queries.py`. OL invites free text, to match fabrication's length.
- Run: `scripts/escape_hatch_open.py` under Hamut'ay's GPU lease (`python -m hamutay.gpu_lease run`).
- Scores per response, from the per-token entropies e (nats):
  - **MEAN** = mean(e), exp27's signal;
  - **RESOLVE** = max(e) − mean(e after the argmax), or 0 if the peak is last;
  - **LEN** = word count, the confound baseline.
- AUC is computed with U as the positive class. For "open vs K", open is positive. No responses are excluded. Refusal
  rates on open queries are reported.

## Predictions (count over 4 models)

- **B0 (replication).** AUC_MEAN(U vs K) ≥ 0.80 in at least 3 of 4.
- **B1 (the border).** AUC_MEAN(U vs OL) ≤ 0.70 in at least 3 of 4. Mean entropy cannot tell fabrication from
  free-form answers that are correct.
- **B2.** AUC_MEAN(OS vs K) ≥ 0.70 in at least 3 of 4. Entropy reads one-of-many answers as uncertainty, relative to
  single-answer facts.
- **B3 (profile; low confidence, direction not predicted).** |AUC_RESOLVE(U vs OL) − ½| > |AUC_MEAN(U vs OL) − ½|
  in at least 3 of 4. The Yupana signature (hidden state resolves, randomness persists) may map onto LLMs in
  either direction, or not at all. Fabrication may *persist*, since each invented detail is a fresh guess, while an
  open choice may *resolve* after its content token.
- **B4 (manipulation check).** AUC_LEN(U vs OL) ≤ 0.70 in at least 3 of 4. OL removes the length confound.

## What each outcome points to

- **B0 fails:** the replication is broken. Find out why before reading anything else.
- **B1 holds:** this is the border, measured. The hatch's scalar confounds the two kinds of uncertainty. Yupi then
  asks what *does* separate them: the profile (B3), or a second query (sampled consistency, the next arm).
- **B1 fails:** real models separate fabrication from open answers by mean entropy, where Yupana's exact one-step
  ceiling says entropy alone mixes the two. Something in LLMs carries the distinction that a next-event law does not.
  That would be the more interesting outcome.
- **B4 fails:** the open-long responses are too short to test B1 cleanly. Read B1 together with LEN.
