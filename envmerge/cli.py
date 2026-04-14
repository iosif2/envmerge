from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .core import sync_env
from .diff import _diff, diff_to_json
from .parser import parse_env_file
from .printer import print_check, print_diff

EXIT_SUCCESS = 0
EXIT_VALIDATION_ERROR = 1
EXIT_FILE_MISSING = 2


def _add_common_paths(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--example", default=".env.example", help="Path to .env.example")
    parser.add_argument("--env", default=".env", help="Path to .env")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="envmerge", description="Sync .env files")
    subparsers = parser.add_subparsers(dest="command", required=True)

    sync_parser = subparsers.add_parser("sync", help="Rebuild .env from .env.example")
    _add_common_paths(sync_parser)
    sync_parser.add_argument("--dry-run", action="store_true", help="Print result only")
    sync_parser.add_argument(
        "--keep-extra",
        action="store_true",
        help="Keep keys that exist only in .env",
    )
    sync_parser.add_argument(
        "--empty-missing",
        action="store_true",
        help="Use empty values for missing keys instead of example defaults",
    )

    check_parser = subparsers.add_parser("check", help="Validate drift against .env.example")
    _add_common_paths(check_parser)
    check_parser.add_argument("--strict", action="store_true", help="Report empty values")

    diff_parser = subparsers.add_parser("diff", help="Show drift summary")
    _add_common_paths(diff_parser)
    diff_parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Output format",
    )
    diff_parser.add_argument("--strict", action="store_true", help="Include empty values")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if args.command == "sync":
            return _handle_sync(args)
        if args.command == "check":
            return _handle_check(args)
        if args.command == "diff":
            return _handle_diff(args)
    except FileNotFoundError as exc:
        print(f"file missing: {exc}", file=sys.stderr)
        return EXIT_FILE_MISSING
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return EXIT_VALIDATION_ERROR

    return EXIT_SUCCESS


def _handle_sync(args: argparse.Namespace) -> int:
    result = sync_env(
        args.example,
        args.env,
        keep_extra=args.keep_extra,
        empty_missing=args.empty_missing,
    )
    _emit_warnings(args.example, result.example.warnings)
    _emit_warnings(args.env, result.current.warnings)
    output = "\n".join(result.lines) + "\n"
    if args.dry_run:
        sys.stdout.write(output)
        return EXIT_SUCCESS
    Path(args.env).write_text(output, encoding="utf-8")
    return EXIT_SUCCESS


def _handle_check(args: argparse.Namespace) -> int:
    example = parse_env_file(args.example, missing_ok=False)
    current = parse_env_file(args.env, missing_ok=True)
    _emit_warnings(args.example, example.warnings)
    _emit_warnings(args.env, current.warnings)
    result = _diff(example, current, strict=args.strict)
    output = print_check(result, strict=args.strict)
    if output:
        print(output)
        return EXIT_VALIDATION_ERROR
    return EXIT_SUCCESS


def _handle_diff(args: argparse.Namespace) -> int:
    example = parse_env_file(args.example, missing_ok=False)
    current = parse_env_file(args.env, missing_ok=True)
    _emit_warnings(args.example, example.warnings)
    _emit_warnings(args.env, current.warnings)
    result = _diff(example, current, strict=args.strict)
    if args.format == "json":
        print(diff_to_json(result))
    else:
        output = print_diff(result)
        if output:
            print(output)
    return (
        EXIT_SUCCESS
        if not (result.added or result.removed or result.changed or (args.strict and result.empty))
        else EXIT_VALIDATION_ERROR
    )


def _emit_warnings(path: str, warnings: list[str]) -> None:
    for warning in warnings:
        print(warning, file=sys.stderr)


if __name__ == "__main__":
    raise SystemExit(main())
