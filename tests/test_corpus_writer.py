"""Design v0.1 §5 layout, gate 1 determinism (worker-count invariant), read-back."""
import filecmp
import json
from fractions import Fraction

from yupi.corpus import manifest as M
from yupi.corpus import writer as Wr
from yupi.corpus.rendering import EpisodeTable
from yupi.corpus.vocab import PAD, TOKEN_ID, VOCAB
from yupi.corpus.windows import deserialize, draw_window

KEY = bytes(range(32))


def _m(n=60):
    return M.Manifest.new(programs="c1", epsilon=Fraction(1), T_ep=8, L=4, B=2, rung="r3", run_key=KEY,
                          splits=(M.Split("train", 0, n), M.Split("val", 1_000_000, 1_000_000 + 12)),
                          git_commit="test")


def test_encode_window_layout():
    m = _m()
    blob, length, table = Wr.encode_window(m, 5)
    assert len(blob) == 2 * m.max_tokens and 0 < length <= m.max_tokens
    ids = list(memoryview(blob).cast("H"))               # host is little-endian; the writer forces LE
    assert all(i == TOKEN_ID[PAD] for i in ids[length:]) and TOKEN_ID[PAD] not in ids[:length]
    assert table["episode"] == 5 and table["T"] - table["U"] == length // 5 and set(table) >= {"thread", "lock", "device", "request"}


def test_generate_layout_counts_and_read_back(tmp_path):
    m = _m()
    d, m2 = Wr.generate(m, tmp_path, workers=1)
    assert d == tmp_path / m.name() / m.run_id()
    assert {p.name for p in d.iterdir()} == {"manifest.json", "vocab.json", "train.tokens", "train.index",
                                             "train.table.jsonl", "val.tokens", "val.index", "val.table.jsonl"}
    assert m2.counts == {"train": 60, "val": 12}
    assert json.loads((d / "manifest.json").read_text())["counts"] == m2.counts
    assert json.loads((d / "vocab.json").read_text()) == {t: i for i, t in enumerate(VOCAB)}
    rows = Wr.read_split(d, "train")
    assert len(rows) == 60
    cfg, progs = m.world()
    for (ids, table), ep in zip(rows, range(60)):
        t = EpisodeTable.from_json(table)
        w = draw_window(cfg, progs, m.law(), m.rung, KEY, ep)
        assert (table["T"], table["U"]) == (w.T, w.U)
        assert deserialize(tuple(VOCAB[i] for i in ids), t) == (w.reset, w.records)


def test_generation_is_byte_identical_across_runs_and_worker_counts(tmp_path):
    m = _m(n=97)
    a, _ = Wr.generate(m, tmp_path / "a", workers=1)
    b, _ = Wr.generate(m, tmp_path / "b", workers=4)
    for name in ("train.tokens", "train.index", "train.table.jsonl", "val.tokens", "val.index",
                 "val.table.jsonl", "manifest.json", "vocab.json"):
        assert filecmp.cmp(a / name, b / name, shallow=False), name
