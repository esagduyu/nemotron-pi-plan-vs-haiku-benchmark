#!/usr/bin/env python3
"""Tiny CLI todo manager using Python 3.11+ stdlib only."""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import List, Dict, Optional

TODO_FILE = Path("todos.json")


def load_todos() -> List[Dict]:
    """Load todos from JSON file, creating empty list if file doesn't exist."""
    if not TODO_FILE.exists():
        return []
    try:
        with open(TODO_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            return []
    except (json.JSONDecodeError, OSError):
        return []


def save_todos(todos: List[Dict]) -> None:
    """Save todos to JSON file."""
    with open(TODO_FILE, "w", encoding="utf-8") as f:
        json.dump(todos, f, indent=2)


def get_next_id(todos: List[Dict]) -> int:
    """Get the next monotonically increasing ID."""
    if not todos:
        return 1
    return max(t["id"] for t in todos) + 1


def find_todo(todos: List[Dict], todo_id: int) -> Optional[Dict]:
    """Find a todo by ID."""
    for t in todos:
        if t["id"] == todo_id:
            return t
    return None


def add_todo(title: str) -> int:
    """Add a new todo. Returns the new ID."""
    if not title.strip():
        print("Error: todo title cannot be empty", file=sys.stderr)
        sys.exit(1)
    todos = load_todos()
    new_id = get_next_id(todos)
    todos.append({"id": new_id, "title": title, "done": False})
    save_todos(todos)
    print(new_id)
    return new_id


def list_todos() -> None:
    """Print all todos."""
    todos = load_todos()
    if not todos:
        print("No todos.")
        return
    for t in todos:
        status = "x" if t["done"] else "·"
        print(f"[{t['id']}] {status} {t['title']}")


def done_todo(todo_id: int) -> None:
    """Mark a todo done by ID."""
    todos = load_todos()
    todo = find_todo(todos, todo_id)
    if todo is None:
        print(f"Error: todo with ID {todo_id} not found", file=sys.stderr)
        sys.exit(1)
    todo["done"] = True
    save_todos(todos)


def rm_todo(todo_id: int) -> None:
    """Delete a todo by ID."""
    todos = load_todos()
    todo = find_todo(todos, todo_id)
    if todo is None:
        print(f"Error: todo with ID {todo_id} not found", file=sys.stderr)
        sys.exit(1)
    todos.remove(todo)
    save_todos(todos)


def clear_todos() -> None:
    """Remove all done todos."""
    todos = load_todos()
    original_len = len(todos)
    todos[:] = [t for t in todos if not t["done"]]
    if len(todos) < original_len:
        save_todos(todos)


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
    done_parser.add_argument("id", type=int, help="Todo ID")

    # rm command
    rm_parser = subparsers.add_parser("rm", help="Remove a todo")
    rm_parser.add_argument("id", type=int, help="Todo ID")

    # clear command
    subparsers.add_parser("clear", help="Clear all done todos")

    args = parser.parse_args()

    if args.command == "add":
        add_todo(args.title)
    elif args.command == "list":
        list_todos()
    elif args.command == "done":
        done_todo(args.id)
    elif args.command == "rm":
        rm_todo(args.id)
    elif args.command == "clear":
        clear_todos()
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()