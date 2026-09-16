"""Corpus files (design v0.1 §5): <split>.tokens is uint16 little-endian,
windows back to back each padded to max_tokens with PAD (id 0);
<split>.index is uint32 little-endian unpadded lengths; <split>.table.jsonl
is one JSON line per window's episode (episode id, T, U, the four
injections). Byte-deterministic given the manifest, for any worker count:
workers take contiguous seed ranges and the parent concatenates in order.
"""
from __future__ import annotations

import json
import struct
from multiprocessing import Pool
from pathlib import Path

from yupi.corpus.manifest import Manifest, Split, validate
from yupi.corpus.rendering import EpisodeTable
from yupi.corpus.vocab import TOKEN_ID, VOCAB
from yupi.corpus.windows import draw_window, serialize


def encode_window(m: Manifest, episode_id: int):
    """(padded uint16-LE token bytes, unpadded length, table json) for one episode."""
    cfg, progs = m.world()
    table = EpisodeTable.draw(m.run_key(), episode_id, cfg, m.lift_reservation)
    w = draw_window(cfg, progs, m.law(), m.rung, m.run_key(), episode_id)
    ids = [TOKEN_ID[t] for t in serialize(w, table)]
    length = len(ids)
    ids.extend([0] * (m.max_tokens - length))
    blob = struct.pack(f"<{m.max_tokens}H", *ids)
    return blob, length, {**table.to_json(), "T": w.T, "U": w.U}


def _chunk(args):
    m_json, start, end = args
    m = Manifest.from_json(m_json)
    cfg, progs = m.world()
    law, key = m.law(), m.run_key()
    toks, lens, lines = [], [], []
    for ep in range(start, end):
        table = EpisodeTable.draw(key, ep, cfg, m.lift_reservation)
        w = draw_window(cfg, progs, law, m.rung, key, ep)
        ids = [TOKEN_ID[t] for t in serialize(w, table)]
        length = len(ids)
        ids.extend([0] * (m.max_tokens - length))
        toks.append(struct.pack(f"<{m.max_tokens}H", *ids))
        lens.append(length)
        lines.append(json.dumps({**table.to_json(), "T": w.T, "U": w.U}, separators=(",", ":"), sort_keys=True))
    return b"".join(toks), struct.pack(f"<{len(lens)}I", *lens), "".join(l + "\n" for l in lines)


def write_split(m: Manifest, split: Split, out_dir: Path, workers: int = 1) -> int:
    n = split.seed_end - split.seed_start
    step = max(1, -(-n // max(1, workers * 4)))          # ~4 chunks per worker, contiguous, in order
    ranges = [(m.to_json(), s, min(s + step, split.seed_end)) for s in range(split.seed_start, split.seed_end, step)]
    if workers > 1 and len(ranges) > 1:
        with Pool(workers) as pool:
            parts = pool.map(_chunk, ranges)
    else:
        parts = [_chunk(r) for r in ranges]
    with open(out_dir / f"{split.name}.tokens", "wb") as ft, open(out_dir / f"{split.name}.index", "wb") as fi, \
            open(out_dir / f"{split.name}.table.jsonl", "w") as fj:
        for t, i, j in parts:
            ft.write(t)
            fi.write(i)
            fj.write(j)
    return n


def read_split(out_dir: Path, name: str):
    """[(unpadded token-id tuple, table dict)] in episode order."""
    out_dir = Path(out_dir)
    raw = (out_dir / f"{name}.tokens").read_bytes()
    idx = (out_dir / f"{name}.index").read_bytes()
    lens = list(struct.unpack(f"<{len(idx) // 4}I", idx))
    tables = [json.loads(l) for l in (out_dir / f"{name}.table.jsonl").read_text().splitlines()]
    if len(tables) != len(lens):
        raise ValueError(f"{name}: {len(lens)} lengths but {len(tables)} table lines")
    mt = len(raw) // (2 * len(lens)) if lens else 0
    out = []
    for k, (length, table) in enumerate(zip(lens, tables)):
        ids = struct.unpack(f"<{mt}H", raw[2 * mt * k: 2 * mt * (k + 1)])
        out.append((ids[:length], table))
    return out


def generate(m: Manifest, root: Path, workers: int = 1):
    """Write the whole corpus under root/<name>/<run_id>/; returns (dir, manifest with counts)."""
    validate(m)
    d = Path(root) / m.name() / m.run_id()
    d.mkdir(parents=True, exist_ok=True)
    (d / "vocab.json").write_text(json.dumps({t: i for i, t in enumerate(VOCAB)}, indent=0) + "\n")
    counts = {s.name: write_split(m, s, d, workers) for s in m.splits}
    m2 = m.with_counts(counts)
    (d / "manifest.json").write_text(json.dumps(m2.to_json(), indent=2, sort_keys=True) + "\n")
    return d, m2
