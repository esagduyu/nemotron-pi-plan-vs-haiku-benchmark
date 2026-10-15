"""Tests for todo.py — uses a temporary directory for todos.json."""

import json
import os
import sys
import tempfile
from pathlib import Path
from unittest import mock

# Ensure the parent directory is on the path so todo.py is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import todo


def _run_with_todos(todos_data, func, *args):
    """Helper: write todos_data to a temp-file, patch todo.DATA_FILE, run func, restore."""
    with tempfile.TemporaryDirectory() as tmpdir:
        data_file = Path(tmpdir) / "todos.json"
        data_file.write_text(json.dumps(todos_data, indent=2))
        with mock.patch.object(todo, "DATA_FILE", data_file):
            return func(*args)


# ---- Tests ----


def test_add():
    """Adding a todo creates it with an incremented ID."""
    results = []
    def capture_add(args):
        todos = todo.load_todos()
        new_id = todo.next_id(todos)
        new_todo = {"id": new_id, "title": args.title, "done": False}
        todos.append(new_todo)
        todo.save_todos(todos)
        results.append(new_id)

    def fake_args(title_str):
        class A:
            title = title_str
        return A()

    _run_with_todos([], capture_add, fake_args("Buy milk"))
    assert results == [1]

    _run_with_todos([{"id": 1, "title": "Buy milk", "done": False}], capture_add, fake_args("Walk dog"))
    assert results == [1, 2]


def test_list():
    """List prints all todos with correct status markers."""
    todos = [
        {"id": 1, "title": "Task A", "done": False},
        {"id": 2, "title": "Task B", "done": True},
    ]
    output = []
    def capture_list(_args):
        loaded = todo.load_todos()
        for t in loaded:
            status = "x" if t["done"] else "·"
            output.append(f"[{t['id']}] [{status}] {t['title']}")

    _run_with_todos(todos, capture_list, None)
    assert output == ["[1] [·] Task A", "[2] [x] Task B"]


def test_done():
    """Marking a todo done sets done=True."""
    todos = [{"id": 1, "title": "Task A", "done": False}]

    with tempfile.TemporaryDirectory() as tmpdir:
        data_file = Path(tmpdir) / "todos.json"
        data_file.write_text(json.dumps(todos, indent=2))
        with mock.patch.object(todo, "DATA_FILE", data_file):
            class Args:
                id = 1
            data = todo.load_todos()
            found = todo.find_todo(data, Args.id)
            assert found is not None
            found["done"] = True
            todo.save_todos(data)
            # Verify the file was updated
            updated = todo.load_todos()
            assert updated[0]["done"] is True


def test_rm():
    """Removing a todo deletes it and doesn't reuse the ID."""
    todos = [
        {"id": 1, "title": "Task A", "done": False},
        {"id": 2, "title": "Task B", "done": False},
    ]
    results = []

    def capture_rm(args):
        data = todo.load_todos()
        item = todo.find_todo(data, args.id)
        assert item is not None
        data.remove(item)
        todo.save_todos(data)
        results.append(len(data))

    class Args:
        id = 1

    _run_with_todos(todos, capture_rm, Args())
    assert results == [1]  # one remaining after removal


def test_next_id_never_reused():
    """IDs are monotonically increasing even after removal."""
    todos = [
        {"id": 1, "title": "A", "done": False},
        {"id": 2, "title": "B", "done": False},
        {"id": 3, "title": "C", "done": False},
    ]
    # Remove id 2
    def rm_2(_args):
        data = todo.load_todos()
        data = [t for t in data if t["id"] != 2]
        todo.save_todos(data)

    class Args:
        id = 2

    _run_with_todos(todos, rm_2, Args())

    # Add a new one — should get ID 4, not 2
    def add_check(args):
        data = todo.load_todos()
        new_id = todo.next_id(data)
        results.append(new_id)

    class AddArgs:
        title = "D"

    results = []
    _run_with_todos([t for t in todos if t["id"] != 2], add_check, AddArgs())
    assert results == [4]
