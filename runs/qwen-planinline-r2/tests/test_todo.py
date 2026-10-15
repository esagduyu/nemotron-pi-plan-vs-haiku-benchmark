"""Tests for the tiny CLI todo manager."""

import json
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest


def _run(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    """Run todo.py with the given args, using the specified cwd."""
    todo_path = Path(__file__).parent.parent / "todo.py"
    return subprocess.run(
        [sys.executable, str(todo_path)] + cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
    )


@pytest.fixture()
def tmp_todo_dir(tmp_path: Path) -> Path:
    """Create a temporary directory with no todos.json."""
    return tmp_path


class TestAdd:
    def test_add_creates_todo(self, tmp_todo_dir: Path) -> None:
        result = _run(["add", "Buy milk"], tmp_todo_dir)
        assert result.returncode == 0
        assert "Added todo 1: Buy milk" in result.stdout

        data = json.loads((tmp_todo_dir / "todos.json").read_text())
        assert len(data) == 1
        assert data[0]["id"] == 1
        assert data[0]["title"] == "Buy milk"
        assert data[0]["done"] is False

    def test_add_increments_id(self, tmp_todo_dir: Path) -> None:
        _run(["add", "First"], tmp_todo_dir)
        _run(["add", "Second"], tmp_todo_dir)

        data = json.loads((tmp_todo_dir / "todos.json").read_text())
        assert data[0]["id"] == 1
        assert data[1]["id"] == 2


class TestList:
    def test_list_empty(self, tmp_todo_dir: Path) -> None:
        result = _run(["list"], tmp_todo_dir)
        assert result.returncode == 0
        assert "No todos." in result.stdout

    def test_list_shows_status(self, tmp_todo_dir: Path) -> None:
        _run(["add", "Task one"], tmp_todo_dir)
        _run(["done", "1"], tmp_todo_dir)

        result = _run(["list"], tmp_todo_dir)
        assert result.returncode == 0
        assert "[1] [x] Task one" in result.stdout

    def test_list_shows_open(self, tmp_todo_dir: Path) -> None:
        _run(["add", "Task two"], tmp_todo_dir)

        result = _run(["list"], tmp_todo_dir)
        assert "[2] [·] Task two" in result.stdout or "[1] [·] Task two" in result.stdout


class TestDone:
    def test_done_marks_todo(self, tmp_todo_dir: Path) -> None:
        _run(["add", "Do laundry"], tmp_todo_dir)
        result = _run(["done", "1"], tmp_todo_dir)
        assert result.returncode == 0
        assert "marked done" in result.stdout

        data = json.loads((tmp_todo_dir / "todos.json").read_text())
        assert data[0]["done"] is True

    def test_done_invalid_id(self, tmp_todo_dir: Path) -> None:
        result = _run(["done", "999"], tmp_todo_dir)
        assert result.returncode != 0
        assert "no todo with ID 999" in result.stderr


class TestRm:
    def test_rm_deletes_todo(self, tmp_todo_dir: Path) -> None:
        _run(["add", "Remove me"], tmp_todo_dir)
        result = _run(["rm", "1"], tmp_todo_dir)
        assert result.returncode == 0
        assert "Deleted todo 1" in result.stdout

        data = json.loads((tmp_todo_dir / "todos.json").read_text())
        assert len(data) == 0

    def test_rm_invalid_id(self, tmp_todo_dir: Path) -> None:
        result = _run(["rm", "42"], tmp_todo_dir)
        assert result.returncode != 0
        assert "no todo with ID 42" in result.stderr


class TestClear:
    def test_clear_removes_done(self, tmp_todo_dir: Path) -> None:
        _run(["add", "Keep me"], tmp_todo_dir)
        _run(["add", "Gone"], tmp_todo_dir)
        _run(["done", "2"], tmp_todo_dir)

        result = _run(["clear"], tmp_todo_dir)
        assert result.returncode == 0
        assert "1 done" in result.stdout

        data = json.loads((tmp_todo_dir / "todos.json").read_text())
        assert len(data) == 1
        assert data[0]["title"] == "Keep me"

    def test_clear_no_done(self, tmp_todo_dir: Path) -> None:
        _run(["add", "Open task"], tmp_todo_dir)
        result = _run(["clear"], tmp_todo_dir)
        assert result.returncode == 0
        assert "0 done" in result.stdout
