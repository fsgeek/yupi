"""Pins for the r0 identity-residual check (2026-09-04, owed by Part II
proposal v0.2.7.1 statement 2; raw `docs/r0-identity-residual-14-2-2026-09-04.json`).

The census note `r0-ladder-census-v0.1.md` §2 said the r0 residual is "a
permutation entropy over kind-indistinguishable roles". The check
anonymizes every support state (threads replaced by their executed-kind
multiset, status and held locks; queue members and the live cursor by
those signatures) and asks whether the support is one anonymized form
with threads relabeled. It is, for about a fifth of the ambiguous mass at
ε = 1 and almost none at ε = ½; the rest differs in the anonymized
`threads` multiset — attribution of progress to threads whose programs
differ — which is structural, not naming. Values are pinned, not merely
bounded (feedback memory of 2026-08-29: a regression that only checks an
invariant the bug preserves cannot catch the bug).
"""
import json
import pathlib
from fractions import Fraction

from yupi.config import WorldConfig
from yupi.programs import c1_programs
from yupi.state import initial_state
import importlib.util

_spec = importlib.util.spec_from_file_location(
    "r0_identity_residual", pathlib.Path(__file__).parent.parent / "scripts" / "r0_identity_residual.py")
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
anonymize, thread_signature = _mod.anonymize, _mod.thread_signature

RAW = pathlib.Path(__file__).parent.parent / "docs" / "r0-identity-residual-14-2-2026-09-04.json"


def _row(eps, L):
    d = json.load(open(RAW))
    assert d["programs"] == "c1" and d["T_ep"] == 14 and d["B"] == 2
    return next(r for r in d["rows"] if r["eps"] == eps and r["L"] == L)


def test_identity_only_share_is_a_minority_at_eps_1():
    for L, share, n in ((4, 0.1790, 6), (8, 0.2050, 67), (12, 0.2164, 234), (14, 0.2164, 234)):
        r = _row("1", L)
        assert round(r["identity_only_share"], 4) == share and r["n_identity_only_windows"] == n
        assert r["non_identity_by_feature"]["threads"] > 0.1     # progress attribution dominates
    assert round(_row("1", 12)["non_identity_by_feature"]["threads"], 4) == 0.5156


def test_identity_only_share_is_near_zero_at_eps_half_because_the_cursor_is_live():
    for L, share in ((4, 0.0), (8, 0.0020), (12, 0.0054), (14, 0.0054)):
        r = _row("1/2", L)
        assert round(r["identity_only_share"], 4) == share
    r = _row("1/2", 12)
    assert round(r["non_identity_by_feature"]["cursor"], 4) == 0.2089      # cursor-only class
    assert round(r["non_identity_by_feature"]["cursor+threads"], 4) == 0.5529


def test_full_context_equals_L12_because_windows_coincide():
    for eps in ("1", "1/2"):
        assert _row(eps, 12) == {**_row(eps, 14), "L": 12}


def test_anonymized_form_ignores_the_cursor_only_when_it_is_inert():
    cfg, progs = WorldConfig.c1(epsilon=Fraction(1)), c1_programs()
    s = initial_state(cfg)
    assert "cursor" not in anonymize(s, progs, cursor_live=False)
    assert anonymize(s, progs, cursor_live=True)["cursor"] == thread_signature(s, progs, 0)
    # at reset every thread has executed nothing: the multiset has four empty prefixes
    assert all(sig[0] == () for sig in anonymize(s, progs, False)["threads"])
