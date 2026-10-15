"""Pytest tests for the todo manager."""

import json
import os
import pathlib
import sys

# Add parent directory to path so we can import todo.py
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))
from todo import add, done, rm, list_todos, clear_done

TODO_FILE = "tests/todos_test.json"


def _setup_temp_dir():
    """Ensure we work in a temp directory for test isolation."""
    test_dir = pathlib.Path("tests")
    test_dir.mkdir(exist_ok=True)
    return test_dir


def _load_todos_file():
    """Load the current todos.json content."""
    if os.path.exists(TODO_FILE):
        with open(TODO_FILE, "r") as f:
            return json.load(f)
    return []


def _save_todos_file(todos):
    """Save todos to the JSON file."""
    with open(TODO_FILE, "w") as f:
        json.dump(todos, f, indent=2)


def _reset_todo_file():
    """Reset the todo file to empty state."""
    _save_todos_file([])


# Override the TODO_FILE for tests
import todo
todo.TODO_FILE = TODO_FILE

todo._next_id = 0


def _reset_test_state():
    """Reset both the todo file and the ID counter."""
    try:
        os.remove(TODO_FILE)
    except FileNotFoundError:
        pass
    todo._next_id = 0


def test_add():
    """Test adding a new todo prints ID and stores it."""
    _reset_test_state()
    result = add("Buy milk")
    assert result == 1

    todos = _load_todos_file()
    assert len(todos) == 1
    assert todos[0]["title"] == "Buy milk"
    assert todos[0]["done"] is False


def test_list():
    """Test listing todos shows correct format."""
    _reset_test_state()

    # Add a todo first
    add("Walk the dog")

    # Capture output
    import io
    from contextlib import redirect_stdout

    f = io.StringIO()
    with redirect_stdout(f):
        list_todos()
    output = f.getvalue().strip()

    assert "[1] · Walk the dog" in output


def test_done():
    """Test marking a todo done."""
    _reset_test_state()

    add("Read book")
    done(1)

    todos = _load_todos_file()
    assert len(todos) == 1
    assert todos[0]["done"] is True


def test_rm():
    """Test removing a todo."""
    _reset_test_state()

    add("Task A")
    add("Task B")
    rm(1)

    todos = _load_todos_file()
    assert len(todos) == 1
    assert todos[0]["title"] == "Task B"
    # ID should not be reused
    assert todos[0]["id"] == 2


def test_clear():
    """Test clearing done todos."""
    _reset_test_state()

    add("Task 1")
    add("Task 2")
    done(1)

    clear_done()

    todos = _load_todos_file()
    assert len(todos) == 1
    assert todos[0]["title"] == "Task 2"
    assert todos[0]["done"] is False