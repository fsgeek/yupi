# Arm B, where the escape hatch stops: result (2026-10-27)

> Declared in `escape-hatch-open-declared-2026-10-27.md` (stamped 721bbda before running). The scorer
> (`scripts/escape_hatch_open_score.py`) was written and checked on synthetic data before the run. Data:
> `~/.cache/yupi-scratch/escape-hatch-2026-10-27/full/{OLMo,Llama,Qwen,Mistral}.jsonl` (per-token entropies of every
> response); scores in `escape-hatch-open-2026-10-27.json`. The run used Hamut'ay's GPU lease; the resident's server
> was confirmed back afterwards.

## Declared predictions

| | OLMo | Llama | Qwen | Mistral | verdict |
|---|---|---|---|---|---|
| B0: AUC_MEAN(U vs K) ≥ 0.80 | 0.894 | 0.922 | 0.896 | 0.905 | **held 4/4**, replicating exp27 |
| B1: AUC_MEAN(U vs OL) ≤ 0.70 | 0.157 | 0.424 | 0.038 | 0.257 | **held 4/4, and inverted in all four** |
| B2: AUC_MEAN(OS vs K) ≥ 0.70 | 0.759 | 0.796 | 0.677 | 0.795 | **held 3/4** (Qwen 0.677) |
| B3: RESOLVE further from ½ than MEAN, U vs OL | 0.281 | 0.452 | 0.159 | 0.343 | **failed 0/4** |
| B4: AUC_LEN(U vs OL) ≤ 0.70 | 0.548 | 0.351 | 0.412 | 0.346 | **held 4/4**: length does not explain B1 |

## What it shows

**Per-token entropy orders the categories K < OS < U < OL in every model.** The median mean entropy (nats) is:

| | knowable | open-short | unknowable | open-long |
|---|---|---|---|---|
| OLMo | 0.24 | 0.48 | 0.80 | 1.14 |
| Llama | 0.16 | 0.45 | 0.63 | 0.71 |
| Qwen | 0.03 | 0.10 | 0.32 | 0.74 |
| Mistral | 0.28 | 0.51 | 0.63 | 0.79 |

Correct free-form answers ("describe a sunset") carry *more* entropy than responses to unanswerable questions. Set a
threshold that catches 80 % of unknowable responses (post hoc), and it also flags:

| | knowable | open-short | open-long |
|---|---|---|---|
| OLMo | 0.17 | 0.38 | 0.94 |
| Llama | 0.15 | 0.40 | 0.88 |
| Qwen | 0.15 | 0.28 | 1.00 |
| Mistral | 0.17 | 0.50 | 0.88 |

**Post hoc, fabrications only** (refusals removed by exp27's markers): AUC_MEAN(fabrication vs OL) is 0.162 (OLMo),
0.656 (Llama), 0.053 (Qwen) and 0.304 (Mistral). The inversion is not carried by refusals, except partly in Llama,
where 73 % of unknowable responses are refusals.

**B3, the profile, failed, and the test was weak.** MEAN was already far from ½, in the wrong direction. The
Yupana signature (hidden state resolves, randomness persists) did not give RESOLVE any extra separation here.

## Where the hatch stops

The tensor interface's scalar measures how many continuations are acceptable. On single-answer facts that tracks
grounding. Once the query mix includes questions with many correct answers, it does not. The order K < U < OL means
no single entropy threshold catches fabrication without flagging most correct free-form answers. The paper itself
anticipated this in words ("Entropy thresholds tuned on the balanced set will not transfer directly", ai-honesty
`arxiv/main.tex` l. 1007). This measures it: open-long answers are flagged at 88–100 %.

This is the border Yupi was built to find. Yupana predicted it in exact form: a one-step entropy separates
randomness from hidden state only when randomness is limited. Here the randomness is legitimate creativity, and it
dominates.

## What it points to

1. **Arm A's repair was "ask a second question".** For LLMs the analogue must separate "many answers are right" from
   "the answer isn't known". Candidates: sample several answers and check whether they *agree on facts* while
   differing in wording (semantic consistency). Or probe the model with a follow-up about an asserted entity's
   existence. Both should be declared before running.
2. **Partial support** said that knowing the common laws buys most of the certification. Here, that is knowing
   which *kind* of query this is. A query-type prior (open vs closed) could restore the hatch. That is cheap to test
   on this data: AUC within the open category and within the closed category.
3. **For ai-honesty:** this qualifies the 0.870, which holds on single-answer queries only. It is Tony's paper.
   The result is recorded here, and he decides where it goes.
