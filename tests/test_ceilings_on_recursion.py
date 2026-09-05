"""`scripts/c1_query_ceilings.py` on the window-process recursion
(YUPI_AGG=window; freeze note §5 item 3, handoff item 3): the statutory
producer must give the SAME rows from the recursion as from path
aggregation wherever both can run, and must reproduce a committed
corrected artifact row for row; its inline gate compares each window's
state marginal and law mass with the exact filter (what the sharded gate
does); an external gate mode is refused unless the gated shard raws for
(law, rung, ε) exist with zero mismatches. Written before the refactor."""
import importlib.util
import json
import pathlib
from fractions import Fraction

import pytest

from yupi.config import WorldConfig
from yupi.programs import c1_programs, c1_prime_loop_programs
from yupi.window import WindowLaw

_spec = importlib.util.spec_from_file_location(
    "c1_query_ceilings", pathlib.Path(__file__).parent.parent / "scripts" / "c1_query_ceilings.py")
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
compute_rows = _mod.compute_rows
DOCS = pathlib.Path(__file__).parent.parent / "docs"


def _close(a, b, tol=1e-9):
    if isinstance(a, dict):
        assert set(a) == set(b), (set(a) ^ set(b))
        return all(_close(a[k], b[k], tol) for k in a)
    if isinstance(a, float) or isinstance(b, float):
        return abs(a - b) <= tol
    return a == b


def test_recursion_and_paths_agree_at_8_4_2():
    cfg, progs, law = WorldConfig.c1(epsilon=Fraction(1, 2)), c1_programs(), WindowLaw(T_ep=8, L=4, B=2)
    by_paths = compute_rows(law, Fraction(1, 2), cfg, progs, ("r1", "r2", "r3", "r4"), agg="paths", gate="inline")
    by_rec = compute_rows(law, Fraction(1, 2), cfg, progs, ("r1", "r2", "r3", "r4"), agg="window", gate="inline")
    assert len(by_paths) == len(by_rec) == 4
    for a, b in zip(by_paths, by_rec):
        assert a["rung"] == b["rung"] and a["n_windows"] == b["n_windows"]
        assert _close(a["queries"], b["queries"]) and _close(a["by_endpoint"], b["by_endpoint"])
        assert abs(a["mean_state_entropy_bits"] - b["mean_state_entropy_bits"]) < 1e-9


@pytest.mark.parametrize("eps", [Fraction(1), Fraction(1, 2)])
def test_recursion_reproduces_the_committed_14_4_2_artifact(eps):
    d = json.load(open(DOCS / "c1-query-ceilings-14-4-2-corrected-2026-08-20.json"))
    rows = compute_rows(WindowLaw(T_ep=14, L=4, B=2), eps, WorldConfig.c1(epsilon=eps), c1_programs(),
                        ("r1", "r2", "r3", "r4"), agg="window", gate="inline")
    for r in rows:
        c = next(x for x in d["rows"] if x["eps"] == str(eps) and x["rung"] == r["rung"])
        assert r["n_windows"] == c["n_windows"]
        assert abs(r["mean_state_entropy_bits"] - c["mean_state_entropy_bits"]) < 1e-9
        assert _close(r["queries"], c["queries"]) and _close(r["by_endpoint"], c["by_endpoint"])
        assert r["gate"] == "inline-marginal"


def test_r0_can_be_requested_and_is_coarser_than_r1():
    cfg, progs, law = WorldConfig.c1(epsilon=Fraction(1)), c1_programs(), WindowLaw(T_ep=8, L=4, B=2)
    rows = compute_rows(law, Fraction(1), cfg, progs, ("r0", "r1"), agg="window", gate="inline")
    assert [r["rung"] for r in rows] == ["r0", "r1"]
    assert rows[0]["mean_state_entropy_bits"] > rows[1]["mean_state_entropy_bits"]
    assert rows[0]["queries"]["Q1[L0]"]["mean_bits"] >= rows[1]["queries"]["Q1[L0]"]["mean_bits"]


def test_external_gate_is_refused_without_gated_raws(tmp_path):
    cfg, progs, law = WorldConfig.c1(epsilon=Fraction(1)), c1_prime_loop_programs(), WindowLaw(T_ep=8, L=4, B=2)
    with pytest.raises(RuntimeError, match="not gated"):
        compute_rows(law, Fraction(1), cfg, progs, ("r4",), agg="window", gate="external", docs_dir=tmp_path)
