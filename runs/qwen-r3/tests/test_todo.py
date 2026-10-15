"""Tests for the CLI todo manager."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

PYTHON = sys.executable
SCRIPT = Path(__file__).resolve().parent.parent / "todo.py"


def _run(args: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    """Run todo.py with extra args, returning the completed process."""
    return subprocess.run(
        [PYTHON, str(SCRIPT), *args],
        cwd=cwd,
        capture_output=True,
        text=True,
    )


# ── fixtures ─────────────────────────────────────────────────────────


@pytest.fixture()
def tmp_todo(tmp_path: Path) -> Path:
    """Create a temporary directory that already contains a todos.json."""
    todos_file = tmp_path / "todos.json"
    todos_file.write_text("[]", encoding="utf-8")
    return tmp_path


# ── tests ────────────────────────────────────────────────────────────


def test_add(tmp_todo: Path) -> None:
    """Adding a todo creates it in the JSON file and prints the ID."""
    result = _run(["add", "Buy milk"], tmp_todo)
    assert result.returncode == 0
    assert "Added todo #1" in result.stdout

    raw = json.loads((tmp_todo / "todos.json").read_text())
    todos = raw.get("todos", raw) if isinstance(raw, dict) else raw
    assert len(todos) == 1
    assert todos[0]["id"] == 1
    assert todos[0]["title"] == "Buy milk"
    assert todos[0]["done"] is False


def test_list(tmp_todo: Path) -> None:
    """List prints todos in the expected format."""
    _run(["add", "Alpha"], tmp_todo)
    _run(["add", "Beta"], tmp_todo)

    # Mark one done
    _run(["done", "1"], tmp_todo)

    result = _run(["list"], tmp_todo)
    assert result.returncode == 0
    lines = [l for l in result.stdout.strip().splitlines() if l.strip()]
    assert len(lines) == 2
    assert lines[0] == "[1] [x] Alpha"
    assert lines[1] == "[2] [·] Beta"


def _get_todos_list(tmp_todo: Path) -> list:
    """Helper to extract the todos list from the JSON file."""
    raw = json.loads((tmp_todo / "todos.json").read_text())
    return raw.get("todos", raw) if isinstance(raw, dict) else raw


def test_done(tmp_todo: Path) -> None:
    """Marking a todo done sets done=True; invalid ID errors."""
    _run(["add", "Test"], tmp_todo)

    result = _run(["done", "1"], tmp_todo)
    assert result.returncode == 0
    assert "Marked todo #1 as done" in result.stdout

    # Invalid ID
    result_bad = _run(["done", "99"], tmp_todo)
    assert result_bad.returncode != 0
    assert "no todo with ID 99" in result_bad.stderr


def test_rm(tmp_todo: Path) -> None:
    """Removing a todo deletes it; ID is never reused."""
    _run(["add", "To remove"], tmp_todo)

    result = _run(["rm", "1"], tmp_todo)
    assert result.returncode == 0
    assert "Removed todo #1" in result.stdout

    raw = json.loads((tmp_todo / "todos.json").read_text())
    todos = raw.get("todos", raw) if isinstance(raw, dict) else raw
    assert len(todos) == 0

    # After removal, next ID should be 2 (not 1)
    _run(["add", "New item"], tmp_todo)
    raw2 = json.loads((tmp_todo / "todos.json").read_text())
    todos2 = raw2.get("todos", raw2) if isinstance(raw2, dict) else raw2
    assert todos2[0]["id"] == 2

    # Invalid ID
    result_bad = _run(["rm", "42"], tmp_todo)
    assert result_bad.returncode != 0
    assert "no todo with ID 42" in result_bad.stderr
