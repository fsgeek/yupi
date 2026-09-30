"""Pairing check for the relay corpus (relay design v0.1 §2 item 4): same episodes and
windows as the r1 corpus; dropping the relay slot reproduces r1 token for token; the
relay slot is the relay recomputed from the r1 tokens."""
import sys
from fractions import Fraction
from pathlib import Path

import numpy as np

from yupi.corpus.manifest import Manifest, Split
from yupi.corpus.writer import generate

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import relay_corpus_check as C  # noqa: E402

KEY = bytes(range(32))


def _pair(tmp_path, law=(40, 8, 2)):
    out = {}
    for rung in ("r1", "r1R"):
        m = Manifest.new(programs="c1prime-loop", epsilon=Fraction(1), T_ep=law[0], L=law[1], B=law[2], rung=rung,
                         run_key=KEY, splits=(Split("train", 0, 300), Split("test", 2_000_000, 2_000_200)),
                         git_commit="t")
        out[rung], _ = generate(m, tmp_path, workers=1)
    return out["r1"], out["r1R"]


def test_pairing_passes_on_a_true_pair(tmp_path):
    d1, dr = _pair(tmp_path)
    rep = C.check_split(d1, dr, "test")
    assert rep == dict(split="test", n_r1=200, n_r1R=200, lengths_equal=True, tables_identical=True,
                       drop_relay_equals_r1=True, relay_recomputed_equal=True,
                       n_windows_with_a_kind_relay=rep["n_windows_with_a_kind_relay"], passed=True)
    assert rep["n_windows_with_a_kind_relay"] > 150
    assert C.check_manifests(d1, dr)["passed"]


def test_pairing_fails_on_a_changed_relay_token(tmp_path):
    d1, dr = _pair(tmp_path)
    raw = np.fromfile(dr / "test.tokens", dtype="<u2").reshape(200, 41)
    from yupi.corpus.vocab import TOKEN_ID
    row = next(i for i in range(200) if raw[i, 0] != TOKEN_ID["RESET"])
    raw[row, 2] = TOKEN_ID["IDLE"] if raw[row, 2] != TOKEN_ID["IDLE"] else TOKEN_ID["STEP"]
    raw.tofile(dr / "test.tokens")
    rep = C.check_split(d1, dr, "test")
    assert rep["drop_relay_equals_r1"] and not rep["relay_recomputed_equal"] and not rep["passed"]


def test_pairing_fails_on_a_changed_non_relay_token(tmp_path):
    d1, dr = _pair(tmp_path)
    raw = np.fromfile(dr / "test.tokens", dtype="<u2").reshape(200, 41)
    raw[5, 0] = raw[5, 0] + 1 if raw[5, 0] != 0 else 3
    raw.tofile(dr / "test.tokens")
    assert not C.check_split(d1, dr, "test")["passed"]
