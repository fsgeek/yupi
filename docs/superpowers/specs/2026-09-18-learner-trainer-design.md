# The learner, sub-project 2 — trainer and evaluator (design, 2026-09-18)

> **Status: design, decided by the researcher under the PI's delegation of
> 2026-09-13; the PI reverts it with one word.** Implements the contract
> `docs/learner-model-vs-ceiling-contract-v0.1.md` (v0.1.1). Adds no statute.
> Brainstormed alone on the trace (the clarifying questions the house skill
> would have asked are answered below from the record, with the reason);
> the plan follows in `docs/superpowers/plans/`.

## 1. Purpose

Train small decoder-only transformers from scratch on the ten (40, 8, 2)
window corpora and measure their excess over the pattern observer's exact
ceiling at the last record of the window (contract §2.1–2.2), with the
resolution the contract demands (§2.4). Everything from-scratch and
inspectable (CLAUDE.md: hardware and posture); the residual stream at
every layer must be reachable for sub-project 3's probes.

## 2. Questions answered from the trace

| Question | Answer | Reason on the trace |
|---|---|---|
| Own transformer or `nn.Transformer`? | **Own**, ~250 lines: embeddings, pre-LN blocks (causal attention + MLP), final LN, untied output head. | Probes need the residual stream per layer; "every component from-scratch and inspectable" (CLAUDE.md). A library layer hides exactly what paper 1's belief-geometry slice reads. |
| Size | d = 128, 4 layers, 4 heads, MLP 4d, learned positions over 42 slots → **≈ 0.85M parameters**. The first grid point; d ∈ {64, 128, 256} later (RQ5). | Contract: "~1M". Tokens per epoch 8.2M; ~5·10¹³ FLOPs per epoch. |
| Sequence framing | Input `[BOS] + window`, target `window + [PAD]`; one PAD target per window (the end-of-window event, contract §1 item 3), further PADs masked. BOS is a **model-side** input index 156; the output head is over the 156 corpus tokens and never predicts BOS. | The corpus vocabulary is pinned by test and shared by every corpus (D5); BOS is a trainer convention, not a vocabulary change. Without BOS the first token has no prediction and the RESET prior ($P(U=0)=0.2$) would be unmeasured. |
| Packing | None. One window per sequence, padded to 42. | Design v0.1 §2: a packed neighbour is evidence the law does not provide. |
| Loss | Mean token cross-entropy over unmasked targets. | The learner's own loss (Part II §2(a)); contract §2.3. |
| Optimizer / schedule | AdamW (β 0.9/0.95, wd 0.1 on matrices only), lr 1e-3 peak, linear warmup 500 steps then cosine to 1e-4; batch 256 windows; 10 epochs (~7,800 steps). Grad clip 1.0. | Standard small-LM recipe; nothing here is a claim. Val loss every 250 steps; the run stops at the epoch budget, not on val (no early-stopping optics). |
| Precision | fp32 on CPU; bf16 autocast on GPU with `torch.use_deterministic_algorithms(True)` and a fixed `CUBLAS_WORKSPACE_CONFIG`. | The lease memo: any GPU nondeterminism is measured, not hidden. |
| Seeds | One integer seed fixes init, data order and dropout (none used). Recorded in the run manifest. | Contract §2.4 pilot: three seeds on r4 ε=1 first. |
| Checkpoint / resume | Every 500 steps and on SIGTERM: model, optimizer, scheduler, step, epoch, data-order permutation seed and position, torch/CUDA RNG states, run manifest. Written to `<run>/ckpt.tmp` then fsync + atomic rename to `<run>/ckpt.pt`; previous checkpoint kept as `ckpt.prev.pt` until the new one is durable. **Resume gate** (test): 200 straight steps vs 100 + checkpoint + fresh process + 100 must give bit-identical parameters on CPU; on GPU the max abs parameter difference is reported. | The lease memo of 2026-09-15 (kill six minutes before expiry, 60 s grace; resume gate; retain-until-committed). |
| Where P* comes from | The ceiling tables (`yupi.pattern_ceiling`, JSON lines under `~/.cache/yupi-scratch/ceilings/`, sha256 in the committed raw), looked up by the test window's serial key. Interior positions: the prefix filter on a subsample. | Contract v0.1.1 ledger (b); 0.56–0.84 s/window through the filter. |
| Firewall | `yupi.learner.{data,model,train,checkpoint}` import **nothing** from the exact side but the corpus vocabulary; only `yupi.learner.evaluate` imports `naming`, `pattern_ceiling`, `pattern_filter`. | The model must not be able to see the ceiling; the evaluator must not be able to train. Tested by an import-graph test. |
| Dependencies | `torch`, `numpy` as an **optional group** `learner` (`uv sync --extra learner`). | The exact side stays torch-free and its suite unchanged. |

## 3. Components

```
src/yupi/learner/
  data.py        read a corpus split -> (inputs[N,42] int64, targets[N,42], mask[N,42]); BOS/PAD framing;
                 seeded epoch permutation; batches. No torch model here.
  model.py       Decoder(cfg): tok+pos embeddings, n_layer × Block(LN, causal MHA, LN, MLP), LN, head.
                 forward(ids, return_hidden=False) -> logits [N,T,156] (+ list of residual streams per layer).
  train.py       TrainConfig (dataclass, JSON-able), the loop, val loss, logging (JSON lines), lease-aware
                 SIGTERM -> checkpoint -> exit(0).
  checkpoint.py  save_atomic / load; RNG capture/restore; the resume protocol.
  evaluate.py    the contract's evaluator: per window, one forward pass; per field of the realized next
                 record at the headline position: P*(pattern value | Π-prefix) from the table's P*(Πr|Πw)
                 by marginalization, P̃_M(pattern value | surface prefix) by summing softmax entries over
                 the consistent token set; structural excess, naming excess, raw CE and its ceiling,
                 kind-level exact KL; means, standard deviations, standard errors; JSON raw.
scripts/
  learner_train.py     --corpus <manifest> --seed --out <run dir> [--device cpu|cuda] [--resume]
  learner_evaluate.py  --run <run dir> --table <jsonl> [--n 100000] -> docs/<raw>.json
```

**Data flow.** manifest → corpus dir → `read_split` (existing) → int arrays → batches → model → loss.
Evaluation: test split → per window: surface tokens → pattern window (Π_all on surface tokens by
token type; invariant under σ) → table lookup → P*; forward pass → conditionals → excesses.

**Error handling.** Refuse, never coerce (design v0.1 §9): a manifest whose vocabulary hash differs
from the code's; a table whose law/rung/ε differ from the corpus's; a test window whose class is
absent from the table (a finding, counted and reported, never skipped silently); a resume whose
manifest differs from the checkpoint's; GPU without deterministic algorithms enabled.

## 4. Testing (TDD, per the house)

- `data`: framing shape and masks on a hand-built window; exactly one PAD target per window; the
  permutation is a function of (seed, epoch); round trip through the corpus reader.
- `model`: causality (perturbing token j changes no logit at positions < j); parameter count within
  1% of the arithmetic; hidden states returned per layer with the right shapes.
- `train`: a 30-step run on a synthetic corpus lowers the loss; run manifest written; log lines parse.
- `checkpoint`: **the resume gate** (bit-identical on CPU); atomic write leaves `ckpt.prev.pt` intact
  on a simulated crash between tmp and rename.
- `evaluate`: the **synthetic Bayes model** (a fake model whose softmax at each field is P* spread
  uniformly over unused tokens) gives structural and naming excess exactly 0.0 (to 1e-9) on every
  test window of a small-law corpus; the **uniform model** gives structural excess equal to the known
  entropy gap; structural + naming = raw token excess per window to 1e-9; kind-level KL ≥ 0.
- Firewall: an import-graph test that `yupi.learner.{data,model,train,checkpoint}` never import
  `yupi.pattern_*`, `yupi.naming`, `yupi.window_*`, `yupi.kernel`.

A small-law corpus for the evaluator tests: C1 (8, 4, 2), 2,000 windows, generated by the existing
generator into a `tmp_path`, with its ceiling table from `ceiling_table` (seconds).

## 5. Runs

1. **Pilot** (contract §2.4): r4 ε=1, seeds {1, 2, 3}, CPU or GPU as available; between-seed sd of
   the mean structural excess sets the seed count (SE ≤ δ/3 ≈ 0.003 bits, floor 3).
2. **Sweep**: ten cells × the seed count; GPU through the lease
   (`ayllu-gpu run --holder yupi --purpose "<cell/seed>" --ttl 6h -- <cmd>`).
3. **Raw per run**: `docs/learner-eval-<cell>-seed<k>-<date>.json` (means, sd, SE, n, table sha256,
   checkpoint sha256, git commit); a summary table in a dated note.

## 6. Out of scope

Probes and belief-geometry alignment (sub-project 3). Model-size and data-volume grids (after the
pilot). Any law but the frozen one. The lexical-holdout corpus. TIME_CLASS.

## 7. Ledger

- 2026-09-18 10:50 PDT (from `date`): written after §4 items 1–4 of the contract landed the same morning; the
  ceiling-table producer for (40, 8, 2) running in the background (PID recorded in
  `~/.cache/yupi-scratch/ceilings/run-2026-09-18.log`).
