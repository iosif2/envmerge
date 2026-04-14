from __future__ import annotations

from .diff import DiffResult


def print_check(result: DiffResult, *, strict: bool = False) -> str:
    lines: list[str] = []
    if result.removed:
        lines.append("Missing keys:")
        lines.extend(f"- {key}" for key in result.removed)
    if result.added:
        lines.append("Extra keys:")
        lines.extend(f"- {key}" for key in result.added)
    if strict and result.empty:
        lines.append("Empty values:")
        lines.extend(f"- {key}" for key in result.empty)
    return "\n".join(lines)


def print_diff(result: DiffResult) -> str:
    lines: list[str] = []
    lines.extend(f"+ {key}" for key in result.added)
    lines.extend(f"- {key}" for key in result.removed)
    lines.extend(f"~ {key}" for key in result.changed)
    return "\n".join(lines)
