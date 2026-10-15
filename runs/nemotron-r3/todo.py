#!/usr/bin/env python3
"""Tiny CLI todo manager using only stdlib (plus pytest for tests)."""

import argparse
import json
import sys
from pathlib import Path
from typing import List, Dict, Any

DEFAULT_DATA_FILE = Path("./todos.json")
DEFAULT_NEXT_ID_FILE = Path("./.next_id")


def _load_todos(data_file: Path) -> List[Dict[str, Any]]:
    """Load todos from the JSON file. Returns empty list if file doesn't exist."""
    if not data_file.exists():
        return []
    try:
        with open(data_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            return data
        return []
    except (json.JSONDecodeError, OSError):
        return []


def _save_todos(todos: List[Dict[str, Any]], data_file: Path) -> None:
    """Save todos to the JSON file."""
    with open(data_file, "w", encoding="utf-8") as f:
        json.dump(todos, f, indent=2)


def _get_next_id(next_id_file: Path) -> int:
    """Get the next available ID. Creates .next_id if it doesn't exist."""
    if not next_id_file.exists():
        with open(next_id_file, "w", encoding="utf-8") as f:
            f.write("1")
        return 1
    with open(next_id_file, "r", encoding="utf-8") as f:
        content = f.read().strip()
        if content == "":
            return 1
        return int(content)


def _set_next_id(next_id_file: Path, nid: int) -> None:
    """Set the next ID value."""
    with open(next_id_file, "w", encoding="utf-8") as f:
        f.write(str(nid))


def _generate_id(next_id_file: Path) -> int:
    """Generate a new monotonically increasing ID."""
    current = _get_next_id(next_id_file)
    _set_next_id(next_id_file, current + 1)
    return current


def add_todo(title: str, data_file: Path = None, next_id_file: Path = None) -> int:
    """Add a new todo and return its ID."""
    if not title.strip():
        print("Error: todo title cannot be empty", file=sys.stderr)
        sys.exit(1)

    if data_file is None:
        data_file = DEFAULT_DATA_FILE
    if next_id_file is None:
        next_id_file = DEFAULT_NEXT_ID_FILE

    todos = _load_todos(data_file)
    new_id = _generate_id(next_id_file)
    todos.append({"id": new_id, "title": title, "done": False})
    _save_todos(todos, data_file)
    return new_id


def list_todos(data_file: Path = None) -> None:
    """Print all todos."""
    if data_file is None:
        data_file = DEFAULT_DATA_FILE
    todos = _load_todos(data_file)
    if not todos:
        print("No todos found.")
        return

    for todo in todos:
        status = "x" if todo["done"] else "·"
        print(f"[{todo['id']}] {status} {todo['title']}")


def done_todo(todo_id: int, data_file: Path = None, next_id_file: Path = None) -> None:
    """Mark a todo as done by ID."""
    if data_file is None:
        data_file = DEFAULT_DATA_FILE
    if next_id_file is None:
        next_id_file = DEFAULT_NEXT_ID_FILE

    todos = _load_todos(data_file)

    found = False
    for todo in todos:
        if todo["id"] == todo_id:
            found = True
            todo["done"] = True
            break

    if not found:
        print(f"Error: todo with ID {todo_id} not found", file=sys.stderr)
        sys.exit(1)

    _save_todos(todos, data_file)


def rm_todo(todo_id: int, data_file: Path = None, next_id_file: Path = None) -> None:
    """Delete a todo by ID."""
    if data_file is None:
        data_file = DEFAULT_DATA_FILE
    if next_id_file is None:
        next_id_file = DEFAULT_NEXT_ID_FILE

    todos = _load_todos(data_file)

    found = False
    new_todos = []
    for todo in todos:
        if todo["id"] == todo_id:
            found = True
            # Skip this todo (delete it)
            continue
        new_todos.append(todo)

    if not found:
        print(f"Error: todo with ID {todo_id} not found", file=sys.stderr)
        sys.exit(1)

    _save_todos(new_todos, data_file)


def clear_completed(data_file: Path = None, next_id_file: Path = None) -> None:
    """Remove all done todos."""
    if data_file is None:
        data_file = DEFAULT_DATA_FILE
    if next_id_file is None:
        next_id_file = DEFAULT_NEXT_ID_FILE
    todos = _load_todos(data_file)
    before = len(todos)
    todos = [t for t in todos if not t["done"]]
    after = len(todos)
    removed = before - after

    if removed > 0:
        _save_todos(todos, data_file)
        print(f"Removed {removed} completed todo(s).")
    else:
        print("No completed todos to remove.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Tiny CLI todo manager")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # add command
    add_parser = subparsers.add_parser("add", help="Add a new todo")
    add_parser.add_argument("title", help="Title of the todo")

    # done command
    done_parser = subparsers.add_parser("done", help="Mark a todo as done")
    done_parser.add_argument("id", type=int, help="Todo ID")

    # rm command
    rm_parser = subparsers.add_parser("rm", help="Delete a todo")
    rm_parser.add_argument("id", type=int, help="Todo ID")

    # list command (no args)
    list_parser = subparsers.add_parser("list", help="List all todos")

    # clear command
    clear_parser = subparsers.add_parser("clear", help="Remove all done todos")

    args = parser.parse_args()

    if args.command == "add":
        new_id = add_todo(args.title)
        print(new_id)
    elif args.command == "list":
        list_todos()
    elif args.command == "done":
        done_todo(args.id)
    elif args.command == "rm":
        rm_todo(args.id)
    elif args.command == "clear":
        clear_completed()
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()