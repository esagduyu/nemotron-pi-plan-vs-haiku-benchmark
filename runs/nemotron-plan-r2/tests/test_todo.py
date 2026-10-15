"""Pytest tests for the todo manager."""

import json
import os
import sys
import tempfile
from pathlib import Path

# Ensure todo.py can be imported
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pytest
import todo


@pytest.fixture
def temp_todo_file():
    """Create a temporary directory and set TODO_FILE for each test."""
    with tempfile.TemporaryDirectory() as tmpdir:
        todo_path = os.path.join(tmpdir, "todos.json")
        # Monkeypatch the TODO_FILE path for each test
        todo.TODO_FILE = Path(todo_path)
        yield tmpdir
        # Restore original path
        todo.TODO_FILE = Path("todos.json")


def test_add_and_list(temp_todo_file, capsys):
    """Test adding a todo and listing it."""
    # Ensure clean state
    if Path("todos.json").exists():
        Path("todos.json").unlink()

    todo.add_todo("Buy milk")

    # List todos
    todo.list_todos()
    captured = capsys.readouterr()
    # The list output should contain "Buy milk"
    assert "Buy milk" in captured.out


def test_id_is_printed_on_add(temp_todo_file, capsys):
    """Test that add prints the new ID."""
    if Path("todos.json").exists():
        Path("todos.json").unlink()

    todo.add_todo("Learn Python")

    captured = capsys.readouterr()
    # The output should be just the ID (1 on first add)
    assert captured.out.strip() == "1"


def test_mark_done(temp_todo_file, capsys):
    """Test marking a todo as done."""
    if Path("todos.json").exists():
        Path("todos.json").unlink()

    todo.add_todo("Read book")
    todo.done_todo(1)

    # List should show 'x' for done
    todo.list_todos()
    captured = capsys.readouterr()
    # After marking done, the output should have 'x' and the title
    assert "x" in captured.out
    assert "Read book" in captured.out


def test_rm(temp_todo_file, capsys):
    """Test removing a todo."""
    if Path("todos.json").exists():
        Path("todos.json").unlink()

    todo.add_todo("Delete me")
    todo.rm_todo(1)

    # List should not show the removed todo
    todo.list_todos()
    captured = capsys.readouterr()
    assert "Delete me" not in captured.out


def test_clear_removes_done():
    """Test that clear removes all done todos."""
    if Path("todos.json").exists():
        Path("todos.json").unlink()

    todo.add_todo("Task 1")
    todo.add_todo("Task 2")

    # Mark first as done by directly editing the JSON file
    todo_path = Path("todos.json")
    with open(todo_path, "r") as f:
        todos = json.load(f)
    todos[0]["done"] = True
    with open(todo_path, "w") as f:
        json.dump(todos, f)

    todo.clear_todos()

    # Verify only undone todo remains
    remaining = todo.load_todos()
    assert len(remaining) == 1
    assert remaining[0]["title"] == "Task 2"
    assert remaining[0]["done"] is False