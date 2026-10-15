#!/usr/bin/env python3
"""Tiny CLI todo manager using Python stdlib only."""

import argparse
import json
import os
import sys
from typing import List, Dict, Any

TODO_FILE = "todos.json"
_next_id = 0


def _init_next_id():
    """Initialize _next_id based on existing todo file."""
    global _next_id
    if os.path.exists(TODO_FILE):
        try:
            with open(TODO_FILE, "r") as f:
                data = json.load(f)
                if data:
                    _next_id = max(t["id"] for t in data) + 1
                else:
                    _next_id = 1
        except (json.JSONDecodeError, OSError):
            _next_id = 1
    else:
        _next_id = 0


def _load_todos() -> List[Dict[str, Any]]:
    """Load todos from JSON file, creating empty list if file doesn't exist."""
    global _next_id
    if not os.path.exists(TODO_FILE):
        return []
    try:
        with open(TODO_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return []


def _save_todos(todos: List[Dict[str, Any]]) -> None:
    """Save todos to JSON file."""
    with open(TODO_FILE, "w") as f:
        json.dump(todos, f, indent=2)


def _generate_id() -> int:
    """Generate the next monotonically increasing ID."""
    global _next_id
    _next_id += 1
    return _next_id


def add(title: str) -> int:
    """Add a new todo and return its ID."""
    global _next_id
    todos = _load_todos()
    todo_id = _generate_id()
    todos.append({"id": todo_id, "title": title, "done": False})
    _save_todos(todos)
    print(todo_id)
    return todo_id


def list_todos() -> None:
    """Print all todos as [ID] [x|·] title."""
    todos = _load_todos()
    if not todos:
        print("No todos.")
        return
    for todo in todos:
        status = "x" if todo["done"] else "·"
        print(f"[{todo['id']}] {status} {todo['title']}")


def done(todo_id: int) -> None:
    """Mark a todo done by ID."""
    todos = _load_todos()
    found = False
    for todo in todos:
        if todo["id"] == todo_id:
            todo["done"] = True
            found = True
            break
    if not found:
        print(f"Error: todo with ID {todo_id} not found", file=sys.stderr)
        sys.exit(1)
    _save_todos(todos)


def rm(todo_id: int) -> None:
    """Delete a todo by ID."""
    todos = _load_todos()
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
    _save_todos(new_todos)


def clear_done() -> None:
    """Remove all done todos."""
    todos = _load_todos()
    before = len(todos)
    new_todos = [t for t in todos if not t["done"]]
    removed = before - len(new_todos)
    if removed > 0:
        _save_todos(new_todos)
        print(f"Removed {removed} done todo(s).")
    else:
        print("No done todos to remove.")


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Tiny CLI todo manager")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # add command
    add_parser = subparsers.add_parser("add", help="Add a new todo")
    add_parser.add_argument("title", help="Title of the todo")

    # list command
    subparsers.add_parser("list", help="List all todos")

    # done command
    done_parser = subparsers.add_parser("done", help="Mark a todo done")
    done_parser.add_argument("id", type=int, help="Todo ID")

    # rm command
    rm_parser = subparsers.add_parser("rm", help="Remove a todo")
    rm_parser.add_argument("id", type=int, help="Todo ID")

    # clear command
    subparsers.add_parser("clear", help="Remove all done todos")

    args = parser.parse_args()

    if args.command == "add":
        add(args.title)
    elif args.command == "list":
        list_todos()
    elif args.command == "done":
        done(args.id)
    elif args.command == "rm":
        rm(args.id)
    elif args.command == "clear":
        clear_done()
    else:
        parser.print_help()


# Initialize _next_id when module is imported (not when run directly)
_init_next_id()

if __name__ == "__main__":
    main()