#!/usr/bin/env python3
"""Tiny CLI todo manager."""

import argparse
import json
import os
import sys
from pathlib import Path

DATA_FILE = Path("todos.json")


def load_todos() -> list[dict]:
    """Load todos from the JSON file. Returns empty list if file missing."""
    if not DATA_FILE.exists():
        return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, list):
            raise ValueError("Invalid todos file: expected a list")
        return data
    except (json.JSONDecodeError, ValueError) as e:
        print(f"Error reading {DATA_FILE}: {e}", file=sys.stderr)
        sys.exit(1)


def save_todos(todos: list[dict]) -> None:
    """Save todos to the JSON file."""
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(todos, f, indent=2)
    except OSError as e:
        print(f"Error writing {DATA_FILE}: {e}", file=sys.stderr)
        sys.exit(1)


def next_id(todos: list[dict]) -> int:
    """Return the next monotonically increasing ID (never reused)."""
    if not todos:
        return 1
    return max(t["id"] for t in todos) + 1


def find_todo(todos: list[dict], todo_id: int) -> dict | None:
    """Find a todo by ID, or None if not found."""
    for t in todos:
        if t["id"] == todo_id:
            return t
    return None


def cmd_add(args: argparse.Namespace) -> None:
    """Add a new todo."""
    todos = load_todos()
    title = args.title
    if not title.strip():
        print("Error: title cannot be empty", file=sys.stderr)
        sys.exit(1)
    new_todo = {"id": next_id(todos), "title": title, "done": False}
    todos.append(new_todo)
    save_todos(todos)
    print(f"Added todo {new_todo['id']}: {title}")


def cmd_list(_args: argparse.Namespace) -> None:
    """List all todos."""
    todos = load_todos()
    if not todos:
        print("No todos found.")
        return
    for t in todos:
        status = "x" if t["done"] else "·"
        print(f"[{t['id']}] [{status}] {t['title']}")


def cmd_done(args: argparse.Namespace) -> None:
    """Mark a todo as done."""
    todos = load_todos()
    todo = find_todo(todos, args.id)
    if todo is None:
        print(f"Error: todo with ID {args.id} not found", file=sys.stderr)
        sys.exit(1)
    todo["done"] = True
    save_todos(todos)
    print(f"Todo {todo['id']} marked as done.")


def cmd_rm(args: argparse.Namespace) -> None:
    """Remove a todo by ID."""
    todos = load_todos()
    todo = find_todo(todos, args.id)
    if todo is None:
        print(f"Error: todo with ID {args.id} not found", file=sys.stderr)
        sys.exit(1)
    todos.remove(todo)
    save_todos(todos)
    print(f"Deleted todo {todo['id']}.")


def cmd_clear(_args: argparse.Namespace) -> None:
    """Remove all done todos."""
    todos = load_todos()
    before = len(todos)
    todos = [t for t in todos if not t["done"]]
    removed = before - len(todos)
    save_todos(todos)
    print(f"Cleared {removed} done todo(s).")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Tiny CLI todo manager"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # add
    add_parser = subparsers.add_parser("add", help="Add a new todo")
    add_parser.add_argument("title", type=str, help="Title of the todo")

    # list
    subparsers.add_parser("list", help="List all todos")

    # done
    done_parser = subparsers.add_parser("done", help="Mark a todo as done")
    done_parser.add_argument("id", type=int, help="ID of the todo to mark done")

    # rm
    rm_parser = subparsers.add_parser("rm", help="Remove a todo")
    rm_parser.add_argument("id", type=int, help="ID of the todo to remove")

    # clear
    subparsers.add_parser("clear", help="Remove all done todos")

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(1)

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
