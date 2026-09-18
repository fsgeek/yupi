"""The headline-position ceiling table: P*(Πr | Πw) and the law mass for
every pattern class of a (law, rung, ε), by the AGGREGATE route (learner
contract v0.1.1 ledger (b), 2026-09-18).

Route: the window-process pass (`window_process.window_law_aggregates`,
one r4 recursion projected to every rung), re-keyed by Π_all
(`naming.pattern_all`, the corpus-track producer's construction with all
four entity types), then one kernel step per support (S, β) with the
record projected to the rung and re-keyed through β by `extend_binding`.
Validated against `pattern_filter` class by class at (8, 4, 2)
(tests/test_pattern_ceiling.py); at the frozen law the gate is a random
sample of test windows through the filter (scripts/pattern_ceiling.py).

Serialization is exact (Fractions as "num/den" strings, JSON lines): the
evaluator loads the table and looks a test window's class up by its
serial key. Firewall: this module is on the recursive side (it imports
the window process and the kernel step); it never imports an enumerator.
"""
from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path
from typing import Dict, Iterable, Tuple

from yupi.config import WorldConfig
from yupi.interfaces import MASKED, project
from yupi.kernel import enabled
from yupi.naming import ENTITY_ORDER, extend_binding, pattern_all
from yupi.queries import entropy_bits
from yupi.records import Record, record_of
from yupi.window import WindowLaw
from yupi.window_process import prefix_law_aggregates, window_law_aggregates

Key = Tuple[bool, tuple]                     # (reset_observed, pattern window)
Entry = Tuple[Fraction, Dict[Record, Fraction]]   # (law mass, P*(Πr | Πw))
Table = Dict[Key, Entry]


def _moves(s, cfg, programs, rung, memo):
    m = memo.get(s)
    if m is None:
        m = [(project(record_of(tr), rung), p) for tr, p in enabled(s, cfg, programs)]
        memo[s] = m
    return m


def ceiling_table(cfg: WorldConfig, programs, law: WindowLaw, rungs: Iterable[str] = ("r0", "r1", "r2", "r3", "r4"),
                  stats: dict = None, types=ENTITY_ORDER, prefix_len: int = None) -> Dict[str, Table]:
    """{rung: {(reset, Πw): (law mass, P*(Πr | Πw))}}. With `prefix_len = k`
    the classes are k-record prefixes (contract v0.1.2: the headline
    position k = L − 1 and the interior curve), from the prefix-length pass."""
    rungs = tuple(rungs)
    if prefix_len is None:
        aggs = window_law_aggregates(cfg, programs, law, rungs, stats)
    else:
        aggs = prefix_law_aggregates(cfg, programs, law, prefix_len, rungs, stats)
    out: Dict[str, Table] = {}
    for rung in rungs:
        patt: Dict[Key, Dict[tuple, Fraction]] = {}
        for (reset, win), joint in aggs[rung].items():
            pw, binding = pattern_all(win, types)
            d = patt.setdefault((reset, pw), {})
            for s, m in joint.items():
                d[(s, binding)] = d.get((s, binding), Fraction(0)) + m
        moves: dict = {}
        table: Table = {}
        for key, joint in patt.items():
            mass = sum(joint.values(), Fraction(0))
            star: Dict[Record, Fraction] = {}
            for (s, b), m in joint.items():
                for r, p in _moves(s, cfg, programs, rung, moves):
                    rho, _ = extend_binding(b, r, types)
                    star[rho] = star.get(rho, Fraction(0)) + m * p
            table[key] = (mass, {rho: q / mass for rho, q in star.items()})
        out[rung] = table
        if stats is not None:
            stats.setdefault("n_pattern_classes", {})[rung] = len(table)
    return out


def mean_next_entropy_bits(table: Table) -> float:
    """Law-mass mean of H(P*(Πr | Πw)) over the classes — the pattern
    observer's next-record entropy at the headline position."""
    return sum(float(m) * entropy_bits(star) for m, star in table.values())


# ---- exact serialization -------------------------------------------------------

def _f(v) -> str:
    if v is None:
        return "NONE"
    if v == MASKED:
        return "MASKED"
    if isinstance(v, tuple):
        tag, k = v
        return ("L" if tag == "LOCK" else "D") + str(k)
    return str(v)


def _v(s: str):
    if s == "NONE":
        return None
    if s == "MASKED":
        return MASKED
    if s[0] in "LD" and s[1:].isdigit():
        return ("LOCK" if s[0] == "L" else "DEV", int(s[1:]))
    return int(s)


def serial_record(r: Record) -> str:
    return ",".join((r.kind, _f(r.actor), _f(r.obj), _f(r.related), _f(r.lineage)))


def record_from_serial(s: str) -> Record:
    kind, a, o, rel, lin = s.split(",")
    return Record(kind, _v(a), _v(o), _v(rel), _v(lin))


def serial_key(key: Key) -> str:
    reset, pw = key
    return ("R|" if reset else "N|") + ";".join(serial_record(r) for r in pw)


def key_from_serial(s: str) -> Key:
    flag, body = s.split("|", 1)
    recs = tuple(record_from_serial(x) for x in body.split(";")) if body else ()
    return flag == "R", recs


def save_table(table: Table, path: Path) -> None:
    with open(path, "w") as f:
        for key, (mass, star) in table.items():
            f.write(json.dumps({"k": serial_key(key), "m": str(mass),
                                "p": {serial_record(r): str(q) for r, q in star.items()}}) + "\n")


def load_table(path: Path) -> Table:
    out: Table = {}
    with open(path) as f:
        for line in f:
            d = json.loads(line)
            out[key_from_serial(d["k"])] = (Fraction(d["m"]), {record_from_serial(r): Fraction(q) for r, q in d["p"].items()})
    return out
