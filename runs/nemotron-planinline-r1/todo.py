#!/usr/bin/env python3
"""Tiny CLI todo manager using argparse subcommands and JSON persistence."""

import argparse
import json
import os
import sys
from pathlib import Path

TODO_FILE = Path(os.environ.get("TODO_FILE", "todos.json"))


def _load_todos() -> list[dict]:
    """Load todos from the JSON file. Returns empty list if file doesn't exist."""
    if not TODO_FILE.exists():
        return []
    try:
        with open(TODO_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, list):
            return []
        return data
    except (json.JSONDecodeError, OSError):
        return []


def _save_todos(todos: list[dict]) -> None:
    """Save todos to the JSON file."""
    with open(TODO_FILE, "w", encoding="utf-8") as f:
        json.dump(todos, f, indent=2)


def _next_id(todos: list[dict]) -> int:
    """Calculate the next monotonically increasing ID."""
    if not todos:
        return 1
    return max(t["id"] for t in todos) + 1


def cmd_add(args: argparse.Namespace) -> None:
    """Add a new todo with the given title."""
    todos = _load_todos()
    todo = {"id": _next_id(todos), "title": args.title, "done": False}
    todos.append(todo)
    _save_todos(todos)
    print(todo["id"])


def cmd_list(todos: list[dict]) -> None:
    """Print all todos as [ID] [x|·] title."""
    if not todos:
        print("No todos.")
        return
    for t in todos:
        marker = "x" if t["done"] else "·"
        print(f"[{t['id']}] [{marker}] {t['title']}")


def cmd_done(args: argparse.Namespace) -> None:
    """Mark a todo as done by ID."""
    todos = _load_todos()
    try:
        todo_id = int(args.id)
    except (ValueError, TypeError):
        print(f"Error: ID must be an integer", file=sys.stderr)
        sys.exit(1)

    found = False
    for t in todos:
        if t["id"] == todo_id:
            t["done"] = True
            found = True
            break

    if not found:
        print(f"Error: todo with ID {todo_id} not found", file=sys.stderr)
        sys.exit(1)

    _save_todos(todos)


def cmd_rm(args: argparse.Namespace) -> None:
    """Delete a todo by ID."""
    todos = _load_todos()
    try:
        todo_id = int(args.id)
    except (ValueError, TypeError):
        print(f"Error: ID must be an integer", file=sys.stderr)
        sys.exit(1)

    found = False
    new_todos = []
    for t in todos:
        if t["id"] == todo_id:
            found = True
            # Skip this todo (delete it)
            continue
        new_todos.append(t)

    if not found:
        print(f"Error: todo with ID {todo_id} not found", file=sys.stderr)
        sys.exit(1)

    _save_todos(new_todos)


def cmd_clear(_args: argparse.Namespace) -> None:
    """Remove all done todos."""
    todos = _load_todos()
    before = len(todos)
    todos = [t for t in todos if not t["done"]]
    after = len(todos)
    if before == after:
        print("No done todos to clear.")
    _save_todos(todos)


def main() -> None:
    parser = argparse.ArgumentParser(description="Tiny CLI todo manager")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # add command
    add_parser = subparsers.add_parser("add", help="Add a new todo")
    add_parser.add_argument("title", help="Title of the todo")

    # list command
    list_parser = subparsers.add_parser("list", help="List all todos")

    # done command
    done_parser = subparsers.add_parser("done", help="Mark a todo as done")
    done_parser.add_argument("id", help="ID of the todo to mark as done")

    # rm command
    rm_parser = subparsers.add_parser("rm", help="Remove a todo by ID")
    rm_parser.add_argument("id", help="ID of the todo to remove")

    # clear command
    clear_parser = subparsers.add_parser("clear", help="Clear all done todos")

    args = parser.parse_args()

    match args.command:
        case "add":
            cmd_add(args)
        case "list":
            todos = _load_todos()
            cmd_list(todos)
        case "done":
            cmd_done(args)
        case "rm":
            cmd_rm(args)
        case "clear":
            cmd_clear(args)


if __name__ == "__main__":
    main()