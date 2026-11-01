"""The reviewed feature vocabulary. Strategies never supply computations."""

FEATURE_VERSION = "nova-features-v2"
FEATURE_PARAMS = {
    "sma": [6, 24],
    "ema": [6, 24, 60],
    "atr": 14,
    "rsi": 14,
    "psar": {"acceleration": 0.02, "maximum": 0.2},
    "supertrend": {"atr": 14, "multiplier": 3.0},
    "research": {
        "prior_range_bars": 24,
        "relative_volume_prior_bars": 24,
        "efficiency_bars": 24,
        "return_bars": 6,
        "normalization": "atr_14",
        "session_clock": "bar_open_time_UTC",
    },
}


def definition(kind, unit, warmup, domain):
    return {
        "type": kind,
        "unit": unit,
        "warmup_bars": warmup,
        "domain": domain,
        "available_at": "bar_close_time",
    }


FEATURES = {
    "close": definition("VALUE", "price", 1, "core"),
    "volume": definition("VALUE", "source_activity", 1, "core"),
    "atr_sma_14": definition("VALUE", "price", 14, "core"),
    "atr_14": definition("VALUE", "price", 15, "core"),
    "rsi_14": definition("VALUE", "0_to_100", 15, "momentum"),
    "sma_6": definition("VALUE", "price", 6, "trend"),
    "sma_24": definition("VALUE", "price", 24, "trend"),
    "sma_alignment_6_24": definition("STATE", "sign", 24, "trend"),
    "sma_cross_up_6_24": definition("EVENT", "boolean", 25, "trend"),
    "sma_cross_down_6_24": definition("EVENT", "boolean", 25, "trend"),
    "close_sma24_distance_atr": definition("VALUE", "atr_sma_14", 24, "trend"),
    **{f"ema_{n}": definition("VALUE", "price", n, "trend") for n in (6, 24, 60)},
    "ema_alignment_6_24": definition("STATE", "sign", 24, "trend"),
    "ema_cross_up_6_24": definition("EVENT", "boolean", 25, "trend"),
    "ema_cross_down_6_24": definition("EVENT", "boolean", 25, "trend"),
    "close_ema60_distance_atr": definition("VALUE", "atr_14", 60, "trend"),
    "psar": definition("VALUE", "price", 2, "trend"),
    "psar_direction": definition("STATE", "sign", 2, "trend"),
    "psar_distance_atr": definition("VALUE", "atr_14", 15, "trend"),
    "psar_flip_up": definition("EVENT", "boolean", 3, "trend"),
    "psar_flip_down": definition("EVENT", "boolean", 3, "trend"),
    "supertrend": definition("VALUE", "price", 15, "trend"),
    "supertrend_direction": definition("STATE", "sign", 15, "trend"),
    "supertrend_distance_atr": definition("VALUE", "atr_14", 15, "trend"),
    "supertrend_flip_up": definition("EVENT", "boolean", 16, "trend"),
    "supertrend_flip_down": definition("EVENT", "boolean", 16, "trend"),
    "prior_high_24": definition("VALUE", "price", 25, "trend"),
    "prior_low_24": definition("VALUE", "price", 25, "trend"),
    "range_position_24": definition("VALUE", "prior_range_fraction", 25, "trend"),
    "range_width_atr_24": definition("VALUE", "atr_14", 25, "trend"),
    "breakout_up_24": definition("STATE", "boolean", 25, "trend"),
    "breakout_down_24": definition("STATE", "boolean", 25, "trend"),
    "failed_breakout_up_24": definition("EVENT", "boolean", 25, "trend"),
    "failed_breakout_down_24": definition("EVENT", "boolean", 25, "trend"),
    "return_6_atr": definition("VALUE", "atr_14", 15, "momentum"),
    "range_atr": definition("VALUE", "atr_14", 15, "core"),
    "relative_volume_24": definition("VALUE", "prior_activity_ratio", 25, "core"),
    "utc_hour": definition("VALUE", "UTC_hour", 1, "core"),
    "efficiency_24": definition("VALUE", "0_to_1", 25, "trend"),
}

FAMILIES = (
    "trend_continuation",
    "pullback_reentry",
    "volatility_expansion",
    "mean_reversion",
    "range_trading",
    "failed_breakout",
    "market_structure",
    "volume_activity",
    "session_temporal",
    "relative_strength",
    "regime_transition",
    "momentum_exhaustion",
)
