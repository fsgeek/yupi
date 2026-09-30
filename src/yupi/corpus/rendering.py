"""Keyed rendering (Part II v0.2.9 Clause 4; design v0.1 §3; Part I D3).

σ is drawn per episode and entity type by HMAC-SHA256(run_key,
f"{episode_id}:{entity_type}") seeding random.Random, which drives a
partial Fisher–Yates over the pool's drawable (non-reserved) slice:
exactly uniform over injections under the idealized-key assumption;
randrange is unbiased (rejection over getrandbits); no modulo reduction.
The table is provenance beside the corpus, never inside it.
"""
from __future__ import annotations

import hashlib
import hmac
import random
from dataclasses import dataclass

from yupi.corpus.vocab import ENTITY_TYPES, KINDS, MASKED, NONE, RESERVED, pool_tokens
from yupi.interfaces import Lit
from yupi.records import Record


class RenderingRefused(ValueError):
    """A D3 / design §3 refusal; the message names the statute line."""


def d3_check(entity_type: str, n_entities: int, pool_size: int) -> None:
    """Part I D3: a pool of ≥ 50 tokens for ≤ 4 threads, others proportionally;
    design §3: every pool ≥ 8× its entity count. The rule is on the pool
    (the reserved slice is part of it, held out for the lexical split):
    request ids have 32 tokens for 4 ids, of which 28 are drawable."""
    need = max(50 if entity_type == "thread" else 0, 8 * n_entities)
    if pool_size < need:
        raise RenderingRefused(
            f"Part I D3 / design v0.1 §3: {entity_type} pool has {pool_size} "
            f"tokens for {n_entities} entities; requires >= {need}")


def _seed(run_key: bytes, episode_id: int, label: str) -> int:
    return int.from_bytes(hmac.new(run_key, f"{episode_id}:{label}".encode(), hashlib.sha256).digest(), "big")


def _keyed_injection(run_key: bytes, episode_id: int, entity_type: str, pool: tuple,
                     drawable: int, n_entities: int) -> tuple:
    """The mechanism, D3-unchecked (tests exercise it on tiny pools); injection() checks D3."""
    rng = random.Random(_seed(run_key, episode_id, entity_type))
    slots = list(pool[:drawable])
    for i in range(n_entities):                     # partial Fisher–Yates: uniform injection
        j = rng.randrange(i, drawable)
        slots[i], slots[j] = slots[j], slots[i]
    return tuple(slots[:n_entities])


def injection(run_key: bytes, episode_id: int, entity_type: str, n_entities: int,
              lift_reservation: bool = False) -> tuple:
    pool = pool_tokens(entity_type)
    drawable = len(pool) - (0 if lift_reservation else RESERVED[entity_type])
    d3_check(entity_type, n_entities, len(pool))
    return _keyed_injection(run_key, episode_id, entity_type, pool, drawable, n_entities)


@dataclass(frozen=True)
class EpisodeTable:
    """(entity type, structural index) -> token for one episode."""
    episode_id: int
    thread: tuple
    lock: tuple
    device: tuple
    request: tuple

    @classmethod
    def draw(cls, run_key: bytes, episode_id: int, cfg, lift_reservation: bool = False) -> "EpisodeTable":
        n = {"thread": cfg.n_threads, "lock": cfg.n_locks, "device": cfg.n_devices, "request": cfg.req_pool}
        return cls(episode_id, *(injection(run_key, episode_id, et, n[et], lift_reservation) for et in ENTITY_TYPES))

    def inverse(self) -> dict:
        return {tok: (et, i) for et in ENTITY_TYPES for i, tok in enumerate(getattr(self, et))}

    def to_json(self) -> dict:
        return {"episode": self.episode_id, **{et: list(getattr(self, et)) for et in ENTITY_TYPES}}

    @classmethod
    def from_json(cls, d: dict) -> "EpisodeTable":
        return cls(d["episode"], *(tuple(d[et]) for et in ENTITY_TYPES))


def _tok(v, names: tuple) -> str:
    if v == MASKED:
        return MASKED
    if v is None:
        return NONE
    return names[v]


def render(rec: Record, table: EpisodeTable) -> tuple:
    """Five tokens: KIND ACTOR OBJECT RELATED LINEAGE (Part I D5)."""
    if isinstance(rec.obj, Lit):                     # the relay rung: a KIND token in the OBJECT slot
        obj = rec.obj.kind
    elif rec.obj == MASKED:
        obj = MASKED
    elif rec.obj is None:
        obj = NONE
    else:
        kind, i = rec.obj
        obj = table.lock[i] if kind == "LOCK" else table.device[i]
    return (rec.kind, _tok(rec.actor, table.thread), obj,
            _tok(rec.related, table.thread), _tok(rec.lineage, table.request))


def _val(tok: str, inv: dict, expect: tuple):
    if tok == MASKED:
        return MASKED
    if tok == NONE:
        return None
    et, i = inv[tok]
    if et not in expect:
        raise ValueError(f"token {tok!r} is a {et}, expected one of {expect}")
    return i


def unrender(tokens: tuple, table: EpisodeTable) -> Record:
    """Inverse of render for this episode's table (structural, projected record)."""
    if len(tokens) != 5:
        raise ValueError("a record is exactly five tokens (Part I D5)")
    inv = table.inverse()
    kind, actor, obj, related, lineage = tokens
    if obj in KINDS:                                 # the relay rung's literal (never an entity token)
        o = Lit(obj)
    elif obj == MASKED:
        o = MASKED
    elif obj == NONE:
        o = None
    else:
        et, i = inv[obj]
        o = ("LOCK", i) if et == "lock" else ("DEV", i) if et == "device" else None
        if o is None:
            raise ValueError(f"OBJECT token {obj!r} is a {et}")
    return Record(kind, _val(actor, inv, ("thread",)), o,
                  _val(related, inv, ("thread",)), _val(lineage, inv, ("request",)))
