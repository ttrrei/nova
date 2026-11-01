"""Supertrend — adapted from Moneta v1 library/supertrend.py (Apache-2.0).

Causal, path-dependent, no TA-Lib implementation available.

TA-Lib ships no Supertrend, so this is the project's own implementation.
It follows the canonical construction (as used by TradingView and
pandas-ta-classic):

* Basic bands from ATR: ``ub = hl2 + k * ATR``, ``lb = hl2 - k * ATR``.
* **Final** bands ratchet against the *previous bar's close*:
  the final upper band only moves *down* (or when the price closes above it),
  the final lower band only moves *up* (or when the price closes below it).
* Direction: in an uptrend the **lower** band is active and the trend flips
  to down when the close crosses *below* it; in a downtrend the upper band is
  active and the trend flips to up when the close crosses *above* it.
* The reported line is the **active** band (lower in uptrends, upper in
  downtrends) — that is the trailing-stop line a strategy would trade.

Causality: bar ``T`` uses only bars ``<= T`` (the recursion reads the
previous close, which is closed by then). The recursion is
**path-dependent** — starting later can give a different state. Nova always
computes from the snapshot's source head, retains NULL warm-up outputs and
does not claim that a fixed number of bars guarantees state convergence.

Parameters
----------
h, low, c : 1-D float64 arrays (high / low / close).
atr     : 1-D float64 ATR series (any window ``n``); NaN where undefined.
mult    : ATR multiplier ``k`` — a **free** parameter (not grid-restricted),
          must be passed explicitly, ``> 0``.

Returns
-------
(line, direction) : 1-D float64 arrays. ``line`` is NaN where ATR is NaN;
``direction`` is +1 (uptrend) / -1 (downtrend), NaN before start.
"""

from __future__ import annotations

import numpy as np

__all__ = ["supertrend"]


def supertrend(
    h: np.ndarray, low: np.ndarray, c: np.ndarray, atr: np.ndarray, mult: float = 3.0
) -> tuple[np.ndarray, np.ndarray]:
    """Supertrend line and direction (+1 uptrend / -1 downtrend), causal.

    Bar T uses only bars <= T: bands are ratcheted against the previous bar's
    close, and the direction flips when bar T's close crosses the active band.
    Bars before ``atr`` is defined are NaN. The recursion is path-dependent;
    the caller retains full source history and the unknown warm-up outputs.
    """
    n = len(c)
    line = np.full(n, np.nan)
    direction = np.full(n, np.nan)
    if not mult > 0:
        raise ValueError(f"Supertrend multiplier must be > 0, got {mult}")

    hl2 = (h + low) / 2.0
    ub = hl2 + mult * atr
    lb = hl2 - mult * atr
    fu = fl = np.nan  # final upper / lower band (the ratcheted ones)
    d = 1.0
    started = False
    for t in range(n):
        if not np.isfinite(atr[t]):
            continue
        if not started:
            fu, fl, d, started = ub[t], lb[t], 1.0, True
        else:
            fu = ub[t] if (ub[t] < fu or c[t - 1] > fu) else fu
            fl = lb[t] if (lb[t] > fl or c[t - 1] < fl) else fl
            if d > 0:
                if c[t] < fl:
                    d = -1.0
            elif c[t] > fu:
                d = 1.0
        direction[t] = d
        line[t] = fl if d > 0 else fu
    return line, direction
