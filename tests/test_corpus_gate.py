"""Design v0.1 §8 gates 2–4 at C1 (8, 4, 2): slow at N = 10^5 per cell; the
script's committed raw at N = 10^6 is pinned once it exists (Task 8)."""
import sys
from fractions import Fraction
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import corpus_gate as Gt  # noqa: E402


def test_exact_pattern_aggregate_matches_the_lemma_construction():
    from yupi.config import WorldConfig
    from yupi.programs import c1_programs
    from yupi.window import WindowLaw
    agg = Gt.exact_pattern_aggregate(WorldConfig.c1(), c1_programs(), WindowLaw(8, 4, 2), "r1")
    assert len(agg) == 207
    assert sum((sum(v.values(), Fraction(0)) for v in agg.values()), Fraction(0)) == 1
    assert sum(m for (reset, _), v in agg.items() for m in v.values() if reset) == Fraction(1, 2)


@pytest.mark.slow
@pytest.mark.parametrize("eps,rung", [(Fraction(1), "r1"), (Fraction(1), "r3"), (Fraction(1, 2), "r1"),
                                      (Fraction(1, 2), "r3"), (Fraction(1), "r4")])
def test_gates_2_3_4_at_1e5(eps, rung, tmp_path):
    rep = Gt.run_gate(eps, rung, n_windows=100_000, root=tmp_path, workers=8, h_tol=0.03)
    assert rep["passed"], {k: v for k, v in rep.items() if k.startswith("g")}


def test_committed_gate_raw_passed_at_1e6():
    """The committed raw of the 10^6-window gate run (design §8 gates 2–4)."""
    import json
    raws = sorted((Path(__file__).resolve().parents[1] / "docs").glob("corpus-gate-8-4-2-*.json"))
    assert raws, "no committed gate raw"
    doc = json.loads(raws[-1].read_text())
    assert doc["n"] == 1_000_000 and doc["all_passed"]
    cells = {(c["eps"], c["rung"]): c for c in doc["cells"]}
    assert set(cells) == {("1", "r1"), ("1", "r3"), ("1", "r4"), ("1/2", "r1"), ("1/2", "r3")}
    for c in cells.values():
        assert c["g2_tv"] <= c["g2_tv_bound"] and c["g2_missing_above_1e4"] == 0 and c["g2_unknown_classes"] == 0
        assert c["K_empirical"] == c["K_exact"]
        assert c["g3_reserved_hits"] == 0
        if c["g4_hq_pinned"] is not None:
            assert abs(c["g4_hq_hat"] - c["g4_hq_pinned"]) <= 0.01
