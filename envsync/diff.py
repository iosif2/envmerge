from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
import json

from .parser import ParsedEnv, parse_env_file


@dataclass(slots=True)
class DiffResult:
    added: list[str]
    removed: list[str]
    changed: list[str]
    empty: list[str]

    def to_dict(self) -> dict[str, list[str]]:
        return asdict(self)


def diff_env(
    example_path: str | Path = ".env.example",
    current_path: str | Path = ".env",
    *,
    strict: bool = False,
) -> DiffResult:
    example = parse_env_file(example_path, missing_ok=False)
    current = parse_env_file(current_path, missing_ok=True)
    return _diff(example, current, strict=strict)


def _diff(example: ParsedEnv, current: ParsedEnv, *, strict: bool) -> DiffResult:
    example_values = example.values
    current_values = current.values
    example_keys = set(example_values)
    current_keys = set(current_values)

    added = [key for key, _ in current.entries if key not in example_keys]
    removed = [key for key, _ in example.entries if key not in current_keys]
    changed = [
        key
        for key, _ in example.entries
        if key in current_values and current_values[key] != example_values[key]
    ]
    empty = [
        key
        for key, _ in current.entries
        if key in example_keys and current_values[key] == ""
    ]
    if not strict:
        empty = []
    return DiffResult(added=added, removed=removed, changed=changed, empty=empty)


def diff_to_json(result: DiffResult) -> str:
    return json.dumps(result.to_dict(), ensure_ascii=False, indent=2)
