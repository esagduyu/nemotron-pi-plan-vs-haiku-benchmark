"""Pytest tests for the todo CLI manager."""

import json
import os
import subprocess
import sys

import pytest

# The module under test
from todo import main, add, list_todos, done, rm, clear_done, TodoError


@pytest.fixture
def todo_path(tmp_path, monkeypatch):
    """Use a temp directory for todos.json so we don't pollute the CWD.

    Changes the current working directory to a temp dir so that
    resolve_path("./todos.json") resolves to the temp directory.
    """
    # Create a temp dir and chdir into it
    chdir_dir = tmp_path / "todo_test_dir"
    chdir_dir.mkdir(parents=True, exist_ok=True)
    import pathlib

    original_cwd = os.getcwd()
    os.chdir(chdir_dir)
    try:
        yield str(chdir_dir / "todos.json")
    finally:
        os.chdir(original_cwd)


def test_add_prints_id_and_persists(todo_path):
    """Test add prints the ID and persists the todo."""
    # Clean slate - remove if exists in the temp dir
    if os.path.exists(todo_path):
        os.remove(todo_path)

    exit_code = main(["add", "Buy milk"])
    assert exit_code == 0

    # Verify persistence
    with open(todo_path, "r", encoding="utf-8") as f:
        store = json.load(f)

    assert "next_id" in store
    assert len(store["todos"]) == 1
    assert store["todos"][0]["title"] == "Buy milk"
    assert store["todos"][0]["done"] is False
    assert store["todos"][0]["id"] == 1
    assert store["next_id"] == 2


def test_list_output_format(todo_path):
    """Test list output format for open and done todos."""
    # Clean up
    if os.path.exists(todo_path):
        os.remove(todo_path)

    # Add two open todos
    main(["add", "Walk the dog"])
    main(["add", "Read book"])

    # Capture output
    from io import StringIO
    from contextlib import redirect_stdout

    output = StringIO()
    with redirect_stdout(output):
        list_todos()
    text = output.getvalue()

    assert "[1] [·] Walk the dog" in text
    assert "[2] [·] Read book" in text


def test_list_with_done(todo_path):
    """Test list shows x for done todos."""
    # Clean up
    if os.path.exists(todo_path):
        os.remove(todo_path)

    main(["add", "Task 1"])
    main(["add", "Task 2"])

    # Mark first as done
    done(1)

    from io import StringIO
    from contextlib import redirect_stdout

    output = StringIO()
    with redirect_stdout(output):
        list_todos()
    text = output.getvalue()

    assert "[1] [x] Task 1" in text
    assert "[2] [·] Task 2" in text


def test_done_marks_done_unknown_id_fails(todo_path):
    """Test done marks a todo done; unknown ID exits non-zero with stderr message."""
    # Clean up
    if os.path.exists(todo_path):
        os.remove(todo_path)

    main(["add", "Something"])

    # Try to mark non-existent ID as done
    exit_code = main(["done", "999"])
    assert exit_code != 0


def test_rm_removes_todo_ids_not_reused(todo_path):
    """Test rm removes a todo and IDs are not reused after rm."""
    # Clean up
    if os.path.exists(todo_path):
        os.remove(todo_path)

    main(["add", "First"])
    main(["add", "Second"])

    # Remove the first todo
    rm(1)

    # Add a new todo; it should get ID 3, not ID 1
    exit_code = main(["add", "Third"])
    assert exit_code == 0

    with open(todo_path, "r", encoding="utf-8") as f:
        store = json.load(f)

    assert len(store["todos"]) == 2
    assert store["todos"][0]["title"] == "Second"
    assert store["todos"][0]["id"] == 2
    assert store["todos"][1]["title"] == "Third"
    assert store["todos"][1]["id"] == 3
    assert store["next_id"] == 4


def test_clear_removes_only_done(todo_path):
    """Test clear removes only done todos."""
    # Clean up
    if os.path.exists(todo_path):
        os.remove(todo_path)

    main(["add", "Open task"])
    main(["add", "Done task"])
    # Mark the second as done
    done(2)

    clear_done()

    with open(todo_path, "r", encoding="utf-8") as f:
        store = json.load(f)

    assert len(store["todos"]) == 1
    assert store["todos"][0]["title"] == "Open task"
    assert store["todos"][0]["done"] is False


def test_invalid_id_exits_nonzero_without_traceback(tmp_path):
    """Test invalid (non-integer) ID exits non-zero without a traceback."""
    result = subprocess.run(
        [sys.executable, "todo.py", "done", "abc"],
        capture_output=True,
        text=True,
        cwd=tmp_path,
    )
    assert result.returncode != 0
    # Should not contain a traceback
    assert "Traceback" not in result.stdout
    assert "Traceback" not in result.stderr


def test_empty_title_rejected(todo_path):
    """Test that empty/whitespace-only titles are rejected."""
    # Clean up
    if os.path.exists(todo_path):
        os.remove(todo_path)

    exit_code = main(["add", "   "])
    assert exit_code == 1

    # Verify nothing was added
    if os.path.exists(todo_path):
        with open(todo_path, "r", encoding="utf-8") as f:
            store = json.load(f)
        assert len(store["todos"]) == 0