"""ε grid for ceilings and sweep scripts.

Default is the historical pair (1, ½) so every artifact produced before the
held-out round reproduces bit-for-bit. `YUPI_EPS="1/4,5/8"` overrides it for
held-out families (held-out-laws-proposal v0.3, Selection E draw
`docs/held-out-selection-e-draw-2026-08-21.json`). Values must be exact
Fractions in (0, 1]; decimals are refused because the truth oracle is exact.
"""
import os
from fractions import Fraction
from typing import Tuple

DEFAULT: Tuple[Fraction, ...] = (Fraction(1), Fraction(1, 2))


def eps_grid() -> Tuple[Fraction, ...]:
    raw = os.environ.get("YUPI_EPS")
    if raw is None:
        return DEFAULT
    out = []
    for tok in raw.split(","):
        tok = tok.strip()
        if "." in tok or not tok:
            raise ValueError(f"YUPI_EPS entries must be exact fractions, got {tok!r}")
        try:
            f = Fraction(tok)
        except (ValueError, ZeroDivisionError) as e:
            raise ValueError(f"YUPI_EPS entry {tok!r}: {e}") from None
        if not (0 < f <= 1):
            raise ValueError(f"YUPI_EPS entry {tok!r} outside (0, 1]")
        out.append(f)
    return tuple(out)
