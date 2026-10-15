"""Tests for the tiny CLI todo manager."""

import json
import os
import subprocess
import sys
import tempfile

import pytest

PYTHON = sys.executable
SCRIPT = os.path.join(os.path.dirname(__file__), "..", "todo.py")


def run_todo(*args: str, cwd: str | None = None) -> subprocess.CompletedProcess[str]:
    """Run todo.py with given args, returning the CompletedProcess."""
    result = subprocess.run(
        [PYTHON, SCRIPT, *args],
        capture_output=True,
        text=True,
        cwd=cwd,
    )
    return result


class TestAdd:
    def test_add_creates_todo(self, tmp_path):
        """Adding a todo creates it in the JSON file and prints the ID."""
        todos_file = tmp_path / "todos.json"
        result = run_todo("--todos", str(todos_file), "add", "Buy milk")
        assert result.returncode == 0
        assert "Added todo 1" in result.stdout

        with open(todos_file) as f:
            todos = json.load(f)
        assert len(todos) == 1
        assert todos[0]["id"] == 1
        assert todos[0]["title"] == "Buy milk"
        assert todos[0]["done"] is False

    def test_add_increments_id(self, tmp_path):
        """Adding multiple todos yields monotonically increasing IDs."""
        todos_file = tmp_path / "todos.json"
        run_todo("--todos", str(todos_file), "add", "First")
        run_todo("--todos", str(todos_file), "add", "Second")
        run_todo("--todos", str(todos_file), "add", "Third")

        result = run_todo("--todos", str(todos_file), "add", "Fourth")
        assert "Added todo 4" in result.stdout


class TestList:
    def test_list_shows_all_todos(self, tmp_path):
        """List prints all todos with correct format."""
        todos_file = tmp_path / "todos.json"
        run_todo("--todos", str(todos_file), "add", "Alpha")
        run_todo("--todos", str(todos_file), "add", "Beta")

        result = run_todo("--todos", str(todos_file), "list")
        assert result.returncode == 0
        lines = [l for l in result.stdout.strip().splitlines() if l.strip()]
        assert len(lines) == 2
        assert "[1] [·] Alpha" in lines[0]
        assert "[2] [·] Beta" in lines[1]

    def test_list_shows_done_status(self, tmp_path):
        """List shows x for done and · for open todos."""
        todos_file = tmp_path / "todos.json"
        run_todo("--todos", str(todos_file), "add", "Task")
        run_todo("--todos", str(todos_file), "done", "1")

        result = run_todo("--todos", str(todos_file), "list")
        assert "[1] [x] Task" in result.stdout


class TestDone:
    def test_done_marks_todo(self, tmp_path):
        """Marking a todo as done sets done=True."""
        todos_file = tmp_path / "todos.json"
        run_todo("--todos", str(todos_file), "add", "Task")
        result = run_todo("--todos", str(todos_file), "done", "1")
        assert result.returncode == 0
        assert "done" in result.stdout.lower()

        with open(todos_file) as f:
            todos = json.load(f)
        assert todos[0]["done"] is True

    def test_done_invalid_id(self, tmp_path):
        """Marking a non-existent ID prints error and exits non-zero."""
        todos_file = tmp_path / "todos.json"
        result = run_todo("--todos", str(todos_file), "done", "999")
        assert result.returncode != 0
        assert "Error" in result.stderr


class TestRm:
    def test_rm_removes_todo(self, tmp_path):
        """Removing a todo deletes it from the file."""
        todos_file = tmp_path / "todos.json"
        run_todo("--todos", str(todos_file), "add", "ToDelete")
        run_todo("--todos", str(todos_file), "add", "Keep")
        result = run_todo("--todos", str(todos_file), "rm", "1")
        assert result.returncode == 0
        assert "Removed todo 1" in result.stdout

        with open(todos_file) as f:
            todos = json.load(f)
        assert len(todos) == 1
        assert todos[0]["title"] == "Keep"

    def test_rm_invalid_id(self, tmp_path):
        """Removing a non-existent ID prints error and exits non-zero."""
        todos_file = tmp_path / "todos.json"
        result = run_todo("--todos", str(todos_file), "rm", "999")
        assert result.returncode != 0
        assert "Error" in result.stderr
