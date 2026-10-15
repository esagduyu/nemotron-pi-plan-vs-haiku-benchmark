import json
import os
import tempfile
from pathlib import Path
import pytest

from todo import load_todos, save_todos, cmd_add, cmd_list, cmd_done, cmd_rm, cmd_clear


@pytest.fixture
def temp_todo_file(monkeypatch):
    """Use a temporary file for todos so tests don't pollute the cwd."""
    tmpdir = tempfile.mkdtemp()
    tmpfile = os.path.join(tmpdir, "todos.json")
    monkeypatch.setattr("todo.TODO_FILE", Path(tmpfile))
    yield tmpfile
    # cleanup handled by temp dir


def test_add(temp_todo_file):
    """Test adding a todo returns the new ID."""
    cmd_add("Buy milk")
    todos = load_todos()
    assert len(todos) == 1
    assert todos[0]["title"] == "Buy milk"
    assert todos[0]["done"] is False
    assert todos[0]["id"] == 1


def test_list(capsys, temp_todo_file):
    """Test listing todos shows correct format."""
    cmd_add("Walk the dog")
    cmd_list()
    captured = capsys.readouterr()
    output = captured.out.strip()
    assert "[1] · Walk the dog" in output


def test_done(temp_todo_file):
    """Test marking a todo as done."""
    cmd_add("Read book")
    cmd_done(1)
    todos = load_todos()
    assert todos[0]["done"] is True


def test_rm(temp_todo_file):
    """Test removing a todo."""
    cmd_add("Old task")
    cmd_rm(1)
    todos = load_todos()
    assert len(todos) == 0


def test_clear(temp_todo_file):
    """Test clearing all done todos."""
    cmd_add("Task 1")
    cmd_add("Task 2")
    # Mark first as done
    todos = load_todos()
    todos[0]["done"] = True
    save_todos(todos)
    cmd_clear()
    todos = load_todos()
    assert todos[0]["title"] == "Task 2"
    assert len(todos) == 1 and todos[0]["title"] == "Task 2"