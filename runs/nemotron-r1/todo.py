#!/usr/bin/env python3
"""Tiny CLI todo manager using only stdlib (plus pytest for tests)."""

import argparse
import json
import sys
from pathlib import Path
from typing import List, Dict, Any

DATA_FILE = Path("./todos.json")
NEXT_ID = 1  # module-level counter for monotonically increasing IDs


def _load_todos() -> List[Dict[str, Any]]:
    """Load todos from the JSON file. Returns empty list if file missing/empty."""
    if not DATA_FILE.exists():
        return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, list):
            return []
        return data
    except (json.JSONDecodeError, OSError):
        return []


def _save_todos(todos: List[Dict[str, Any]]) -> None:
    """Save todos to the JSON file."""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(todos, f, indent=2)


def _generate_id() -> int:
    """Return the next monotonically increasing ID and increment the counter."""
    global NEXT_ID
    id_val = NEXT_ID
    NEXT_ID += 1
    return id_val


def cmd_add(title: str) -> None:
    """Add a new todo with the given title. Prints the new ID."""
    global NEXT_ID
    todo_id = _generate_id()
    todos = _load_todos()
    todos.append({"id": todo_id, "title": title, "done": False})
    _save_todos(todos)
    print(todo_id)


def cmd_list() -> None:
    """Print all todos as [ID] [x|·] title."""
    todos = _load_todos()
    if not todos:
        print("(no todos)")
        return
    for todo in todos:
        status = "x" if todo["done"] else "·"
        print(f"[{todo['id']}] {status} {todo['title']}")


def cmd_done(todo_id: int) -> None:
    """Mark a todo done by ID. Prints success or error."""
    todos = _load_todos()
    found = False
    for todo in todos:
        if todo["id"] == todo_id:
            found = True
            todo["done"] = True
            break
    if not found:
        print(f"Error: todo with ID {todo_id} not found", file=sys.stderr)
        sys.exit(1)
    _save_todos(todos)


def cmd_rm(todo_id: int) -> None:
    """Delete a todo by ID. Prints error if not found."""
    todos = _load_todos()
    found = False
    new_todos = []
    for todo in todos:
        if todo["id"] == todo_id:
            found = True
            # skip this todo (delete it)
            continue
        new_todos.append(todo)
    if not found:
        print(f"Error: todo with ID {todo_id} not found", file=sys.stderr)
        sys.exit(1)
    _save_todos(new_todos)


def cmd_clear() -> None:
    """Remove all done todos."""
    todos = _load_todos()
    before = len(todos)
    new_todos = [t for t in todos if not t["done"]]
    removed = before - len(new_todos)
    if removed > 0:
        _save_todos(new_todos)
        print(f"Removed {removed} done todo(s)")
    else:
        print("No done todos to remove")


def main() -> None:
    parser = argparse.ArgumentParser(description="Tiny CLI todo manager")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # add
    add_parser = subparsers.add_parser("add", help="Add a new todo")
    add_parser.add_argument("title", help="Title of the todo")

    # done
    done_parser = subparsers.add_parser("done", help="Mark a todo done")
    done_parser.add_argument("id", type=int, help="Todo ID")

    # rm
    rm_parser = subparsers.add_parser("rm", help="Delete a todo")
    rm_parser.add_argument("id", type=int, help="Todo ID")

    # list (no args)
    list_parser = subparsers.add_parser("list", help="List all todos")

    # clear (no args)
    clear_parser = subparsers.add_parser("clear", help="Clear all done todos")

    args = parser.parse_args()

    if args.command == "add":
        cmd_add(args.title)
    elif args.command == "done":
        cmd_done(args.id)
    elif args.command == "rm":
        cmd_rm(args.id)
    elif args.command == "list":
        cmd_list()
    elif args.command == "clear":
        cmd_clear()


if __name__ == "__main__":
    main()