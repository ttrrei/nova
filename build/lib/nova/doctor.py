"""Check the installed runtime without requiring optional modules at import time."""

import importlib
import importlib.metadata
import json
import platform


PACKAGES = {
    "duckdb": "duckdb",
    "pyarrow": "pyarrow",
    "numpy": "numpy",
    "pandas": "pandas",
    "talib": "TA-Lib",
    "yaml": "PyYAML",
    "pytz": "pytz",
}


def check_environment():
    packages = {}
    for module, distribution in PACKAGES.items():
        try:
            importlib.import_module(module)
            packages[module] = {
                "status": "ready",
                "version": importlib.metadata.version(distribution),
            }
        except (ImportError, OSError, importlib.metadata.PackageNotFoundError) as error:
            packages[module] = {"status": "unavailable", "error": str(error)}
    return {
        "status": "ready"
        if all(p["status"] == "ready" for p in packages.values())
        else "unavailable",
        "python": platform.python_version(),
        "packages": packages,
    }


def main():
    result = check_environment()
    print(json.dumps(result, indent=2))
    if result["status"] != "ready":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
