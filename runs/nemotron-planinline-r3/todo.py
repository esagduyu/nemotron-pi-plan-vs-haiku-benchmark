#!/usr/bin/env python3
"""Todo manager CLI — argparse subcommands, JSON persistence."""

import argparse
import json
import os
import sys
from pathlib import Path

TODO_FILE = Path("todos.json")


def load_todos():
    """Load todos from JSON file, returning empty list if file missing/invalid."""
    if not TODO_FILE.exists():
        return []
    try:
        with open(TODO_FILE, "r") as f:
            data = json.load(f)
        if not isinstance(data, list):
            return []
        return data
    except (json.JSONDecodeError, ValueError):
        return []


def save_todos(todos):
    """Save todos list to JSON file."""
    with open(TODO_FILE, "w") as f:
        json.dump(todos, f, indent=2)


def get_next_id(todos):
    """Get the next monotonically increasing ID."""
    if not todos:
        return 1
    max_id = max(t["id"] for t in todos)
    return max_id + 1


def find_todo(todos, todo_id):
    """Find a todo by ID, returning (index, todo) or (None, None)."""
    for i, t in enumerate(todos):
        if t["id"] == todo_id:
            return i, t
    return None, None


def cmd_add(args):
    """Add a new todo with the given title."""
    todos = load_todos()
    new_id = get_next_id(todos)
    todo = {"id": new_id, "title": args.title, "done": False}
    todos.append(todo)
    save_todos(todos)
    print(new_id)


def cmd_list(_args):
    """List all todos as [ID] [x|·] title."""
    todos = load_todos()
    if not todos:
        print("No todos.")
        return
    for t in todos:
        marker = "x" if t["done"] else "·"
        print(f"[{t['id']}] {marker} {t['title']}")


def cmd_done(args):
    """Mark a todo done by ID."""
    todos = load_todos()
    idx, todo = find_todo(todos, args.id)
    if idx is None:
        print(f"Error: todo with ID {args.id} not found", file=sys.stderr)
        sys.exit(1)
    todos[idx]["done"] = True
    save_todos(todos)


def cmd_rm(args):
    """Remove a todo by ID."""
    todos = load_todos()
    idx, todo = find_todo(todos, args.id)
    if idx is None:
        print(f"Error: todo with ID {args.id} not found", file=sys.stderr)
        sys.exit(1)
    todos.pop(idx)
    save_todos(todos)


def cmd_clear(_):
    """Remove all done todos."""
    todos = load_todos()
    todos = [t for t in todos if not t["done"]]
    save_todos(todos)


def main():
    parser = argparse.ArgumentParser(description="Tiny CLI todo manager")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # add <title>
    add_parser = subparsers.add_parser("add", help="Add a new todo")
    add_parser.add_argument("title", help="Title of the todo")

    # list
    subparsers.add_parser("list", help="List all todos")

    # done <id>
    done_parser = subparsers.add_parser("done", help="Mark a todo done")
    done_parser.add_argument("id", type=int, help="Todo ID")

    # rm <id>
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