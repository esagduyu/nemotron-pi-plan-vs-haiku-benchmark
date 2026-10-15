#!/usr/bin/env python3
"""Tiny CLI todo manager using only stdlib (plus pytest for tests)."""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import List, Dict, Any

TODO_FILE = Path("todos.json")


def load_todos() -> List[Dict[str, Any]]:
    """Load todos from the JSON persistence file. Creates file if missing."""
    if not TODO_FILE.exists():
        TODO_FILE.write_text("[]")
        return []
    try:
        data = TODO_FILE.read_text()
        return json.loads(data)
    except (json.JSONDecodeError, OSError) as e:
        print(f"Error reading {TODO_FILE}: {e}", file=sys.stderr)
        sys.exit(1)


def save_todos(todos: List[Dict[str, Any]]) -> None:
    """Save todos to the JSON persistence file."""
    try:
        TODO_FILE.write_text(json.dumps(todos, indent=2))
    except OSError as e:
        print(f"Error writing {TODO_FILE}: {e}", file=sys.stderr)
        sys.exit(1)


def next_id(todos: List[Dict[str, Any]]) -> int:
    """Return the next monotonically increasing ID."""
    if not todos:
        return 1
    return max(t["id"] for t in todos) + 1


def find_todo(todos: List[Dict[str, Any]], todo_id: int) -> int:
    """Return the index of the todo with given ID, or -1 if not found."""
    for i, t in enumerate(todos):
        if t["id"] == todo_id:
            return i
    return -1


def cmd_add(args: argparse.Namespace) -> None:
    """Add a new todo with the given title."""
    todos = load_todos()
    todo = {"id": next_id(todos), "title": args.title, "done": False}
    todos.append(todo)
    save_todos(todos)
    print(todo["id"])


def cmd_list(todos: argparse.Namespace) -> None:
    """Print all todos."""
    todos = load_todos()
    if not todos:
        print("No todos.")
        return
    for t in todos:
        status = "x" if t["done"] else "·"
        print(f"[{t['id']}] {status} {t['title']}")


def cmd_done(args: argparse.Namespace) -> None:
    """Mark a todo done by ID."""
    todos = load_todos()
    idx = find_todo(todos, args.id)
    if idx == -1:
        print(f"Error: todo with ID {args.id} not found.", file=sys.stderr)
        sys.exit(1)
    todos[idx]["done"] = True
    save_todos(todos)


def cmd_rm(args: argparse.Namespace) -> None:
    """Delete a todo by ID."""
    todos = load_todos()
    idx = find_todo(todos, args.id)
    if idx == -1:
        print(f"Error: todo with ID {args.id} not found.", file=sys.stderr)
        sys.exit(1)
    del todos[idx]
    save_todos(todos)


def cmd_clear(todos: argparse.Namespace) -> None:
    """Remove all done todos."""
    todos = load_todos()
    remaining = [t for t in todos if not t["done"]]
    if len(remaining) == len(todos):
        print("No done todos to clear.")
    else:
        saved = len(todos) - len(remaining)
        todos = remaining
        save_todos(todos)
        print(f"Cleared {saved} done todo(s).")


def main() -> None:
    parser = argparse.ArgumentParser(description="Tiny CLI todo manager")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # add
    add_parser = subparsers.add_parser("add", help="Add a new todo")
    add_parser.add_argument("title", help="Title of the todo")

    # list
    subparsers.add_parser("list", help="List all todos")

    # done
    done_parser = subparsers.add_parser("done", help="Mark a todo done")
    done_parser.add_argument("id", type=int, help="Todo ID")

    # rm
    rm_parser = subparsers.add_parser("rm", help="Remove a todo")
    rm_parser.add_argument("id", type=int, help="Todo ID")

    # clear
    subparsers.add_parser("clear", help="Clear all done todos")

    args = parser.parse_args()

    commands = {
        "add": cmd_add,
        "list": cmd_list,
        "done": cmd_done,
        "rm": cmd_rm,
        "clear": cmd_clear,
    }

    commands[args.command](args)


if __name__ == "__main__":
    main()