"""Reviewed feature identifiers; strategies cannot supply computations."""

FEATURE_VERSION = "migration-features-v2"
FEATURES = {
    "close": {"type": "VALUE", "unit": "price", "warmup_bars": 1},
    "volume": {"type": "VALUE", "unit": "source_activity", "warmup_bars": 1},
    "atr_sma_14": {"type": "VALUE", "unit": "price", "warmup_bars": 14},
    "sma_6": {"type": "VALUE", "unit": "price", "warmup_bars": 6},
    "sma_24": {"type": "VALUE", "unit": "price", "warmup_bars": 24},
    "sma_alignment_6_24": {"type": "STATE", "unit": "sign", "warmup_bars": 24},
    "sma_cross_up_6_24": {"type": "EVENT", "unit": "boolean", "warmup_bars": 25},
    "sma_cross_down_6_24": {"type": "EVENT", "unit": "boolean", "warmup_bars": 25},
    "close_sma24_distance_atr": {"type": "VALUE", "unit": "atr", "warmup_bars": 24},
}

for _definition in FEATURES.values():
    _definition["available_at"] = "bar_close_time"

TREND_COLUMNS = [name for name in FEATURES if name not in {"close", "volume", "atr_sma_14"}]

STARTER_FEATURES = frozenset(FEATURES)
from .legacy_catalog import LEGACY_FEATURES
for _name, _definition in LEGACY_FEATURES.items():
    FEATURES.setdefault(_name, _definition)
