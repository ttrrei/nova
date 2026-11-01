import math
from pathlib import Path

import yaml


class UniqueLoader(yaml.SafeLoader):
    pass


def _mapping(loader, node, deep=False):
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if not isinstance(key, str) or key in result:
            raise ValueError("YAML keys must be unique strings")
        result[key] = loader.construct_object(value_node, deep=deep)
    return result


UniqueLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _mapping)


def keys(value, allowed, required=()):
    if not isinstance(value, dict):
        raise ValueError("Expected a mapping")
    unknown = set(value) - set(allowed)
    missing = set(required) - set(value)
    if unknown or missing:
        raise ValueError(
            f"Unknown keys: {sorted(unknown)}; missing keys: {sorted(missing)}"
        )


def number(value, name, minimum=0, maximum=None):
    if (
        isinstance(value, bool)
        or not isinstance(value, (int, float))
        or not math.isfinite(value)
    ):
        raise ValueError(f"{name} must be a finite number")
    if value < minimum or (maximum is not None and value > maximum):
        raise ValueError(f"{name} is out of range")
    return float(value)


def positive_integer(value, name):
    if isinstance(value, bool) or not isinstance(value, int) or not 1 <= value <= 10000:
        raise ValueError(f"{name} must be an integer between 1 and 10000")
    return value


def load_strategy(path):
    text = Path(path).read_text(encoding="utf-8")
    if len(text.encode()) > 1_000_000:
        raise ValueError("Strategy YAML exceeds 1 MB")
    spec = yaml.load(text, Loader=UniqueLoader)
    keys(
        spec,
        {
            "version",
            "id",
            "family",
            "hypothesis",
            "timeframe_minutes",
            "entry",
            "exit",
            "execution",
        },
        {"version", "id", "family", "timeframe_minutes", "entry", "exit"},
    )
    if type(spec["version"]) is not int or spec["version"] != 1:
        raise ValueError("Only strategy version 1 is supported")
    for name in ("id", "family"):
        if not isinstance(spec[name], str) or not spec[name].strip():
            raise ValueError(f"{name} must be a nonempty string")
    if "hypothesis" in spec and (
        not isinstance(spec["hypothesis"], str) or not spec["hypothesis"].strip()
    ):
        raise ValueError("hypothesis must be a nonempty string")
    positive_integer(spec["timeframe_minutes"], "timeframe_minutes")
    keys(spec["entry"], {"long", "short"})
    if not spec["entry"]:
        raise ValueError("At least one entry direction is required")
    keys(
        spec["exit"],
        {"stop_loss_pct", "take_profit_pct", "max_holding_bars", "long", "short"},
    )
    stop = number(spec["exit"].get("stop_loss_pct", 0.02), "stop_loss_pct")
    if stop != 0.02:
        raise ValueError("Nova requires the mandatory 2% entry-price stop")
    spec["exit"]["stop_loss_pct"] = stop
    if "take_profit_pct" in spec["exit"]:
        if not 0 < number(spec["exit"]["take_profit_pct"], "take_profit_pct") < 1:
            raise ValueError("take_profit_pct must be between zero and one")
    if "max_holding_bars" in spec["exit"]:
        positive_integer(spec["exit"]["max_holding_bars"], "max_holding_bars")
    execution = spec.setdefault("execution", {})
    names = {
        "spread_bps",
        "slippage_bps_per_side",
        "commission_bps_round_trip",
        "financing_bps_per_day",
    }
    keys(execution, names)
    for name in names:
        execution[name] = number(execution.get(name, 0), name, maximum=1000)
    return spec
