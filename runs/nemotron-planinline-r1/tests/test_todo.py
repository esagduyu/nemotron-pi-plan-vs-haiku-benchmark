"""Pytest tests for the CLI todo manager."""

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

# We'll run todo.py as a subprocess with a TODO_FILE env var.
TODO_FILE_DEFAULT = Path("todos.json")


def _run_todo(*args: str, data_dir: str | None = None) -> subprocess.CompletedProcess:
    """Run the todo.py script with the given arguments.

    If data_dir is provided, set TODO_FILE env var to point to a temp file
    inside that directory.
    """
    env = os.environ.copy()
    if data_dir is not None:
        # Ensure TODO_FILE points to a JSON file in data_dir
        env["TODO_FILE"] = os.path.join(data_dir, "todos.json")
    return subprocess.run(
        [sys.executable, "todo.py", *args],
        capture_output=True,
        text=True,
        env=env,
    )


# ── Tests ─────────────────────────────────────────────────────────────────

def test_add_todo(tmp_path: Path) -> None:
    """Adding a todo prints the new ID."""
    result = _run_todo("add", "Buy milk", data_dir=str(tmp_path))
    assert result.returncode == 0
    assert result.stdout.strip() == "1"

    result = _run_todo("add", "Learn Python", data_dir=str(tmp_path))
    assert result.returncode == 0
    assert result.stdout.strip() == "2"


def test_list_todos(tmp_path: Path) -> None:
    """Listing todos shows [ID] [x|·] title format."""
    _run_todo("add", "Read book", data_dir=str(tmp_path))

    result = _run_todo("list", data_dir=str(tmp_path))
    assert result.returncode == 0
    assert "1" in result.stdout
    assert "[·]" in result.stdout or "[x]" in result.stdout


def test_mark_done(tmp_path: Path) -> None:
    """Marking a todo as done by ID works."""
    _run_todo("add", "Finish report", data_dir=str(tmp_path))

    result = _run_todo("done", "1", data_dir=str(tmp_path))
    assert result.returncode == 0

    result = _run_todo("list", data_dir=str(tmp_path))
    assert result.returncode == 0
    assert "[x]" in result.stdout
    assert "Finish report" in result.stdout


def test_rm_todo(tmp_path: Path) -> None:
    """Removing a todo by ID deletes it."""
    _run_todo("add", "Task A", data_dir=str(tmp_path))
    _run_todo("add", "Task B", data_dir=str(tmp_path))

    result = _run_todo("rm", "1", data_dir=str(tmp_path))
    assert result.returncode == 0

    result = _run_todo("list", data_dir=str(tmp_path))
    assert result.returncode == 0
    assert "Task A" not in result.stdout
    assert "Task B" in result.stdout


def test_clear_done(tmp_path: Path) -> None:
    """Clearing all done todos works."""
    _run_todo("add", "Open task", data_dir=str(tmp_path))
    _run_todo("add", "Closed task", data_dir=str(tmp_path))

    # Mark first as done
    _run_todo("done", "1", data_dir=str(tmp_path))

    result = _run_todo("clear", data_dir=str(tmp_path))
    assert result.returncode == 0

    # Only "Closed task" (the undone one) should remain
    result = _run_todo("list", data_dir=str(tmp_path))
    assert result.returncode == 0
    # "Open task" was marked done and should have been removed
    assert "Open task" not in result.stdout
    # "Closed task" (undone) should remain
    assert "Closed task" in result.stdout