from pathlib import Path

from envsync.core import sync_env
from envsync.parser import parse_env_text


def test_sync_preserves_example_comments_and_blank_lines(tmp_path: Path):
    example = tmp_path / ".env.example"
    current = tmp_path / ".env"
    example.write_text(
        "\n".join(
            [
                "# database settings",
                "DB_HOST=localhost",
                "",
                "# api settings",
                "API_KEY=",
            ]
        ),
        encoding="utf-8",
    )
    current.write_text("DB_HOST=prod-db\n", encoding="utf-8")

    result = sync_env(example, current)

    assert result.lines == [
        "# database settings",
        "DB_HOST=prod-db",
        "",
        "# api settings",
        "API_KEY=",
    ]


def test_sync_dry_run_keeps_comment_lines_in_output(tmp_path: Path):
    example = tmp_path / ".env.example"
    current = tmp_path / ".env"
    example.write_text("# header\nKEY=value\n", encoding="utf-8")
    current.write_text("", encoding="utf-8")

    result = sync_env(example, current)

    assert "# header" in result.lines


def test_parser_keeps_comment_lines_as_raw_entries():
    parsed = parse_env_text("# one\nKEY=value\n# two\n")

    assert [line.kind for line in parsed.lines] == ["comment", "kv", "comment"]
    assert [line.raw for line in parsed.lines if line.kind == "comment"] == [
        "# one",
        "# two",
    ]
