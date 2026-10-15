"""Pytest tests for the todo manager CLI."""

import json
import os
import subprocess
import sys
import tempfile

import pytest

TODO_SCRIPT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "todo.py")


def _run_todo(*args, cwd=None):
    """Run the todo.py script and return (returncode, stdout, stderr)."""
    result = subprocess.run(
        [sys.executable, TODO_SCRIPT, *args],
        capture_output=True,
        text=True,
        cwd=cwd,
    )
    return result.returncode, result.stdout.strip(), result.stderr.strip()


class TestAdd:
    def test_add_creates_todo_and_prints_id(self, tmp_path):
        rc, stdout, stderr = _run_todo("add", "Buy milk", cwd=tmp_path)
        assert rc == 0
        assert stdout.strip().isdigit()
        todo_id = int(stdout.strip())
        # Verify the todo was persisted
        todos_path = os.path.join(tmp_path, "todos.json")
        assert os.path.exists(todos_path)
        with open(todos_path) as f:
            todos = json.load(f)
        assert len(todos) == 1
        assert todos[0]["title"] == "Buy milk"
        assert todos[0]["done"] is False
        assert todos[0]["id"] == todo_id

    def test_add_multiple_ids_monotonically_increasing(self, tmp_path):
        rc1, stdout1, _ = _run_todo("add", "First", cwd=tmp_path)
        assert rc1 == 0
        rc2, stdout2, _ = _run_todo("add", "Second", cwd=tmp_path)
        assert rc2 == 0
        rc3, stdout3, _ = _run_todo("add", "Third", cwd=tmp_path)
        assert rc3 == 0
        # IDs should be 1, 2, 3 (monotonically increasing, never reused)
        assert int(stdout1.strip()) == 1
        assert int(stdout2.strip()) == 2
        assert int(stdout3.strip()) == 3


class TestList:
    def test_list_empty(self, tmp_path):
        rc, stdout, stderr = _run_todo("list", cwd=tmp_path)
        assert rc == 0
        assert stdout == "No todos."

    def test_list_todos(self, tmp_path):
        _run_todo("add", "Walk the dog", cwd=tmp_path)
        _run_todo("add", "Wash car", cwd=tmp_path)
        rc, stdout, stderr = _run_todo("list", cwd=tmp_path)
        assert rc == 0
        lines = stdout.strip().split("\n")
        assert len(lines) == 2  # two todos, no extra header
        # Check format: [ID] [x|·] title
        assert "Walk the dog" in stdout
        assert "Wash car" in stdout


class TestDone:
    def test_done_marks_todo_done(self, tmp_path):
        _run_todo("add", "Study Python", cwd=tmp_path)
        rc, stdout, stderr = _run_todo("done", "1", cwd=tmp_path)
        assert rc == 0
        # List should show x marker
        rc2, stdout2, _ = _run_todo("list", cwd=tmp_path)
        assert rc2 == 0
        assert "x" in stdout2
        assert "Study Python" in stdout2

    def test_done_invalid_id_errors(self, tmp_path):
        _run_todo("add", "Test todo", cwd=tmp_path)
        rc, _, stderr = _run_todo("done", "999", cwd=tmp_path)
        assert rc != 0
        assert "Error" in stderr


class TestRm:
    def test_rm_removes_todo(self, tmp_path):
        _run_todo("add", "Temporary task", cwd=tmp_path)
        rc, stdout, stderr = _run_todo("rm", "1", cwd=tmp_path)
        assert rc == 0
        rc2, stdout2, _ = _run_todo("list", cwd=tmp_path)
        assert rc2 == 0
        assert "Temporary task" not in stdout2

    def test_rm_invalid_id_errors(self, tmp_path):
        rc, _, stderr = _run_todo("rm", "999", cwd=tmp_path)
        assert rc != 0
        assert "Error" in stderr


class TestClear:
    def test_clear_removes_done_todos(self, tmp_path):
        _run_todo("add", "Open todo 1", cwd=tmp_path)
        _run_todo("add", "Open todo 2", cwd=tmp_path)
        # Mark one as done
        _run_todo("done", "1", cwd=tmp_path)
        # Clear done todos
        rc, _, _ = _run_todo("clear", cwd=tmp_path)
        assert rc == 0
        rc2, stdout2, _ = _run_todo("list", cwd=tmp_path)
        assert rc2 == 0
        # Only the open todo should remain
        assert "Open todo 2" in stdout2
        assert "Open todo 1" not in stdout2