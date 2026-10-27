"""Declared: docs/open-factual-declared-2026-10-27.md (stamped before running).

Arm B2: open-factual queries ("Name a novel by X") on exp27's four models, scored against frozen Wikidata answer sets
(docs/open-factual-2026-10-27/answer-sets.json). Same decoding and entropy capture as scripts/escape_hatch_open.py.

  uv run --project ~/projects/ai-honesty python scripts/open_factual.py --sets FILE --out DIR [--models ...] [--limit N]
"""
import argparse
import gc
import json
import sys
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

sys.path.insert(0, str(Path(__file__).parent))
from escape_hatch_open import exp27, generate  # noqa: E402

PROMPT = {"novel": "Name a novel by {e}.", "film": "Name a film directed by {e}.", "album": "Name an album by {e}."}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sets", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--models", nargs="*", default=None)
    ap.add_argument("--limit", type=int, default=None)
    a = ap.parse_args()
    rows = json.load(open(a.sets))["rows"][:a.limit]
    outdir = Path(a.out); outdir.mkdir(parents=True, exist_ok=True)
    for family, model_id in exp27.MODELS:
        if a.models and family not in a.models:
            continue
        path = outdir / f"{family}.jsonl"
        if path.exists():
            print("skip (exists)", path, flush=True); continue
        kw = {"fix_mistral_regex": True} if model_id in exp27.MISTRAL_MODELS else {}
        tok = AutoTokenizer.from_pretrained(model_id, **kw)
        model = AutoModelForCausalLM.from_pretrained(model_id, dtype=torch.float16, device_map="cuda")
        tmp = path.with_suffix(".partial")
        with open(tmp, "w") as f:
            for i, r in enumerate(rows):
                q = PROMPT[r["relation"]].format(e=r["entity"])
                resp, ents, ids = generate(model, tok, exp27.format_chat(exp27.SYSTEM_PROMPT, q, tok))
                f.write(json.dumps(dict(family=family, relation=r["relation"], qid=r["qid"], entity=r["entity"], query=q,
                                        response=resp, entropies=ents, token_ids=ids)) + "\n")
                if i % 20 == 0:
                    print(family, i, flush=True)
        tmp.rename(path)
        del model, tok; gc.collect(); torch.cuda.empty_cache()


if __name__ == "__main__":
    main()
