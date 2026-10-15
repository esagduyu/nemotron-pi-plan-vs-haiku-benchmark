#!/usr/bin/env python3
"""Tiny CLI todo manager."""

import argparse
import json
import os
import sys

DATA_FILE = "todos.json"


def load_todos():
    """Load todos from JSON file. Returns list of dicts."""
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r") as f:
        return json.load(f)


def save_todos(todos):
    """Save todos to JSON file."""
    with open(DATA_FILE, "w") as f:
        json.dump(todos, f, indent=2)


def next_id(todos):
    """Return the next monotonically increasing ID."""
    if not todos:
        return 1
    return max(t["id"] for t in todos) + 1


def cmd_add(args):
    """Add a new todo."""
    todos = load_todos()
    new_todo = {"id": next_id(todos), "title": args.title, "done": False}
    todos.append(new_todo)
    save_todos(todos)
    print(f"Added todo {new_todo['id']}: {new_todo['title']}")


def cmd_list(args):
    """List all todos."""
    todos = load_todos()
    if not todos:
        print("No todos.")
        return
    for t in todos:
        status = "x" if t["done"] else "·"
        print(f"[{t['id']}] [{status}] {t['title']}")


def cmd_done(args):
    """Mark a todo as done."""
    todos = load_todos()
    for t in todos:
        if t["id"] == args.id:
            t["done"] = True
            save_todos(todos)
            print(f"Todo {t['id']} marked done.")
            return
    print(f"Error: no todo with ID {args.id}", file=sys.stderr)
    sys.exit(1)


def cmd_rm(args):
    """Remove a todo by ID."""
    todos = load_todos()
    for i, t in enumerate(todos):
        if t["id"] == args.id:
            todos.pop(i)
            save_todos(todos)
            print(f"Removed todo {t['id']}.")
            return
    print(f"Error: no todo with ID {args.id}", file=sys.stderr)
    sys.exit(1)


def cmd_clear(args):
    """Remove all done todos."""
    todos = load_todos()
    before = len(todos)
    todos = [t for t in todos if not t["done"]]
    after = len(todos)
    removed = before - after
    save_todos(todos)
    print(f"Cleared {removed} done todo(s).")


def main():
    parser = argparse.ArgumentParser(description="Tiny CLI todo manager")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # add
    add_parser = subparsers.add_parser("add", help="Add a new todo")
    add_parser.add_argument("title", help="Todo title")
    add_parser.set_defaults(func=cmd_add)

    # list
    list_parser = subparsers.add_parser("list", help="List all todos")
    list_parser.set_defaults(func=cmd_list)

    # done
    done_parser = subparsers.add_parser("done", help="Mark a todo done")
    done_parser.add_argument("id", type=int, help="Todo ID")
    done_parser.set_defaults(func=cmd_done)

    # rm
    rm_parser = subparsers.add_parser("rm", help="Remove a todo")
    rm_parser.add_argument("id", type=int, help="Todo ID")
    rm_parser.set_defaults(func=cmd_rm)

    # clear
    clear_parser = subparsers.add_parser("clear", help="Remove all done todos")
    clear_parser.set_defaults(func=cmd_clear)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
