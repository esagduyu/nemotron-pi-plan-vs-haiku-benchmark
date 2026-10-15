"""Tests for the CLI todo manager."""

from __future__ import annotations

import json
import sys
from io import StringIO
from pathlib import Path
from types import ModuleType

import contextlib
import pytest

# Ensure todo.py is importable regardless of cwd.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import todo  # noqa: E402


@pytest.fixture
def patched_data_file(tmp_path: Path) -> Path:
    """Temporarily swap DATA_FILE to a path inside tmp_path and restore after."""
    original = todo.DATA_FILE
    target = tmp_path / "todos.json"
    todo.DATA_FILE = target
    yield target
    todo.DATA_FILE = original


# ── helpers ──────────────────────────────────────────────────────────────────

def _capture_output(func) -> str:
    """Run *func* and return its stdout as a string."""
    buf = StringIO()
    with contextlib.redirect_stdout(buf):
        func()
    return buf.getvalue()


def _real_todos(raw_data: list[dict]) -> list[dict]:
    """Filter out the hidden sentinel entry from raw JSON data."""
    return [t for t in raw_data if t["title"] != todo._SENTRY_KEY]


# ── add ──────────────────────────────────────────────────────────────────────

class TestAdd:
    def test_add_creates_file(self, patched_data_file: Path) -> None:
        """Adding a todo should create the JSON file with correct schema."""
        sys.argv = ["todo", "add", "Buy milk"]
        todo.main()

        data = json.loads(patched_data_file.read_text())
        todos = _real_todos(data)
        assert len(todos) == 1
        assert todos[0] == {"id": 1, "title": "Buy milk", "done": False}

    def test_add_increments_id(self, patched_data_file: Path) -> None:
        """IDs should be monotonically increasing."""
        for title in ("First", "Second", "Third"):
            sys.argv = ["todo", "add", title]
            todo.main()

        data = json.loads(patched_data_file.read_text())
        todos = _real_todos(data)
        ids = [t["id"] for t in todos]
        assert ids == [1, 2, 3]


# ── list ─────────────────────────────────────────────────────────────────────

class TestList:
    def test_list_empty(self, patched_data_file: Path) -> None:
        """Listing with no todos should print (none)."""
        output = _capture_output(lambda: todo.cmd_list(None))
        assert "(none)" in output

    def test_list_shows_status(self, patched_data_file: Path) -> None:
        """List should show x for done and · for open."""
        sys.argv = ["todo", "add", "Task one"]
        todo.main()
        sys.argv = ["todo", "add", "Task two"]
        todo.main()
        sys.argv = ["todo", "done", "1"]
        todo.main()

        output = _capture_output(lambda: todo.cmd_list(None))
        assert "[1] [x]" in output
        assert "[2] [·]" in output


# ── done ─────────────────────────────────────────────────────────────────────

class TestDone:
    def test_done_marks_as_done(self, patched_data_file: Path) -> None:
        """Marking a todo done should set done=True."""
        sys.argv = ["todo", "add", "Wash car"]
        todo.main()
        sys.argv = ["todo", "done", "1"]
        todo.main()

        data = json.loads(patched_data_file.read_text())
        todos = _real_todos(data)
        assert todos[0]["done"] is True

    def test_done_invalid_id(self, patched_data_file: Path) -> None:
        """Done with a non-existent ID should fail gracefully."""
        sys.argv = ["todo", "done", "999"]
        with pytest.raises(SystemExit) as exc_info:
            todo.main()
        assert exc_info.value.code != 0


# ── rm ───────────────────────────────────────────────────────────────────────

class TestRm:
    def test_rm_removes_todo(self, patched_data_file: Path) -> None:
        """Removing a todo should delete it from the file."""
        sys.argv = ["todo", "add", "Temp task"]
        todo.main()
        sys.argv = ["todo", "rm", "1"]
        todo.main()

        data = json.loads(patched_data_file.read_text())
        todos = _real_todos(data)
        assert len(todos) == 0

    def test_rm_invalid_id(self, patched_data_file: Path) -> None:
        """RM with a non-existent ID should fail gracefully."""
        sys.argv = ["todo", "rm", "42"]
        with pytest.raises(SystemExit) as exc_info:
            todo.main()
        assert exc_info.value.code != 0

    def test_rm_id_not_reused(self, patched_data_file: Path) -> None:
        """After rm, the next ID should still increment (never reused)."""
        sys.argv = ["todo", "add", "First"]
        todo.main()
        sys.argv = ["todo", "rm", "1"]
        todo.main()
        sys.argv = ["todo", "add", "Second"]
        todo.main()

        data = json.loads(patched_data_file.read_text())
        todos = _real_todos(data)
        assert len(todos) == 1
        assert todos[0]["id"] == 2  # not 1
