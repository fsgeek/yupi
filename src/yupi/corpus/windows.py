"""One training example is one Part II §2(a) window of one exact episode
(design v0.1 §2). The episode's dynamics are seeded by the episode id
alone (the exact side can regenerate the episode from the seed); the
endpoint T is keyed like the injections, HMAC(run_key, f"{id}:endpoint"),
so everything an example depends on is fixed by (manifest, episode id).
"""
from __future__ import annotations

import hashlib
import hmac
import random
from dataclasses import dataclass

from yupi.corpus.rendering import EpisodeTable, render, unrender
from yupi.corpus.vocab import RESET
from yupi.interfaces import project
from yupi.simulator import sample_episode
from yupi.window import WindowLaw


@dataclass(frozen=True)
class Window:
    episode_id: int
    T: int
    U: int
    rung: str
    records: tuple          # projected structural records O_{U+1..T}

    @property
    def reset(self) -> bool:
        return self.U == 0


def draw_endpoint(run_key: bytes, episode_id: int, law: WindowLaw) -> int:
    """T ~ Uniform{B, 2B, …, T_ep} (Part II §2(a)); keyed, unbiased randrange."""
    seed = int.from_bytes(hmac.new(run_key, f"{episode_id}:endpoint".encode(), hashlib.sha256).digest(), "big")
    ends = list(law.endpoints())
    return ends[random.Random(seed).randrange(len(ends))]


def draw_window(cfg, programs, law: WindowLaw, rung: str, run_key: bytes, episode_id: int) -> Window:
    episode = sample_episode(cfg, programs, law.T_ep, episode_id)
    T = draw_endpoint(run_key, episode_id, law)
    U = law.offset(T)
    return Window(episode_id, T, U, rung, tuple(project(r, rung) for _, r in episode[U:T]))


def max_tokens(law: WindowLaw) -> int:
    """L records of five tokens plus RESET when U = 0 (design §2)."""
    return 5 * law.L + 1


def serialize(window: Window, table: EpisodeTable) -> tuple:
    out = [RESET] if window.reset else []
    for r in window.records:
        out.extend(render(r, table))
    return tuple(out)


def deserialize(tokens, table: EpisodeTable):
    """tokens -> (reset, projected structural records); inverse of serialize."""
    toks = list(tokens)
    reset = bool(toks) and toks[0] == RESET
    if reset:
        toks = toks[1:]
    if len(toks) % 5:
        raise ValueError("window body must be a whole number of five-token records (Part I D5)")
    return reset, tuple(unrender(tuple(toks[i:i + 5]), table) for i in range(0, len(toks), 5))
