"""Declared: docs/escape-hatch-open-declared-2026-10-27.md (stamped before running).

Arm B: exp27's four models and its knowable and unknowable queries, plus determined-but-open queries
(scripts/open_queries.py). Greedy decoding, 150 tokens, exp27's system prompt and chat formatting; the per-token
entropy (nats, as exp27) of every generated token is kept, so profiles can be scored.

  uv run --project ~/projects/ai-honesty python scripts/escape_hatch_open.py --out DIR [--models Llama Qwen ...]

(Run in ai-honesty's environment: Yupi's own environment stays free of pretrained-model code.)
"""
import argparse
import gc
import importlib.util
import json
import sys
from pathlib import Path

import torch
import torch.nn.functional as F
from transformers import AutoModelForCausalLM, AutoTokenizer

sys.path.insert(0, str(Path(__file__).parent))
from open_queries import OPEN_LONG, OPEN_SHORT  # noqa: E402

EXP27 = Path.home() / "projects/ai-honesty/scripts/experiment27_bounded_verification.py"
spec = importlib.util.spec_from_file_location("exp27", EXP27)
exp27 = importlib.util.module_from_spec(spec); spec.loader.exec_module(exp27)


@torch.no_grad()
def generate(model, tok, prompt, max_tokens=150):
    inputs = tok(prompt, return_tensors="pt").to(model.device)
    out = model.generate(**inputs, max_new_tokens=max_tokens, do_sample=False, pad_token_id=tok.eos_token_id,
                         output_scores=True, return_dict_in_generate=True)
    ids = out.sequences[0, inputs.input_ids.shape[1]:]
    ents = []
    for s in out.scores:
        lp = F.log_softmax(s.squeeze(0).float(), dim=-1)
        ents.append(float(-(lp.exp() * lp).sum()))
    return tok.decode(ids, skip_special_tokens=True).strip(), ents, [int(i) for i in ids]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--models", nargs="*", default=None)
    ap.add_argument("--limit", type=int, default=None, help="smoke test: first N queries per set")
    a = ap.parse_args()
    outdir = Path(a.out); outdir.mkdir(parents=True, exist_ok=True)
    sets = [("knowable", [q for q, _ in exp27.KNOWABLE_QUERIES]), ("unknowable", [q for q, _ in exp27.UNKNOWABLE_QUERIES]),
            ("open_short", OPEN_SHORT), ("open_long", OPEN_LONG)]
    for family, model_id in exp27.MODELS:
        if a.models and family not in a.models:
            continue
        path = outdir / f"{family}.jsonl"
        if path.exists():
            print("skip (exists)", path, flush=True); continue
        kw = {"fix_mistral_regex": True} if model_id in exp27.MISTRAL_MODELS else {}
        tok = AutoTokenizer.from_pretrained(model_id, **kw)
        model = AutoModelForCausalLM.from_pretrained(model_id, torch_dtype=torch.float16, device_map="cuda")
        tmp = path.with_suffix(".partial")
        with open(tmp, "w") as f:
            for cat, qs in sets:
                for i, q in enumerate(qs[:a.limit]):
                    resp, ents, ids = generate(model, tok, exp27.format_chat(exp27.SYSTEM_PROMPT, q, tok))
                    f.write(json.dumps(dict(family=family, model_id=model_id, category=cat, query=q, response=resp,
                                            entropies=ents, token_ids=ids)) + "\n")
                    if i % 25 == 0:
                        print(family, cat, i, len(ents), flush=True)
        tmp.rename(path)
        del model, tok; gc.collect(); torch.cuda.empty_cache()


if __name__ == "__main__":
    main()
