"""Compile reviewed YAML predicates into past-only DuckDB SQL."""

from .catalog import FEATURES
from .config import keys, number, positive_integer

OPERATORS = {"eq": "=", "ne": "!=", "gt": ">", "gte": ">=", "lt": "<", "lte": "<="}


class Compiler:
    def __init__(self):
        self.steps = []

    def add(self, expression):
        if len(self.steps) >= 256:
            raise ValueError("Strategy exceeds 256 expression nodes")
        name = f"_condition_{len(self.steps)}"
        self.steps.append((name, expression))
        return name

    def predicate(self, node, depth=0):
        if depth > 12:
            raise ValueError("Expression exceeds depth 12")
        if node is None:
            return self.add("FALSE")
        if not isinstance(node, dict) or not node:
            raise ValueError("A condition must be a nonempty mapping")
        if "feature" in node:
            keys(node, {"feature", "op", "value"}, {"feature", "op", "value"})
            feature, operator, value = node["feature"], node["op"], node["value"]
            if not isinstance(feature, str) or feature not in FEATURES or not isinstance(operator, str) or operator not in OPERATORS:
                raise ValueError("Unknown registered feature or comparison operator")
            is_boolean = FEATURES[feature]["unit"] == "boolean"
            if is_boolean:
                if type(value) is not bool or operator not in {"eq", "ne"}:
                    raise ValueError("Boolean features require eq/ne and a boolean value")
                literal = "TRUE" if value else "FALSE"
            else:
                literal = repr(number(value, "comparison value", minimum=-1e100, maximum=1e100))
            return self.add(f"({feature} {OPERATORS[operator]} {literal})")
        if len(node) != 1:
            raise ValueError("Use one logical/temporal operator per condition")
        kind, body = next(iter(node.items()))
        if kind in {"all", "any"}:
            if not isinstance(body, list) or not body:
                raise ValueError("all/any require a nonempty list")
            children = [self.predicate(child, depth+1) for child in body]
            return self.add("(" + (" AND " if kind == "all" else " OR ").join(children) + ")")
        if kind == "not":
            return self.add("NOT " + self.predicate(body, depth+1))
        if kind in {"held_for", "within"}:
            keys(body, {"bars", "condition"}, {"bars", "condition"})
            n = positive_integer(body["bars"], "bars")
            child = self.predicate(body["condition"], depth+1)
            return self.add(self.rolling(child, n, "bool_and" if kind == "held_for" else "bool_or"))
        if kind == "after_event":
            keys(body, {"bars", "event", "condition"}, {"bars", "event", "condition"})
            n = positive_integer(body["bars"], "bars")
            event = self.predicate(body["event"], depth+1)
            condition = self.predicate(body["condition"], depth+1)
            held = self.add(self.rolling(condition, n, "bool_and"))
            return self.add(f"lag({event}, {n}) OVER (PARTITION BY instrument ORDER BY bar_open_time) AND {held}")
        raise ValueError(f"Unsupported expression: {kind}")

    @staticmethod
    def rolling(child, n, aggregate):
        window = f"(PARTITION BY instrument ORDER BY bar_open_time ROWS BETWEEN {n-1} PRECEDING AND CURRENT ROW)"
        return f"CASE WHEN count({child}) OVER {window} = {n} THEN {aggregate}({child}) OVER {window} END"

    def compile(self, spec, instrument_filter=False):
        roots = {}
        for phase in ("entry", "exit"):
            for direction in ("long", "short"):
                roots[f"{phase}_{direction}"] = self.predicate(spec[phase].get(direction))
        ctes = ["s0 AS (SELECT * FROM features" + (" WHERE instrument=?" if instrument_filter else "") + ")"]
        for index, (name, expression) in enumerate(self.steps):
            ctes.append(f"s{index+1} AS (SELECT *, {expression} AS {name} FROM s{index})")
        output = ", ".join(f"coalesce({name}, FALSE) AS {label}" for label, name in roots.items())
        return "WITH " + ",\n".join(ctes) + f"\nSELECT instrument, bar_open_time, bar_close_time, {output} FROM s{len(self.steps)} ORDER BY instrument, bar_open_time"


def compile_strategy(spec, instrument_filter=False):
    return Compiler().compile(spec, instrument_filter)


def required_features(node):
    if isinstance(node, dict):
        own = {node["feature"]} if "feature" in node else set()
        return own.union(*(required_features(child) for child in node.values()))
    if isinstance(node, list):
        return set().union(*(required_features(child) for child in node))
    return set()
