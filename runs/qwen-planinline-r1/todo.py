#!/usr/bin/env python3
"""Tiny CLI todo manager."""

import argparse
import json
import os
import sys

DATA_FILE = "todos.json"


def _load_data():
    """Load todos and next_id from the JSON data file."""
    if not os.path.exists(DATA_FILE):
        return [], 1
    with open(DATA_FILE, "r") as f:
        try:
            data = json.load(f)
            todos = data.get("todos", [])
            next_id = data.get("next_id", 1)
            return todos, next_id
        except json.JSONDecodeError:
            print("Error: corrupted data file.", file=sys.stderr)
            sys.exit(1)


def _save_data(todos, next_id):
    """Save todos and next_id to the JSON data file."""
    with open(DATA_FILE, "w") as f:
        json.dump({"todos": todos, "next_id": next_id}, f, indent=2)


def _next_id(next_id):
    """Return the next monotonically increasing ID and increment."""
    current = next_id
    return current, current + 1


def _find_todo(todos, todo_id):
    """Find a todo by ID. Print error and exit if not found."""
    for t in todos:
        if t["id"] == todo_id:
            return t
    print(f"Error: no todo with ID {todo_id}.", file=sys.stderr)
    sys.exit(1)


def cmd_add(args):
    """Add a new todo."""
    if not args.title:
        print("Error: title is required.", file=sys.stderr)
        sys.exit(1)
    todos, next_id = _load_data()
    new_id, next_id = _next_id(next_id)
    todos.append({"id": new_id, "title": args.title, "done": False})
    _save_data(todos, next_id)
    print(f"Added todo {new_id}: {args.title}")


def cmd_list(args):
    """List all todos."""
    todos, _ = _load_data()
    if not todos:
        print("No todos.")
        return
    for t in todos:
        status = "x" if t["done"] else "·"
        print(f"[{t['id']}] [{status}] {t['title']}")


def cmd_done(args):
    """Mark a todo as done."""
    try:
        todo_id = int(args.id)
    except ValueError:
        print(f"Error: invalid ID '{args.id}'. Must be an integer.", file=sys.stderr)
        sys.exit(1)
    todos, next_id = _load_data()
    todo = _find_todo(todos, todo_id)
    todo["done"] = True
    _save_data(todos, next_id)
    print(f"Todo {todo_id} marked done.")


def cmd_rm(args):
    """Remove a todo by ID."""
    try:
        todo_id = int(args.id)
    except ValueError:
        print(f"Error: invalid ID '{args.id}'. Must be an integer.", file=sys.stderr)
        sys.exit(1)
    todos, next_id = _load_data()
    _find_todo(todos, todo_id)  # validate existence
    todos = [t for t in todos if t["id"] != todo_id]
    _save_data(todos, next_id)
    print(f"Todo {todo_id} deleted.")


def cmd_clear(args):
    """Remove all done todos."""
    todos, next_id = _load_data()
    before = len(todos)
    todos = [t for t in todos if not t["done"]]
    removed = before - len(todos)
    _save_data(todos, next_id)
    print(f"Cleared {removed} done todo(s).")


def main():
    parser = argparse.ArgumentParser(description="Tiny CLI todo manager")
    subparsers = parser.add_subparsers(dest="command")

    # add
    add_parser = subparsers.add_parser("add", help="Add a new todo")
    add_parser.add_argument("title", nargs="?", default="", help="Todo title")

    # list
    subparsers.add_parser("list", help="List all todos")

    # done
    done_parser = subparsers.add_parser("done", help="Mark a todo done")
    done_parser.add_argument("id", help="Todo ID")

    # rm
    rm_parser = subparsers.add_parser("rm", help="Delete a todo")
    rm_parser.add_argument("id", help="Todo ID")

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
