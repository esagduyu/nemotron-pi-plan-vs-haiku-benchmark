#!/usr/bin/env python3
"""Tiny CLI todo manager.

Usage:
    python todo.py add <title>
    python todo.py list
    python todo.py done <id>
    python todo.py rm <id>
    python todo.py clear
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import List, Dict, Optional

TODO_FILE = Path("./todos.json")


def load_todos() -> List[Dict]:
    """Load todos from JSON file, creating empty list if file doesn't exist."""
    if not TODO_FILE.exists():
        return []
    try:
        with open(TODO_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
    except (json.JSONDecodeError, OSError):
        pass
    return []


def save_todos(todos: List[Dict]) -> None:
    """Save todos to JSON file."""
    with open(TODO_FILE, "w", encoding="utf-8") as f:
        json.dump(todos, f, indent=2)


def find_todo_index(todos: List[Dict], todo_id: int) -> Optional[int]:
    """Find the index of a todo by ID, or None if not found."""
    for i, todo in enumerate(todos):
        if todo.get("id") == todo_id:
            return i
    return None


def next_id(todos: List[Dict]) -> int:
    """Generate the next monotonically increasing ID."""
    if not todos:
        return 1
    return max(todo.get("id", 0) for todo in todos) + 1


def cmd_add(title: str) -> None:
    """Add a new todo with the given title."""
    todos = load_todos()
    new_todo = {"id": next_id(todos), "title": title, "done": False}
    todos.append(new_todo)
    save_todos(todos)
    print(new_todo["id"])


def cmd_list() -> None:
    """Print all todos."""
    todos = load_todos()
    if not todos:
        print("No todos.")
        return
    for todo in todos:
        status = "x" if todo.get("done") else "·"
        print(f"[{todo['id']}] {status} {todo['title']}")


def cmd_done(todo_id: int) -> None:
    """Mark a todo as done by ID."""
    todos = load_todos()
    idx = find_todo_index(todos, todo_id)
    if idx is None:
        print(f"Error: todo with ID {todo_id} not found", file=sys.stderr)
        sys.exit(1)
    todos[idx]["done"] = True
    save_todos(todos)


def cmd_rm(todo_id: int) -> None:
    """Delete a todo by ID."""
    todos = load_todos()
    idx = find_todo_index(todos, todo_id)
    if idx is None:
        print(f"Error: todo with ID {todo_id} not found", file=sys.stderr)
        sys.exit(1)
    del todos[idx]
    save_todos(todos)


def cmd_clear() -> None:
    """Remove all done todos."""
    todos = load_todos()
    before = len(todos)
    todos = [t for t in todos if not t.get("done", False)]
    after = len(todos)
    if after < before:
        save_todos(todos)
        print(f"Removed {before - after} done todo(s).")
    else:
        print("No done todos to remove.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Tiny CLI todo manager")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # add command
    add_parser = subparsers.add_parser("add", help="Add a new todo")
    add_parser.add_argument("title", help="Title of the todo")

    # list command
    subparsers.add_parser("list", help="List all todos")

    # done command
    done_parser = subparsers.add_parser("done", help="Mark a todo as done")
    done_parser.add_argument("id", type=int, help="ID of the todo to mark as done")

    # rm command
    rm_parser = subparsers.add_parser("rm", help="Remove a todo")
    rm_parser.add_argument("id", type=int, help="ID of the todo to remove")

    # clear command
    subparsers.add_parser("clear", help="Remove all done todos")

    args = parser.parse_args()

    if args.command == "add":
        cmd_add(args.title)
    elif args.command == "list":
        cmd_list()
    elif args.command == "done":
        cmd_done(args.id)
    elif args.command == "rm":
        cmd_rm(args.id)
    elif args.command == "clear":
        cmd_clear()
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()