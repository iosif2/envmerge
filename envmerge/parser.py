from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

KEY_RE = re.compile(r"^[A-Z0-9_]+$")

LineKind = Literal["blank", "comment", "kv", "invalid"]


@dataclass(slots=True)
class ParsedLine:
    kind: LineKind
    raw: str
    key: str | None = None
    value: str | None = None
    line_no: int = 0


@dataclass(slots=True)
class ParsedEnv:
    values: dict[str, str]
    entries: list[tuple[str, str]]
    lines: list[ParsedLine]
    warnings: list[str]


def parse_env(path: str | Path) -> tuple[dict[str, str], list[str]]:
    parsed = parse_env_file(path, missing_ok=False)
    return parsed.values, [line.raw for line in parsed.lines]


def parse_env_file(path: str | Path, *, missing_ok: bool) -> ParsedEnv:
    file_path = Path(path)
    if not file_path.exists():
        if missing_ok:
            return ParsedEnv(values={}, entries=[], lines=[], warnings=[])
        raise FileNotFoundError(str(file_path))
    return parse_env_text(file_path.read_text(encoding="utf-8"), source=str(file_path))


def parse_env_text(text: str, *, source: str = "<memory>") -> ParsedEnv:
    values: dict[str, str] = {}
    entries: list[tuple[str, str]] = []
    lines: list[ParsedLine] = []
    warnings: list[str] = []

    for index, raw_line in enumerate(text.splitlines(), start=1):
        stripped = raw_line.strip()
        if not stripped:
            lines.append(ParsedLine(kind="blank", raw=raw_line, line_no=index))
            continue
        if stripped.startswith("#"):
            lines.append(ParsedLine(kind="comment", raw=raw_line, line_no=index))
            continue

        kv = _parse_key_value_line(raw_line, source=source, line_no=index)
        if kv is None:
            warnings.append(f"{source}:{index}: warning: malformed line ignored")
            lines.append(ParsedLine(kind="invalid", raw=raw_line, line_no=index))
            continue

        key, value = kv
        values[key] = value
        entries.append((key, value))
        lines.append(ParsedLine(kind="kv", raw=raw_line, key=key, value=value, line_no=index))

    return ParsedEnv(values=values, entries=entries, lines=lines, warnings=warnings)


def _parse_key_value_line(raw_line: str, *, source: str, line_no: int) -> tuple[str, str] | None:
    text = raw_line.strip()
    if text.startswith("export "):
        text = text[len("export ") :].lstrip()

    if "=" not in text:
        return None

    key_part, value_part = text.split("=", 1)
    key = key_part.strip()
    if not KEY_RE.fullmatch(key):
        return None

    value = _parse_value(value_part)
    return key, value


def _parse_value(value_part: str) -> str:
    value = value_part.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        inner = value[1:-1]
        if value[0] == '"':
            inner = (
                inner.replace(r"\\", "\\")
                .replace(r"\"", '"')
                .replace(r"\n", "\n")
                .replace(r"\t", "\t")
            )
        return inner
    return value
