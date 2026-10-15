#!/usr/bin/env python3
"""Tiny CLI todo manager — stdlib only."""

import argparse
import json
import os
import sys

DEFAULT_PATH = os.path.join(os.getcwd(), "todos.json")


def load_todos(path: str) -> list[dict]:
    """Read todos from JSON file. Returns [] if file is missing."""
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, ValueError) as exc:
        print(f"Error: {path} contains invalid JSON: {exc}", file=sys.stderr)
        sys.exit(1)
    if not isinstance(data, list):
        print(f"Error: {path} does not contain a JSON array", file=sys.stderr)
        sys.exit(1)
    return data


def save_todos(path: str, todos: list[dict]) -> None:
    """Write todos list to JSON file."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(todos, f, indent=2)
        f.write("\n")


def next_id(todos: list[dict]) -> int:
    """Return the next monotonically increasing ID."""
    if not todos:
        return 1
    return max(todo["id"] for todo in todos) + 1


def cmd_add(args: argparse.Namespace) -> None:
    """Add a new todo."""
    todos = load_todos(args.todos)
    new_id = next_id(todos)
    todos.append({"id": new_id, "title": args.title, "done": False})
    save_todos(args.todos, todos)
    print(f"Added todo {new_id}: {args.title}")


def cmd_list(args: argparse.Namespace) -> None:
    """List all todos."""
    todos = load_todos(args.todos)
    if not todos:
        print("No todos found.")
        return
    for todo in todos:
        status = "x" if todo["done"] else "·"
        print(f"[{todo['id']}] [{status}] {todo['title']}")


def cmd_done(args: argparse.Namespace) -> None:
    """Mark a todo as done."""
    todos = load_todos(args.todos)
    for todo in todos:
        if todo["id"] == args.id:
            todo["done"] = True
            save_todos(args.todos, todos)
            print(f"Marked todo {args.id} as done.")
            return
    print(f"Error: No todo with ID {args.id}", file=sys.stderr)
    sys.exit(1)


def cmd_rm(args: argparse.Namespace) -> None:
    """Remove a todo by ID."""
    todos = load_todos(args.todos)
    new_todos = [t for t in todos if t["id"] != args.id]
    if len(new_todos) == len(todos):
        print(f"Error: No todo with ID {args.id}", file=sys.stderr)
        sys.exit(1)
    save_todos(args.todos, new_todos)
    print(f"Removed todo {args.id}.")


def cmd_clear(args: argparse.Namespace) -> None:
    """Remove all done todos."""
    todos = load_todos(args.todos)
    before = len(todos)
    todos = [t for t in todos if not t["done"]]
    removed = before - len(todos)
    save_todos(args.todos, todos)
    print(f"Removed {removed} done todo(s).")


def main() -> None:
    parser = argparse.ArgumentParser(description="Tiny CLI todo manager")
    parser.add_argument(
        "--todos",
        default=DEFAULT_PATH,
        help="Path to the todos JSON file (default: ./todos.json)",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # add
    add_parser = subparsers.add_parser("add", help="Add a new todo")
    add_parser.add_argument("title", help="Title of the todo")
    add_parser.set_defaults(func=cmd_add)

    # list
    list_parser = subparsers.add_parser("list", help="List all todos")
    list_parser.set_defaults(func=cmd_list)

    # done
    done_parser = subparsers.add_parser("done", help="Mark a todo as done")
    done_parser.add_argument("id", type=int, help="ID of the todo to mark done")
    done_parser.set_defaults(func=cmd_done)

    # rm
    rm_parser = subparsers.add_parser("rm", help="Remove a todo")
    rm_parser.add_argument("id", type=int, help="ID of the todo to remove")
    rm_parser.set_defaults(func=cmd_rm)

    # clear
    clear_parser = subparsers.add_parser("clear", help="Remove all done todos")
    clear_parser.set_defaults(func=cmd_clear)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
