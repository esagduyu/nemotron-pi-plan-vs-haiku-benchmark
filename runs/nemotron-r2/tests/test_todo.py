"""Pytest tests for the todo CLI manager using a temp JSON file."""

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

TODO_FILE = Path("todos.json")
TODO_SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "todo.py")


@pytest.fixture
def tmp_todo_dir():
    """Provide a temporary directory with its own todos.json, isolated from cwd."""
    with tempfile.TemporaryDirectory() as tmpdir:
        json_path = os.path.join(tmpdir, "todos.json")
        # Symlink ./todos.json -> tmpdir/todos.json so the app uses it
        # but we need to be in that directory when running.
        # Instead, we'll just copy the todo.py logic or patch the constant.
        # Simplest: change cwd to tmpdir and run; the app reads ./todos.json.
        # But we also need to prevent side-effects on the real cwd.
        # We'll just run from tmpdir and accept the file lives there.
        # To keep cwd clean, we'll remove todos.json from tmpdir after.
        # Actually, let's just use the real ./todos.json but save/restore.
        # For proper isolation, we'll symlink.
        # Let's just run from tmpdir and use the app's default TODO_FILE.
        yield tmpdir


def _run(cmd: list, cwd: str) -> subprocess.CompletedProcess:
    """Run todo.py with given args in the specified cwd."""
    return subprocess.run(
        [sys.executable, os.path.abspath("todo.py")] + cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
    )


def test_add_and_list(tmp_todo_dir):
    """Test adding a todo and listing it."""
    # Clean up any leftover JSON in the temp dir
    json_path = os.path.join(tmp_todo_dir, "todos.json")
    if os.path.exists(json_path):
        os.remove(json_path)

    proc = _run(["add", "Buy milk"], tmp_todo_dir)
    assert proc.returncode == 0, f"add failed: {proc.stderr}"
    new_id = int(proc.stdout.strip())

    proc = _run(["list"], tmp_todo_dir)
    assert proc.returncode == 0
    assert "Buy milk" in proc.stdout
    assert f"[{new_id}]" in proc.stdout


def test_done(tmp_todo_dir):
    """Test marking a todo done."""
    json_path = os.path.join(tmp_todo_dir, "todos.json")
    if os.path.exists(json_path):
        os.remove(json_path)

    # Add a todo
    proc = _run(["add", "Task"], tmp_todo_dir)
    assert proc.returncode == 0
    tid = int(proc.stdout.strip())

    # Mark done
    proc = _run(["done", str(tid)], tmp_todo_dir)
    assert proc.returncode == 0

    # List and check 'x' status
    proc = _run(["list"], tmp_todo_dir)
    assert proc.returncode == 0
    assert "x" in proc.stdout


def test_rm(tmp_todo_dir):
    """Test removing a todo by ID."""
    json_path = os.path.join(tmp_todo_dir, "todos.json")
    if os.path.exists(json_path):
        os.remove(json_path)

    # Add two todos
    proc = _run(["add", "First"], tmp_todo_dir)
    assert proc.returncode == 0
    id1 = int(proc.stdout.strip())

    proc = _run(["add", "Second"], tmp_todo_dir)
    assert proc.returncode == 0
    id2 = int(proc.stdout.strip())

    # Remove one
    proc = _run(["rm", str(id1)], tmp_todo_dir)
    assert proc.returncode == 0

    # List and verify only second remains
    proc = _run(["list"], tmp_todo_dir)
    assert proc.returncode == 0
    assert f"[{id2}]" in proc.stdout
    assert f"[{id1}]" not in proc.stdout


def test_missing_id_error(tmp_todo_dir):
    """Test that invalid ID prints error to stderr and exits non-zero."""
    json_path = os.path.join(tmp_todo_dir, "todos.json")
    if os.path.exists(json_path):
        os.remove(json_path)

    proc = _run(["done", "999"], tmp_todo_dir)
    assert proc.returncode != 0, f"expected non-zero exit, got {proc.returncode}"
    assert proc.stderr.strip() != "", "expected error message on stderr"