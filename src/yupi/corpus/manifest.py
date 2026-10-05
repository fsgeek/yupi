"""The manifest is the record (design v0.1 §5): with it and the code at
its generator version, a corpus regenerates byte for byte. validate()
refuses, never coerces (§9); every refusal names its statute line.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field, replace
from fractions import Fraction

from yupi.config import WorldConfig
from yupi.corpus.rendering import RenderingRefused, d3_check
from yupi.corpus.vocab import ENTITY_TYPES, POOL_SIZES, RESERVED, VOCAB_SHA256, VOCAB_VERSION
from yupi.corpus.windows import max_tokens
from yupi.interfaces import WINDOW_RUNGS
from yupi.programs import programs_for
from yupi.window import WindowLaw

SCHEMA_VERSION = 1
GENERATOR_VERSION = "0.1.0"
# the per-record rungs, then the window-level rungs of interfaces.WINDOW_RUNGS: r1R the relay (relay
# design v0.1 §2, 2026-09-30); r1D the decoy and r1S the self-copy (three-arm design v0.1 §2, 2026-10-05)
RUNGS = ("r0", "r1", "r2", "r3", "r4") + tuple(WINDOW_RUNGS)


class ManifestRefused(ValueError):
    """Design v0.1 §9: refuse, never coerce."""


@dataclass(frozen=True)
class Split:
    name: str
    seed_start: int     # episode ids [seed_start, seed_end)
    seed_end: int


@dataclass(frozen=True)
class Manifest:
    schema_version: int
    generator_version: str
    vocab_version: int
    vocab_sha256: str
    git_commit: str
    config: str
    programs: str
    epsilon: str
    queue_depth: int
    completion_p: str
    T_ep: int
    L: int
    B: int
    rung: str
    pools: dict
    reserved: dict
    lift_reservation: bool
    run_key_hex: str
    splits: tuple
    max_tokens: int
    counts: dict = field(default_factory=dict)

    @classmethod
    def new(cls, *, programs: str, epsilon: Fraction, T_ep: int, L: int, B: int, rung: str,
            run_key: bytes, splits: tuple, git_commit: str, queue_depth: int = 2,
            completion_p: Fraction = Fraction(1, 3), lift_reservation: bool = False) -> "Manifest":
        mt = 5 * L + 1                                  # max_tokens(law) without constructing a law that may be refused
        return cls(SCHEMA_VERSION, GENERATOR_VERSION, VOCAB_VERSION, VOCAB_SHA256, git_commit,
                   "c1", programs, str(Fraction(epsilon)), queue_depth, str(Fraction(completion_p)),
                   T_ep, L, B, rung, dict(POOL_SIZES), dict(RESERVED), lift_reservation,
                   run_key.hex(), tuple(splits), mt)

    def name(self) -> str:
        return f"{self.programs}-{self.T_ep}-{self.L}-{self.B}-{self.rung}-eps{self.epsilon.replace('/', '_')}"

    def run_key(self) -> bytes:
        return bytes.fromhex(self.run_key_hex)

    def run_id(self) -> str:
        return hashlib.sha256(self.run_key()).hexdigest()[:16]

    def world(self):
        cfg = WorldConfig.c1(p=Fraction(self.completion_p), queue_depth=self.queue_depth,
                             epsilon=Fraction(self.epsilon))
        return cfg, programs_for(self.programs)

    def law(self) -> WindowLaw:
        return WindowLaw(self.T_ep, self.L, self.B)

    def with_counts(self, counts: dict) -> "Manifest":
        return replace(self, counts=dict(counts))

    def to_json(self) -> dict:
        d = self.__dict__.copy()
        d["splits"] = [s.__dict__ for s in self.splits]
        return d

    @classmethod
    def from_json(cls, d: dict) -> "Manifest":
        d = dict(d)
        d["splits"] = tuple(Split(**s) for s in d["splits"])
        return cls(**d)


def _entity_counts(m: Manifest) -> dict:
    cfg, _ = m.world()
    return {"thread": cfg.n_threads, "lock": cfg.n_locks, "device": cfg.n_devices, "request": cfg.req_pool}


def validate(m: Manifest) -> None:
    if m.rung not in RUNGS:
        raise ManifestRefused(f"Part II §4 projection table: unknown rung {m.rung!r}")
    if m.T_ep % m.B or m.L % m.B:
        raise ManifestRefused("Part II §2(a): T_ep and L must be multiples of the bucket size B")
    if m.max_tokens != max_tokens(m.law()):
        raise ManifestRefused("design v0.1 §2: max_tokens must be 5·L + 1")
    if m.generator_version != GENERATOR_VERSION or m.schema_version != SCHEMA_VERSION:
        raise ManifestRefused(f"design v0.1 §9: manifest generator {m.generator_version}/schema "
                              f"{m.schema_version} differs from the code's {GENERATOR_VERSION}/{SCHEMA_VERSION}")
    if m.vocab_version != VOCAB_VERSION or m.vocab_sha256 != VOCAB_SHA256:
        raise ManifestRefused("design v0.1 §4: vocabulary version/hash differs from the code's")
    n = _entity_counts(m)
    for et in ENTITY_TYPES:                             # D3 on the manifest's pools, whatever they say
        try:
            d3_check(et, n[et], m.pools.get(et, 0))
        except RenderingRefused as e:
            raise ManifestRefused(str(e)) from e
    if m.pools != POOL_SIZES or m.reserved != RESERVED:
        raise ManifestRefused("design v0.1 §4: pools and reservations are fixed by the vocabulary; "
                              "a manifest asking for others cannot be honoured")
    if m.lift_reservation and any(s.name == "train" for s in m.splits):
        raise ManifestRefused("design v0.1 §3: the reserved slice is never drawn in a training corpus")
    spans = sorted((s.seed_start, s.seed_end, s.name) for s in m.splits)
    for (a0, a1, an), (b0, b1, bn) in zip(spans, spans[1:]):
        if b0 < a1:
            raise ManifestRefused(f"design v0.1 §6 / proposal §7.2: seed ranges overlap ({an}, {bn})")
