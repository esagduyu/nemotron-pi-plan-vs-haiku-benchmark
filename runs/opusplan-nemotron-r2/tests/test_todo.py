"""Pytest tests for the todo CLI manager."""

import os
import subprocess
import sys

import pytest

from todo import add_todo, clear_done, format_todo, load, mark_done, remove_todo, save, TodoError


# ---------------------------------------------------------------------------
# Helper: run the CLI
# ---------------------------------------------------------------------------

def _run_cli(args: list, tmp_path) -> subprocess.CompletedProcess:
    """Run todo.py with the given args, redirecting TODO_FILE to tmp_dir."""
    env = dict(os.environ)
    env["TODO_FILE"] = str(tmp_path / "todos.json")
    result = subprocess.run(
        [sys.executable, "todo.py"] + args,
        capture_output=True,
        text=True,
        env=env,
    )
    return result


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_add_print_sequential_ids(tmp_path, monkeypatch):
    """add prints the new ID and persists the todo."""
    p = tmp_path / "todos.json"
    monkeypatch.setenv("TODO_FILE", str(p))

    result = _run_cli(["add", "Buy milk"], tmp_path)
    assert result.returncode == 0
    assert result.stdout.strip().isdigit()
    new_id = int(result.stdout.strip())

    # Check persistence
    data = load()
    assert len(data["todos"]) == 1
    assert data["todos"][0]["title"] == "Buy milk"
    assert data["todos"][0]["done"] is False
    assert data["todos"][0]["id"] == new_id


def test_list_output_format(tmp_path, monkeypatch):
    """Test list output format for open and done todos."""
    p = tmp_path / "todos.json"
    monkeypatch.setenv("TODO_FILE", str(p))

    # Add two open todos
    _run_cli(["add", "Walk the dog"], tmp_path)
    _run_cli(["add", "Read book"], tmp_path)

    # Mark first as done via CLI
    _run_cli(["done", "1"], tmp_path)

    result = _run_cli(["list"], tmp_path)
    assert result.returncode == 0
    lines = result.stdout.strip().splitlines()
    assert len(lines) == 2
    # First should be done (x), second open (·)
    assert "[1] [x] Walk the dog" in lines[0]
    assert "[2] [·] Read book" in lines[1]


def test_done_marks_todo(tmp_path, monkeypatch):
    """Test done marks the todo; done on missing ID exits non-zero."""
    p = tmp_path / "todos.json"
    monkeypatch.setenv("TODO_FILE", str(p))

    # Add a todo
    _run_cli(["add", "Task"], tmp_path)

    # Mark it done
    result = _run_cli(["done", "1"], tmp_path)
    assert result.returncode == 0

    # Verify via list
    result = _run_cli(["list"], tmp_path)
    assert "[1] [x] Task" in result.stdout

    # done on missing ID
    result = _run_cli(["done", "999"], tmp_path)
    assert result.returncode != 0
    assert "error:" in result.stderr


def test_rm_deletes_todo(tmp_path, monkeypatch):
    """Test rm deletes the todo; rm on missing ID exits non-zero."""
    p = tmp_path / "todos.json"
    monkeypatch.setenv("TODO_FILE", str(p))

    # Add a todo
    _run_cli(["add", "To remove"], tmp_path)

    # Remove it
    result = _run_cli(["rm", "1"], tmp_path)
    assert result.returncode == 0

    # Verify gone
    result = _run_cli(["list"], tmp_path)
    assert result.stdout.strip() == ""

    # rm on missing ID
    result = _run_cli(["rm", "999"], tmp_path)
    assert result.returncode != 0
    assert "error:" in result.stderr


def test_ids_not_reused_after_rm(tmp_path, monkeypatch):
    """Test IDs are not reused after rm."""
    p = tmp_path / "todos.json"
    monkeypatch.setenv("TODO_FILE", str(p))

    # Add three todos
    r1 = _run_cli(["add", "First"], tmp_path)
    r2 = _run_cli(["add", "Second"], tmp_path)
    r3 = _run_cli(["add", "Third"], tmp_path)

    id1 = int(r1.stdout.strip())
    id2 = int(r2.stdout.strip())
    id3 = int(r3.stdout.strip())

    # Remove the middle one
    _run_cli(["rm", str(id2)], tmp_path)

    # Add another — should get a new ID higher than id3
    r4 = _run_cli(["add", "Fourth"], tmp_path)
    id4 = int(r4.stdout.strip())
    assert id4 > id3


def test_clear_removes_only_done(tmp_path, monkeypatch):
    """Test clear removes only done todos."""
    p = tmp_path / "todos.json"
    monkeypatch.setenv("TODO_FILE", str(p))

    # Add open and done todos
    _run_cli(["add", "Open task"], tmp_path)
    _run_cli(["add", "Done task"], tmp_path)
    # Mark the second as done via CLI
    _run_cli(["done", "2"], tmp_path)

    # Clear done
    result = _run_cli(["clear"], tmp_path)
    assert result.returncode == 0
    assert "1" in result.stdout  # one done todo removed

    # Verify only open todo remains
    result = _run_cli(["list"], tmp_path)
    assert "[1] [·] Open task" in result.stdout


def test_corrupt_json_gives_clean_error(tmp_path, monkeypatch):
    """Test a corrupt todos.json gives a clean error, not a traceback."""
    import tempfile
    import json

    # Test 1: load() raises TodoError (not a raw JSONDecodeError) for corrupt file
    p = os.path.join(tmp_path, "corrupt_todos.json")
    with open(p, "w") as f:
        f.write("not valid json {{{")

    # load() should raise TodoError, not let JSONDecodeError propagate
    with pytest.raises(TodoError):
        load(path=p)

    # Test 2: CLI also handles it gracefully
    # Write corrupt JSON to the TODO_FILE location
    q = os.path.join(tmp_path, "todos.json")
    with open(q, "w") as f:
        f.write("not valid json {{{")

    monkeypatch.setenv("TODO_FILE", str(q))

    result = _run_cli(["list"], tmp_path)
    assert result.returncode != 0
    assert "error:" in result.stderr
    # No traceback should be in stderr
    assert "Traceback" not in result.stderr


def test_load_missing_file_returns_empty(tmp_path):
    """load() returns empty store when file is missing."""
    # Use a path that doesn't exist
    p = os.path.join(tmp_path, "nonexistent.json")
    data = load(path=p)
    assert data == {"next_id": 1, "todos": []}


def test_load_invalid_structure_raises(tmp_path):
    """load() raises TodoError for wrong structure."""
    # Write invalid structure
    p = os.path.join(tmp_path, "invalid.json")
    with open(p, "w") as f:
        f.write('{"not_right": true}')

    with pytest.raises(TodoError):
        load(path=p)
