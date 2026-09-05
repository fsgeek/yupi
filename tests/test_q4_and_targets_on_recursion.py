"""The Q4 ceilings and predictive-targets producers on the recursion
(YUPI_AGG=window via `yupi.aggregation`): same rows as path aggregation
at a small law, and each reproduces its committed corrected (14,4,2)
artifact row for row. Written before the refactor (2026-09-04)."""
import importlib.util
import json
import pathlib
from fractions import Fraction

import pytest

from yupi.config import WorldConfig
from yupi.programs import c1_programs
from yupi.window import WindowLaw

ROOT = pathlib.Path(__file__).parent.parent
DOCS = ROOT / "docs"


def _load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m


q4 = _load("c1_q4_ceilings")
pt = _load("c1_predictive_targets")


def _close(a, b, tol=1e-9):
    if isinstance(a, dict):
        assert set(a) == set(b), (set(a) ^ set(b))
        return all(_close(a[k], b[k], tol) for k in a)
    if isinstance(a, float) or isinstance(b, float):
        return abs(a - b) <= tol
    return a == b


def test_q4_modes_agree_at_8_4_2():
    cfg, progs, law = WorldConfig.c1(epsilon=Fraction(1, 2)), c1_programs(), WindowLaw(T_ep=8, L=4, B=2)
    a = q4.compute_rows(law, 4, Fraction(1, 2), cfg, progs, ("r1", "r4"), agg="paths")
    b = q4.compute_rows(law, 4, Fraction(1, 2), cfg, progs, ("r1", "r4"), agg="window")
    for x, y in zip(a, b):
        assert x["rung"] == y["rung"] and x["n_windows"] == y["n_windows"]
        assert _close({k: v for k, v in x.items() if isinstance(v, (float, dict))},
                      {k: v for k, v in y.items() if isinstance(v, (float, dict))})


@pytest.mark.parametrize("eps", [Fraction(1), Fraction(1, 2)])
def test_q4_recursion_reproduces_committed_14_4_2_W4(eps):
    d = json.load(open(DOCS / "c1-q4-ceilings-14-4-2-W4-corrected-2026-08-20.json"))
    rows = q4.compute_rows(WindowLaw(T_ep=14, L=4, B=2), 4, eps, WorldConfig.c1(epsilon=eps), c1_programs(),
                           ("r1", "r2", "r3", "r4"), agg="window")
    for r in rows:
        c = next(x for x in d["rows"] if x["eps"] == str(eps) and x["rung"] == r["rung"])
        for k in ("n_windows", "n_states"):
            assert r[k] == c[k], (k, r["rung"])
        for k in ("total_bits", "irreducible_bits", "gap_bits", "none_mass"):
            assert abs(r[k] - c[k]) < 1e-9, (k, r["rung"])
        assert _close(r["by_endpoint"], c["by_endpoint"])


def test_targets_modes_agree_at_8_4_2():
    cfg, progs, law = WorldConfig.c1(epsilon=Fraction(1)), c1_programs(), WindowLaw(T_ep=8, L=4, B=2)
    a = pt.compute_rows(law, Fraction(1), cfg, progs, ("r1", "r4"), agg="paths")
    b = pt.compute_rows(law, Fraction(1), cfg, progs, ("r1", "r4"), agg="window")
    for x, y in zip(a, b):
        assert x["rung"] == y["rung"] and x["n_windows"] == y["n_windows"] and x["n_pnext_classes"] == y["n_pnext_classes"]
        assert _close(x["means"], y["means"]) and _close(x["divergent"], y["divergent"])


@pytest.mark.parametrize("eps", [Fraction(1), Fraction(1, 2)])
def test_targets_recursion_reproduces_committed_14_4_2(eps):
    d = json.load(open(DOCS / "c1-predictive-targets-14-4-2-corrected-2026-08-20.json"))
    rows = pt.compute_rows(WindowLaw(T_ep=14, L=4, B=2), eps, WorldConfig.c1(epsilon=eps), c1_programs(),
                           ("r1", "r2", "r3", "r4"), agg="window")
    for r in rows:
        c = next(x for x in d["rows"] if x["eps"] == str(eps) and x["rung"] == r["rung"])
        assert r["n_windows"] == c["n_windows"] and r["n_pnext_classes"] == c["n_pnext_classes"]
        assert _close(r["means"], c["means"]) and _close(r["divergent"], c["divergent"])
