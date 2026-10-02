"""Write-once store for frozen hashes (protocol §3.4).

`configs/frozen_hashes.yaml` holds every value that later checks compare against. Each entry is
written once, at its stage, and never edited. `write_once` enforces this: writing a key that already
holds the same value is a no-op; writing a different value raises.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

DEFAULT_PATH = Path("configs/frozen_hashes.yaml")

_HEADER = (
    "# Frozen hashes — protocol §3.4.\n"
    "# Each entry is written once, at its stage, by code. Never edit by hand.\n"
)


class FrozenHashConflict(RuntimeError):
    """Raised when a frozen key already holds a different value."""


def read_frozen_hashes(path: Path | str = DEFAULT_PATH) -> dict[str, Any]:
    """Return the frozen-hash mapping, or an empty dict if the file does not exist."""
    path = Path(path)
    if not path.exists():
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if data is None:
        return {}
    if not isinstance(data, dict):
        raise ValueError(f"{path}: expected a mapping at top level, got {type(data).__name__}")
    return data


def write_once(path: Path | str, key: str, value: Any) -> bool:
    """Write `key: value` to the frozen-hash file unless already present.

    Returns True if the key was written, False if it already held the same value.
    Raises FrozenHashConflict if it holds a different value. Other keys are preserved; keys are
    written in sorted order.
    """
    path = Path(path)
    data = read_frozen_hashes(path)
    if key in data:
        if data[key] != value:
            raise FrozenHashConflict(
                f"{path}: key {key!r} is frozen as {data[key]!r}; refusing to write {value!r}"
            )
        return False
    data[key] = value
    path.parent.mkdir(parents=True, exist_ok=True)
    body = yaml.safe_dump(data, sort_keys=True, default_flow_style=False, allow_unicode=True)
    path.write_text(_HEADER + body, encoding="utf-8")
    return True
