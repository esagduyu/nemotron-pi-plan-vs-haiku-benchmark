#!/usr/bin/env python3
"""Tiny CLI todo manager with JSON persistence."""

import argparse
import json
import os
import sys
from pathlib import Path

DATA_FILE = Path("todos.json")


def _load_todos() -> list[dict]:
    """Load todos from JSON file. Returns empty list if file missing or invalid."""
    if not DATA_FILE.exists():
        return []
    try:
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
        if not isinstance(data, list):
            return []
        return data
    except (json.JSONDecodeError, OSError):
        return []


def _save_todos(todos: list[dict]) -> None:
    """Save todos to JSON file."""
    with open(DATA_FILE, "w") as f:
        json.dump(todos, f, indent=2)
        f.write("\n")


def _next_id(todos: list[dict]) -> int:
    """Compute the next monotonically increasing ID."""
    if not todos:
        return 1
    return max(t["id"] for t in todos) + 1


def cmd_add(args: argparse.Namespace) -> None:
    """Add a new todo."""
    todos = _load_todos()
    new_todo = {"id": _next_id(todos), "title": args.title, "done": False}
    todos.append(new_todo)
    _save_todos(todos)
    print(f"Added todo {new_todo['id']}: {new_todo['title']}")


def cmd_list(_args: argparse.Namespace) -> None:
    """List all todos."""
    todos = _load_todos()
    if not todos:
        print("No todos.")
        return
    for todo in todos:
        status = "x" if todo["done"] else "·"
        print(f"[{todo['id']}] [{status}] {todo['title']}")


def cmd_done(args: argparse.Namespace) -> None:
    """Mark a todo as done."""
    todos = _load_todos()
    for todo in todos:
        if todo["id"] == args.id:
            todo["done"] = True
            _save_todos(todos)
            print(f"Todo {todo['id']} marked done.")
            return
    print(f"Error: no todo with ID {args.id}", file=sys.stderr)
    sys.exit(1)


def cmd_rm(args: argparse.Namespace) -> None:
    """Delete a todo by ID."""
    todos = _load_todos()
    new_todos = [t for t in todos if t["id"] != args.id]
    if len(new_todos) == len(todos):
        print(f"Error: no todo with ID {args.id}", file=sys.stderr)
        sys.exit(1)
    _save_todos(new_todos)
    print(f"Deleted todo {args.id}.")


def cmd_clear(_args: argparse.Namespace) -> None:
    """Remove all done todos."""
    todos = _load_todos()
    before = len(todos)
    todos = [t for t in todos if not t["done"]]
    removed = before - len(todos)
    _save_todos(todos)
    print(f"Cleared {removed} done todo(s).")


def main() -> None:
    parser = argparse.ArgumentParser(description="Tiny CLI todo manager")
    subparsers = parser.add_subparsers(dest="command")

    # add
    add_p = subparsers.add_parser("add", help="Add a new todo")
    add_p.add_argument("title", help="Title of the todo")

    # list
    subparsers.add_parser("list", help="List all todos")

    # done
    done_p = subparsers.add_parser("done", help="Mark a todo as done")
    done_p.add_argument("id", type=int, help="ID of the todo to mark done")

    # rm
    rm_p = subparsers.add_parser("rm", help="Delete a todo")
    rm_p.add_argument("id", type=int, help="ID of the todo to delete")

    # clear
    subparsers.add_parser("clear", help="Remove all done todos")

    args = parser.parse_args()
    if args.command is None:
        parser.print_help()
        sys.exit(1)

    match args.command:
        case "add":
            cmd_add(args)
        case "list":
            cmd_list(args)
        case "done":
            cmd_done(args)
        case "rm":
            cmd_rm(args)
        case "clear":
            cmd_clear(args)


if __name__ == "__main__":
    main()
