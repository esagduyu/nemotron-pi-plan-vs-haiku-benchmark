import pytest
import json
import tempfile
from pathlib import Path

from todo import cmd_add, cmd_list, cmd_done, cmd_rm, cmd_clear


@pytest.fixture
def data_file():
    """Create a temp directory and return the todos.json path within it."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir) / "todos.json"


@pytest.fixture(autouse=True)
def patch_data_file(data_file, monkeypatch, tmp_path):
    """Patch module-level DATA_FILE to the temp file for each test."""
    import todo
    orig = todo.DATA_FILE
    todo.DATA_FILE = data_file
    # Reset ID counter
    todo.NEXT_ID = 1
    yield
    todo.DATA_FILE = orig
    todo.NEXT_ID = 1


def test_add(data_file):
    """Adding a todo should print the new ID and store it."""
    cmd_add("Buy milk")
    with open(data_file, "r") as f:
        todos = json.load(f)
    assert len(todos) == 1
    assert todos[0]["title"] == "Buy milk"
    assert todos[0]["done"] is False
    assert todos[0]["id"] == 1


def test_list(data_file, capsys):
    """Listing todos should show [ID] [x|·] title format."""
    cmd_add("Walk the dog")
    cmd_add("Read book")
    cmd_list()
    captured = capsys.readouterr()
    output = captured.out.strip()
    assert "[1] · Walk the dog" in output
    assert "[2] · Read book" in output


def test_done(data_file):
    """Marking a todo done should set done=True."""
    cmd_add("Task A")
    cmd_add("Task B")
    cmd_done(1)
    with open(data_file, "r") as f:
        todos = json.load(f)
    assert todos[0]["done"] is True
    assert todos[1]["done"] is False


def test_rm(data_file):
    """Removing a todo should delete it and not reuse IDs."""
    cmd_add("First")
    cmd_add("Second")
    cmd_rm(1)
    with open(data_file, "r") as f:
        todos = json.load(f)
    assert len(todos) == 1
    assert todos[0]["title"] == "Second"
    assert todos[0]["id"] == 2  # ID should not be reused


def test_rm_invalid_id():
    """rm with invalid ID should print error to stderr and exit non-zero."""
    import todo
    # Temporarily set DATA_FILE to a real file so cmd_rm can read
    orig = todo.DATA_FILE
    real_file = todo.Path("./todos.json")
    todo.DATA_FILE = real_file
    # Ensure file exists with at least one todo
    cmd_add("test")
    try:
        cmd_rm(999)
        assert False, "Should have exited with code 1"
    except SystemExit as e:
        assert e.code == 1
    finally:
        todo.DATA_FILE = orig