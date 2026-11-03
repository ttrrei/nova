"""Closed-bar alignment adapted from legacy asof_join_h1_features.

Uses the same searchsorted(..., side='right') algorithm, with explicit input
validation, an instrument boundary and caller-selected registered columns.
"""
import numpy as np


def align_closed_features(signal_close_times, context_close_times, values):
    signal = np.asarray(signal_close_times, dtype="datetime64[ns]")
    context = np.asarray(context_close_times, dtype="datetime64[ns]")
    values = np.asarray(values, dtype=float)
    if signal.ndim != 1 or context.ndim != 1 or values.ndim not in (1, 2) or len(values) != len(context):
        raise ValueError("Aligned one-dimensional timestamps and context rows required")
    if np.isnat(signal).any() or np.isnat(context).any():
        raise ValueError("Missing close timestamps")
    if np.any(np.diff(signal) <= np.timedelta64(0, 'ns')) or np.any(np.diff(context) <= np.timedelta64(0, 'ns')):
        raise ValueError("Close timestamps must be unique and increasing")
    positions = np.searchsorted(context, signal, side="right") - 1
    shape = (len(signal),) + values.shape[1:]
    out = np.full(shape, np.nan)
    valid = positions >= 0
    out[valid] = values[positions[valid]]
    return out
