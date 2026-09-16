"""Design v0.1 §5 manifest and §9 refusals (each names its statute line)."""
from fractions import Fraction

import pytest

from yupi.corpus import manifest as M
from yupi.corpus.vocab import VOCAB_SHA256

KEY = bytes(range(32))


def _m(**kw):
    base = dict(programs="c1prime-loop", epsilon=Fraction(1, 2), T_ep=40, L=8, B=2, rung="r1",
                run_key=KEY, splits=(M.Split("train", 0, 100), M.Split("val", 1_000_000, 1_000_010),
                                     M.Split("test", 2_000_000, 2_000_010)), git_commit="deadbeef")
    base.update(kw)
    return M.Manifest.new(**base)


def test_new_manifest_fields_and_names():
    m = _m()
    assert m.name() == "c1prime-loop-40-8-2-r1-eps1_2"
    assert m.run_id() == "630dcd2966c43366"          # sha256(bytes(range(32)))[:16], computed once at execution
    assert m.max_tokens == 41 and m.epsilon == "1/2" and m.completion_p == "1/3"
    assert m.vocab_sha256 == VOCAB_SHA256 and m.generator_version == M.GENERATOR_VERSION
    cfg, progs = m.world()
    assert cfg.epsilon == Fraction(1, 2) and len(progs) == 4
    assert m.law().endpoints() == range(2, 41, 2)
    M.validate(m)


def test_json_round_trip_preserves_everything():
    m = _m().with_counts({"train": 100, "val": 10, "test": 10})
    assert M.Manifest.from_json(m.to_json()) == m
    assert m.run_key() == KEY


def test_refusals_name_the_statute():
    with pytest.raises(M.ManifestRefused, match=r"Part II §4"):
        M.validate(_m(rung="r5"))
    with pytest.raises(M.ManifestRefused, match=r"Part II §2\(a\)"):
        M.validate(_m(L=7))
    with pytest.raises(M.ManifestRefused, match=r"Part II §2\(a\)"):
        M.validate(_m(T_ep=41))
    with pytest.raises(M.ManifestRefused, match=r"design v0.1 §3"):
        M.validate(_m(lift_reservation=True))          # a reserved token in a training corpus
    with pytest.raises(M.ManifestRefused, match=r"design v0.1 §6"):
        M.validate(_m(splits=(M.Split("train", 0, 100), M.Split("val", 50, 60))))
    bad = M.Manifest.from_json({**_m().to_json(), "generator_version": "0.0.9"})
    with pytest.raises(M.ManifestRefused, match=r"design v0.1 §9"):
        M.validate(bad)
    bad = M.Manifest.from_json({**_m().to_json(), "pools": {"thread": 48, "lock": 32, "device": 16, "request": 32}})
    with pytest.raises(M.ManifestRefused, match=r"Part I D3"):
        M.validate(bad)
