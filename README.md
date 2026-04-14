# envmerge

Sync `.env` from `.env.example` — deterministic ordering, zero drift.

```bash
uvx envmerge sync
```

## Usage

```bash
envmerge sync                # rebuild .env from .env.example
envmerge sync --dry-run      # preview without writing
envmerge check               # exit 1 if .env is out of sync
envmerge diff                # show what drifted
envmerge diff --format=json  # machine-readable
```

## Install

```bash
uv tool install envmerge   # global CLI
uv add envmerge            # project dependency
```

## Development

```bash
uv sync --group dev
prek install
uv run pytest
```
