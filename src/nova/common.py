"""Small deterministic artifact helpers."""

import hashlib
import gzip
import io
import json
import os
from contextlib import contextmanager
from pathlib import Path


def file_hash(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(4 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def identity(value):
    return hashlib.sha256(
        json.dumps(
            value, sort_keys=True, separators=(",", ":"), default=str, allow_nan=False
        ).encode()
    ).hexdigest()


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(value, indent=2, sort_keys=True, default=str, allow_nan=False) + "\n"
    )
    os.replace(temporary, path)


def sql_string(value):
    return "'" + str(value).replace("'", "''") + "'"


@contextmanager
def open_text(path, mode="r", newline=None):
    """Open plain or gzip text, with reproducible gzip headers for new writes."""
    path = Path(path)
    if mode not in ("r", "w"):
        raise ValueError("Text artifacts support read or write mode only")
    if path.suffix != ".gz":
        with path.open(mode, encoding="utf-8", newline=newline) as stream:
            yield stream
    elif mode == "r":
        with gzip.open(path, "rt", encoding="utf-8", newline=newline) as stream:
            yield stream
    else:
        with path.open("wb") as raw:
            with gzip.GzipFile(
                fileobj=raw, mode="wb", filename="", mtime=0, compresslevel=1
            ) as compressed:
                with io.TextIOWrapper(
                    compressed, encoding="utf-8", newline=newline
                ) as stream:
                    yield stream


def csv_artifact(directory, name):
    """Resolve one published CSV in either its plain or compressed format."""
    path = Path(directory) / name
    candidates = [
        candidate
        for candidate in (path, path.with_suffix(path.suffix + ".gz"))
        if candidate.is_file()
    ]
    if len(candidates) != 1:
        raise ValueError(f"Expected one plain or gzip CSV artifact: {path}")
    return candidates[0]
