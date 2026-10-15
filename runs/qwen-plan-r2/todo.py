#!/usr/bin/env python3
"""Tiny CLI todo manager — stdlib only."""

import argparse
import json
import os
import sys

DATA_FILE = "todos.json"


def load_todos():
    """Load todos from JSON file. Returns (list, max_id) or ([], 0)."""
    if not os.path.exists(DATA_FILE):
        return [], 0
    try:
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
        if isinstance(data, dict) and "_max_id" in data:
            return data.get("_todos", []), data["_max_id"]
        if isinstance(data, list):
            max_id = max((t["id"] for t in data), default=0)
            return data, max_id
        return [], 0
    except (json.JSONDecodeError, OSError):
        return [], 0


def save_todos(todos, max_id):
    """Save todos list to JSON file, persisting max_id."""
    data = {"_todos": todos, "_max_id": max_id}
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


def next_id(todos, max_id):
    """Return the next monotonically increasing ID, never reused."""
    return max_id + 1


def cmd_add(args):
    """Add a new todo."""
    title = args.title
    if not title.strip():
        print("Error: title cannot be empty", file=sys.stderr)
        sys.exit(1)
    todos, max_id = load_todos()
    new_id = next_id(todos, max_id)
    todo = {"id": new_id, "title": title, "done": False}
    todos.append(todo)
    save_todos(todos, new_id)
    print(f"Added todo {todo['id']}: {title}")


def cmd_list(_args):
    """List all todos."""
    todos, _ = load_todos()
    if not todos:
        print("No todos found.")
        return
    for todo in todos:
        status = "x" if todo["done"] else "·"
        print(f"[{todo['id']}] [{status}] {todo['title']}")


def cmd_done(args):
    """Mark a todo as done."""
    try:
        todo_id = int(args.id)
    except ValueError:
        print(f"Error: invalid ID '{args.id}'", file=sys.stderr)
        sys.exit(1)
    todos, max_id = load_todos()
    for todo in todos:
        if todo["id"] == todo_id:
            todo["done"] = True
            save_todos(todos, max_id)
            print(f"Todo {todo_id} marked done.")
            return
    print(f"Error: todo with ID {todo_id} not found", file=sys.stderr)
    sys.exit(1)


def cmd_rm(args):
    """Delete a todo by ID."""
    try:
        todo_id = int(args.id)
    except ValueError:
        print(f"Error: invalid ID '{args.id}'", file=sys.stderr)
        sys.exit(1)
    todos, max_id = load_todos()
    new_todos = [t for t in todos if t["id"] != todo_id]
    if len(new_todos) == len(todos):
        print(f"Error: todo with ID {todo_id} not found", file=sys.stderr)
        sys.exit(1)
    save_todos(new_todos, max_id)
    print(f"Deleted todo {todo_id}.")


def cmd_clear(_args):
    """Remove all done todos."""
    todos, max_id = load_todos()
    original_count = len(todos)
    todos = [t for t in todos if not t["done"]]
    save_todos(todos, max_id)
    removed = original_count - len(todos)
    print(f"Removed {removed} done todo(s).")


def main():
    parser = argparse.ArgumentParser(description="Tiny CLI todo manager")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # add
    add_parser = subparsers.add_parser("add", help="Add a new todo")
    add_parser.add_argument("title", type=str, help="Title of the todo")

    # list
    subparsers.add_parser("list", help="List all todos")

    # done
    done_parser = subparsers.add_parser("done", help="Mark a todo as done")
    done_parser.add_argument("id", type=str, help="ID of the todo to mark done")

    # rm
    rm_parser = subparsers.add_parser("rm", help="Delete a todo")
    rm_parser.add_argument("id", type=str, help="ID of the todo to delete")

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
