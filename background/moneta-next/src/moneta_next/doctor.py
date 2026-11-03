"""Dependency checks that work before DuckDB is installed."""
import importlib.util
import json


def main():
    groups = {"base": ["duckdb", "yaml", "numpy"], "legacy_recompute": ["pandas", "talib", "pandas_ta_classic"], "download": ["requests"]}
    report = {group: {name: importlib.util.find_spec(name) is not None for name in names} for group, names in groups.items()}
    print(json.dumps(report, indent=2))
    return report


if __name__ == "__main__":
    main()
