from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .parser import ParsedEnv, parse_env_file


@dataclass(slots=True)
class SyncResult:
    lines: list[str]
    example: ParsedEnv
    current: ParsedEnv


def sync_env(
    example_path: str | Path = ".env.example",
    current_path: str | Path = ".env",
    *,
    keep_extra: bool = False,
    empty_missing: bool = False,
) -> SyncResult:
    example = parse_env_file(example_path, missing_ok=False)
    current = parse_env_file(current_path, missing_ok=True)
    return SyncResult(
        lines=_render_sync_lines(
            example=example,
            current=current,
            keep_extra=keep_extra,
            empty_missing=empty_missing,
        ),
        example=example,
        current=current,
    )


def _render_sync_lines(
    *,
    example: ParsedEnv,
    current: ParsedEnv,
    keep_extra: bool,
    empty_missing: bool,
) -> list[str]:
    current_values = current.values
    example_keys = {key for key, _ in example.entries}
    rendered: list[str] = []

    for line in example.lines:
        if line.kind in {"blank", "comment", "invalid"}:
            rendered.append(line.raw)
            continue
        if line.kind != "kv" or line.key is None:
            rendered.append(line.raw)
            continue

        value = current_values.get(line.key)
        if value is None:
            value = "" if empty_missing else (line.value or "")
        rendered.append(f"{line.key}={_format_value(value)}")

    if keep_extra:
        for key, value in current.entries:
            if key not in example_keys:
                rendered.append(f"{key}={_format_value(value)}")

    return rendered


def _format_value(value: str) -> str:
    if value == "":
        return ""
    if _is_safe_unquoted(value):
        return value
    escaped = (
        value.replace("\\", r"\\").replace('"', r"\"").replace("\n", r"\n").replace("\t", r"\t")
    )
    return f'"{escaped}"'


def _is_safe_unquoted(value: str) -> bool:
    if value != value.strip():
        return False
    if any(ch in value for ch in [" ", "\t", "\n", "\r", "#", '"', "'"]):
        return False
    return True
