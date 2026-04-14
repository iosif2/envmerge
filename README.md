# envsync

`envsync` syncs `.env` from `.env.example` with predictable ordering and minimal drift.

## Install

```bash
uv sync --group dev
uv run envsync --help
```

## Commands

```bash
uv run envsync sync
uv run envsync sync --dry-run
uv run envsync check
uv run envsync diff --format=json
```

## Development

```bash
pre-commit install
uv run pytest
pre-commit run --all-files
```
