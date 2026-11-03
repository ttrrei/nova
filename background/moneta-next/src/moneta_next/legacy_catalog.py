"""Exact default feature names reviewed against the pinned legacy engine.

262 original features plus 24 new, one-bar direction transition features.
H1 projections and experimental catalogue features are not auto-promoted.
"""
from .vendor.utils import param_tag

LEGACY_COMMIT = "67896d60bc6ecf73fc6aec42aee469a24cce3564"
WINDOWS = (6, 12, 24, 60, 120)
PAIRS = ((6, 24), (12, 60), (24, 120))
PSAR_PARAMS = ((0.02, 0.20), (0.01, 0.10))
ST_MULTS = (2.0, 3.0)
LEGACY_FEATURES = {}


def add(name, domain, unit="ratio", semantic="VALUE"):
    LEGACY_FEATURES[name] = {"type": semantic, "unit": unit, "domain": domain,
        "available_at": "bar_close_time", "warmup_bars": 360,
        "origin": "legacy_default", "source_commit": LEGACY_COMMIT}


for n in WINDOWS:
    for prefix in ("sma", "ema", "adx", "plus_di", "minus_di", "aroon_up", "aroon_down", "dc_upper", "dc_lower", "dc_mid"):
        add(f"{prefix}_{n}", "trend", "price" if prefix in {"sma", "ema", "dc_upper", "dc_lower", "dc_mid"} else "index")
    for prefix in ("rsi", "roc", "mom", "stoch_k", "stoch_d", "cci", "willr"):
        add(f"{prefix}_{n}", "momentum", "price" if prefix == "mom" else "index")
    for prefix in ("atr", "bb_mid", "bb_upper", "bb_lower", "bb_width", "bb_pctb", "kc_mid", "kc_upper", "kc_lower", "sqz_on", "hv"):
        add(f"{prefix}_{n}", "volatility", "price" if prefix in {"atr", "bb_mid", "bb_upper", "bb_lower", "kc_mid", "kc_upper", "kc_lower"} else "ratio", "STATE" if prefix == "sqz_on" else "VALUE")
    for prefix in ("er", "chop"):
        add(f"{prefix}_{n}", "regime")
    for prefix in ("vol_sma", "vol_rel", "mfi", "cmf"):
        add(f"{prefix}_{n}", "volume", "source_activity" if prefix == "vol_sma" else "ratio")
    for prefix in ("atr_pct", "ema_dist", "dc_pos", "dist_high", "dist_low"):
        add(f"{prefix}_{n}", "derived", "atr" if prefix in {"ema_dist", "dist_high", "dist_low"} else "ratio")
for fast, slow in PAIRS:
    for prefix in ("macd", "macd_signal", "macd_hist"):
        add(f"{prefix}_{fast}_{slow}", "trend", "price")
    for prefix in ("ema_spread", "macd_hist_atr", "vol_ratio"):
        add(f"{prefix}_{fast}_{slow}", "derived", "atr" if prefix != "vol_ratio" else "ratio")
for acceleration, maximum in PSAR_PARAMS:
    tag = f"{param_tag(acceleration)}_{param_tag(maximum)}"
    add(f"psar_{tag}", "trend", "price")
    add(f"psar_dir_{tag}", "trend", "sign", "STATE")
    add(f"psar_dist_{tag}", "derived", "atr")
for n in WINDOWS:
    for multiplier in ST_MULTS:
        tag = f"{n}_{param_tag(multiplier)}"
        add(f"st_{tag}", "trend", "price")
        add(f"st_dir_{tag}", "trend", "sign", "STATE")
        add(f"st_dist_{tag}", "derived", "atr")
for name in ("bar_body_ratio", "bar_upper_wick_ratio", "bar_lower_wick_ratio", "bar_clv"):
    add(name, "candle")
for name in ("hour_sin", "hour_cos", "dow_sin", "dow_cos"):
    add(name, "derived")
for name in ("is_gap_bar", "is_partial", "is_near_market_close"):
    add(name, "quality", "flag", "STATE")
add("tr", "volatility", "price")
add("vwap", "volume", "price")
ORIGINAL_FEATURE_NAMES = frozenset(LEGACY_FEATURES)
assert len(ORIGINAL_FEATURE_NAMES) == 262

# Return-order defects in the pinned engine, plus documented stale VWAP.
# Keep corrected recomputation available while excluding affected old values.
BLOCKED_CACHED_FEATURES = frozenset({"vwap"} | {
    f"{prefix}_{n}" for n in WINDOWS for prefix in
    ("aroon_up", "aroon_down", "bb_mid", "bb_upper", "bb_width", "bb_pctb", "sqz_on")
})
for _name in BLOCKED_CACHED_FEATURES-{"vwap"}:
    LEGACY_FEATURES[_name]["origin"] = "legacy_algorithm_with_return_order_repair"

DIRECTION_TRANSITIONS = {}
for name in tuple(ORIGINAL_FEATURE_NAMES):
    if name.startswith("psar_dir_") or name.startswith("st_dir_"):
        prefix = "psar" if name.startswith("psar") else "st"
        tag = name.split("_dir_", 1)[1]
        for label, before, after in (("up", -1, 1), ("down", 1, -1)):
            event = f"{prefix}_flip_{label}_{tag}"
            DIRECTION_TRANSITIONS[event] = (name, before, after)
            add(event, "events", "boolean", "EVENT")
            LEGACY_FEATURES[event]["origin"] = "new_transform_of_legacy_direction"


def direction_transitions(columns):
    """Nullable one-bar events. First row and undefined states stay unknown."""
    import numpy as np
    out = {}
    for event, (source, before, after) in DIRECTION_TRANSITIONS.items():
        if source not in columns:
            continue
        values = np.asarray(columns[source], dtype=float)
        previous = np.r_[np.nan, values[:-1]]
        valid = np.isfinite(values) & np.isfinite(previous)
        out[event] = np.where(valid, ((previous == before) & (values == after)).astype(float), np.nan)
    return out
