# envmerge

`envmerge` syncs `.env` from `.env.example` with predictable ordering and minimal drift.

## Install

```bash
uv sync --group dev
uv run envmerge --help
```

## Commands

```bash
uv run envmerge sync
uv run envmerge sync --dry-run
uv run envmerge check
uv run envmerge diff --format=json
```

## Development

```bash
pre-commit install
uv run pytest
pre-commit run --all-files
```
