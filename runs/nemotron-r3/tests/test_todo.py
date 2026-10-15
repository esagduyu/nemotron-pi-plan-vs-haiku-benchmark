"""Pytest tests for the todo manager."""

import json
import pathlib
import sys
from io import StringIO

import pytest

# Ensure the project root is on the path so `todo.py` is importable
PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from todo import (
    add_todo,
    list_todos,
    done_todo,
    rm_todo,
    clear_completed,
)

TEST_DATA_FILE = pathlib.Path("./todos_test.json")
TEST_NEXT_ID_FILE = pathlib.Path("./.next_id_test")


def _reset_files():
    """Remove test data files so each test starts clean."""
    for f in (TEST_DATA_FILE, TEST_NEXT_ID_FILE):
        if f.exists():
            f.unlink()


def _load_todos_test():
    """Load todos from the test data file."""
    if not TEST_DATA_FILE.exists():
        return []
    with open(TEST_DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, list):
        return data
    return []


def _save_todos_test(todos):
    """Save todos to the test data file."""
    with open(TEST_DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(todos, f, indent=2)


# ---- Tests ----

class TestAdd:
    def test_add_first_todo(self):
        _reset_files()
        new_id = add_todo("Buy milk", TEST_DATA_FILE, TEST_NEXT_ID_FILE)
        assert new_id == 1
        todos = _load_todos_test()
        assert len(todos) == 1
        assert todos[0]["id"] == 1
        assert todos[0]["title"] == "Buy milk"
        assert todos[0]["done"] is False

    def test_add_second_todo_gets_new_id(self):
        _reset_files()
        add_todo("Walk the dog", TEST_DATA_FILE, TEST_NEXT_ID_FILE)
        new_id = add_todo("Read book", TEST_DATA_FILE, TEST_NEXT_ID_FILE)
        assert new_id == 2
        todos = _load_todos_test()
        assert len(todos) == 2
        assert todos[1]["id"] == 2


class TestList:
    def test_list_empty(self):
        _reset_files()
        # No todos yet - capture stdout
        captured = StringIO()
        sys.stdout = captured
        list_todos(TEST_DATA_FILE)
        sys.stdout = sys.__stdout__
        output = captured.getvalue().strip()
        assert "No todos found." in output

    def test_list_with_todos(self):
        _reset_files()
        add_todo("Buy milk", TEST_DATA_FILE, TEST_NEXT_ID_FILE)
        add_todo("Walk the dog", TEST_DATA_FILE, TEST_NEXT_ID_FILE)

        captured = StringIO()
        sys.stdout = captured
        list_todos(TEST_DATA_FILE)
        sys.stdout = sys.__stdout__
        output = captured.getvalue().strip()

        assert "[1] · Buy milk" in output
        assert "[2] · Walk the dog" in output


class TestDone:
    def test_done_marks_todo(self):
        _reset_files()
        add_todo("Buy milk", TEST_DATA_FILE, TEST_NEXT_ID_FILE)
        done_todo(1, TEST_DATA_FILE, TEST_NEXT_ID_FILE)

        todos = _load_todos_test()
        assert len(todos) == 1
        assert todos[0]["done"] is True

    def test_done_nonexistent_id(self):
        _reset_files()
        with pytest.raises(SystemExit) as exc_info:
            done_todo(999, TEST_DATA_FILE, TEST_NEXT_ID_FILE)
        assert exc_info.value.code != 0


class TestRm:
    def test_rm_removes_todo(self):
        _reset_files()
        add_todo("Buy milk", TEST_DATA_FILE, TEST_NEXT_ID_FILE)
        add_todo("Walk the dog", TEST_DATA_FILE, TEST_NEXT_ID_FILE)
        rm_todo(1, TEST_DATA_FILE, TEST_NEXT_ID_FILE)

        todos = _load_todos_test()
        assert len(todos) == 1
        assert todos[0]["id"] == 2
        assert todos[0]["title"] == "Walk the dog"

    def test_rm_nonexistent_id(self):
        _reset_files()
        with pytest.raises(SystemExit) as exc_info:
            rm_todo(999, TEST_DATA_FILE, TEST_NEXT_ID_FILE)
        assert exc_info.value.code != 0


class TestClear:
    def test_clear_removes_completed(self):
        _reset_files()
        add_todo("Buy milk", TEST_DATA_FILE, TEST_NEXT_ID_FILE)
        add_todo("Walk the dog", TEST_DATA_FILE, TEST_NEXT_ID_FILE)
        done_todo(1, TEST_DATA_FILE, TEST_NEXT_ID_FILE)

        clear_completed(TEST_DATA_FILE, TEST_NEXT_ID_FILE)

        todos = _load_todos_test()
        assert len(todos) == 1
        assert todos[0]["title"] == "Walk the dog"
        assert todos[0]["done"] is False

    def test_clear_nothing_to_remove(self):
        _reset_files()
        add_todo("Buy milk", TEST_DATA_FILE, TEST_NEXT_ID_FILE)
        add_todo("Walk the dog", TEST_DATA_FILE, TEST_NEXT_ID_FILE)

        clear_completed(TEST_DATA_FILE, TEST_NEXT_ID_FILE)

        todos = _load_todos_test()
        assert len(todos) == 2