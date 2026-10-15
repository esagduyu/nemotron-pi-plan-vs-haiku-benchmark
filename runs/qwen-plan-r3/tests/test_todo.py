"""Tests for the tiny CLI todo manager."""

import json
import os
import shutil
import subprocess
import sys
import tempfile


def run_todo(args, cwd):
    """Run todo.py with the given args in the specified directory."""
    result = subprocess.run(
        [sys.executable, "todo.py"] + args,
        capture_output=True,
        text=True,
        cwd=cwd,
    )
    return result


def test_add():
    """Test adding a todo."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Copy todo.py into the temp dir
        shutil.copy2(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "todo.py"),
                      os.path.join(tmpdir, "todo.py"))

        result = run_todo(["add", "Buy milk"], tmpdir)
        assert result.returncode == 0
        assert "Added todo 1: Buy milk" in result.stdout

        # Verify JSON file
        with open(os.path.join(tmpdir, "todos.json")) as f:
            todos = json.load(f)
        assert len(todos) == 1
        assert todos[0]["id"] == 1
        assert todos[0]["title"] == "Buy milk"
        assert todos[0]["done"] is False


def test_list():
    """Test listing todos."""
    with tempfile.TemporaryDirectory() as tmpdir:
        shutil.copy2(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "todo.py"),
                      os.path.join(tmpdir, "todo.py"))

        # Add two todos
        run_todo(["add", "Task one"], tmpdir)
        run_todo(["add", "Task two"], tmpdir)

        result = run_todo(["list"], tmpdir)
        assert result.returncode == 0
        assert "[1] [·] Task one" in result.stdout
        assert "[2] [·] Task two" in result.stdout


def test_done():
    """Test marking a todo as done."""
    with tempfile.TemporaryDirectory() as tmpdir:
        shutil.copy2(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "todo.py"),
                      os.path.join(tmpdir, "todo.py"))

        run_todo(["add", "Some task"], tmpdir)
        run_todo(["done", "1"], tmpdir)

        # Verify via list
        result = run_todo(["list"], tmpdir)
        assert result.returncode == 0
        assert "[1] [x] Some task" in result.stdout

        # Verify invalid ID
        result = run_todo(["done", "999"], tmpdir)
        assert result.returncode != 0
        assert "no todo with ID 999" in result.stderr


def test_rm():
    """Test removing a todo."""
    with tempfile.TemporaryDirectory() as tmpdir:
        shutil.copy2(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "todo.py"),
                      os.path.join(tmpdir, "todo.py"))

        run_todo(["add", "To delete"], tmpdir)
        run_todo(["add", "Keep this"], tmpdir)

        result = run_todo(["rm", "1"], tmpdir)
        assert result.returncode == 0
        assert "Removed todo 1." in result.stdout

        # Verify only one remains
        result = run_todo(["list"], tmpdir)
        assert "[1] [·] To delete" not in result.stdout
        assert "[2] [·] Keep this" in result.stdout

        # Verify ID 3 is next (never reused)
        run_todo(["add", "New one"], tmpdir)
        result = run_todo(["list"], tmpdir)
        assert "[3] [·] New one" in result.stdout

        # Verify invalid ID
        result = run_todo(["rm", "999"], tmpdir)
        assert result.returncode != 0
        assert "no todo with ID 999" in result.stderr
