"""Pins for the EXPLORATORY corpus track at the frozen law (40,8,2), looping
C1′, thread naming, both ε (`docs/corpus-track-40-8-2-note-v0.1.md`;
Part II v0.2.9 proposed, not enacted): the raws carry the external gate,
the pattern classes coarsen the canonical windows except at r0 where Π is
the identity, the canonical column equals the thirty artifacts' pinned
values, and the corpus quantities are pinned to four decimals."""
import json
import pathlib

import pytest

DOCS = pathlib.Path(__file__).parent.parent / "docs"
CANON = {"r0": 12739, "r1": 819073, "r2": 923461, "r3": 991585, "r4": 1524612}
CLASSES = {"r0": 12739, "r1": 316444, "r2": 499899, "r3": 569985, "r4": 908234}
PINS = {  # (eps, rung): (canonical H(S|w), H(q|Πw), H(q\pc|Πw), H(β|Πw), H(S|Πw), Q2[named0], Q2[unseen])
    ("1", "r0"): (3.9474, 3.3082, 1.7899, 0.0, 3.9474, 1.3609, 1.3609),
    ("1", "r1"): (0.6008, 1.6674, 0.7372, 1.6772, 2.0965, 0.0387, 0.2282),
    ("1", "r2"): (0.5277, 1.2736, 0.4006, 1.3417, 1.7173, 0.0107, 0.1709),
    ("1", "r3"): (0.4046, 1.0707, 0.1977, 1.2619, 1.5264, 0.0000, 0.1257),
    ("1", "r4"): (0.3898, 1.0507, 0.1794, 1.2567, 1.5065, 0.0000, 0.1107),
    ("1/2", "r0"): (3.3711, 3.0766, 2.5324, 0.0, 3.3711, 1.3694, 1.3694),
    ("1/2", "r1"): (0.2963, 1.2747, 1.0796, 1.1877, 1.4659, 0.0286, 0.1404),
    ("1/2", "r2"): (0.2400, 0.9778, 0.8015, 0.9455, 1.1801, 0.0056, 0.0910),
    ("1/2", "r3"): (0.1774, 0.8343, 0.6580, 0.8646, 1.0366, 0.0000, 0.0654),
    ("1/2", "r4"): (0.1658, 0.8161, 0.6406, 0.8580, 1.0185, 0.0000, 0.0524),
}


@pytest.mark.parametrize("tag,eps", [("", "1"), ("-eps1_2", "1/2")])
def test_corpus_track_pinned(tag, eps):
    d = json.load(open(DOCS / f"c1prime-loop-corpus-track-40-8-2-2026-09-13{tag}.json"))
    assert d["law"] == dict(T_ep=40, L=8, B=2) and d["programs"] == "c1prime-loop" and d["status"].startswith("EXPLORATORY")
    assert [r["rung"] for r in d["rows"]] == ["r0", "r1", "r2", "r3", "r4"]
    for r in d["rows"]:
        assert r["eps"] == eps and r["gate"].count("full") == 8 and r["status"].startswith("EXPLORATORY")
        assert r["n_windows_canonical"] == CANON[r["rung"]] and r["n_pattern_classes"] == CLASSES[r["rung"]]
        c, k = r["corpus"], r["canonical"]
        got = (k["mean_state_entropy_bits"], c["H_quotient_given_pattern"], c["H_quotient_no_pc_given_pattern"],
               c["H_binding_given_pattern"], c["H_S_given_pattern"], c["Q2"]["named0"], c["Q2_unseen"])
        assert tuple(round(x, 4) for x in got) == PINS[(eps, r["rung"])], r["rung"]
        if r["rung"] == "r0":                       # Π is the identity at r0
            assert c["H_S_given_pattern"] == k["mean_state_entropy_bits"] and c["H_binding_given_pattern"] == 0.0
        assert c["H_quotient_no_pc_given_pattern"] <= c["H_quotient_given_pattern"] + 1e-12
        assert abs(sum(c["law_mass_by_named_count"].values()) - 1) < 1e-12


def test_canonical_column_equals_the_thirty_artifacts():
    """The canonical H(S|w) column is the thirty artifacts' value at every (rung, ε)."""
    for tag in ("", "-eps1_2"):
        d = json.load(open(DOCS / f"c1prime-loop-corpus-track-40-8-2-2026-09-13{tag}.json"))
        for r in d["rows"]:
            (f,) = [p for p in DOCS.glob(f"c1prime-loop-query-ceilings-40-8-2-{r['rung']}-????-??-??{tag}.json")]
            (a,) = json.load(open(f))["rows"]
            assert abs(a["mean_state_entropy_bits"] - r["canonical"]["mean_state_entropy_bits"]) < 1e-9, (tag, r["rung"])
            assert abs(a["queries"]["Q2[T0]"]["mean_bits"] - r["canonical"]["Q2"]["T0"]) < 1e-9
