#!/usr/bin/env python3
"""Tiny CLI todo manager backed by a JSON file."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

TODOS_FILE = "todos.json"


def _load_todos(path: Path) -> list[dict[str, Any]]:
    """Load todos from the JSON file, returning an empty list if missing."""
    if not path.exists():
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError) as exc:
        print(f"Error reading {TODOS_FILE}: {exc}", file=sys.stderr)
        sys.exit(1)
    if not isinstance(data, list):
        print(f"Error: {TODOS_FILE} has invalid format (expected a list)", file=sys.stderr)
        sys.exit(1)
    return data


def _save_todos(todos: list[dict[str, Any]], path: Path) -> None:
    """Persist the todo list to disk."""
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(todos, f, indent=2)
            f.write("\n")
    except OSError as exc:
        print(f"Error writing {TODOS_FILE}: {exc}", file=sys.stderr)
        sys.exit(1)


def _next_id(todos: list[dict[str, Any]]) -> int:
    """Compute the next monotonically increasing ID."""
    if not todos:
        return 1
    return max(todo["id"] for todo in todos) + 1


def _find_todo(todos: list[dict[str, Any]], todo_id: int) -> dict[str, Any] | None:
    """Return the first todo matching *todo_id*, or None."""
    for todo in todos:
        if todo["id"] == todo_id:
            return todo
    return None


# ── subcommands ──────────────────────────────────────────────────────


def cmd_add(args: argparse.Namespace, base_dir: Path) -> None:
    if not args.title.strip():
        print("Error: title must not be empty", file=sys.stderr)
        sys.exit(1)

    todos = _load_todos(base_dir / TODOS_FILE)
    new_id = _next_id(todos)
    todos.append({"id": new_id, "title": args.title.strip(), "done": False})
    _save_todos(todos, base_dir / TODOS_FILE)
    print(f"Added todo #{new_id}")


def cmd_list(_args: argparse.Namespace, base_dir: Path) -> None:
    todos = _load_todos(base_dir / TODOS_FILE)
    if not todos:
        print("(no todos)")
        return
    for todo in todos:
        status = "x" if todo["done"] else "·"
        print(f"[{todo['id']}] [{status}] {todo['title']}")


def cmd_done(args: argparse.Namespace, base_dir: Path) -> None:
    todos = _load_todos(base_dir / TODOS_FILE)
    todo = _find_todo(todos, args.id)
    if todo is None:
        print(f"Error: todo #{args.id} not found", file=sys.stderr)
        sys.exit(1)
    todo["done"] = True
    _save_todos(todos, base_dir / TODOS_FILE)
    print(f"Todo #{args.id} marked done")


def cmd_rm(args: argparse.Namespace, base_dir: Path) -> None:
    todos = _load_todos(base_dir / TODOS_FILE)
    todo = _find_todo(todos, args.id)
    if todo is None:
        print(f"Error: todo #{args.id} not found", file=sys.stderr)
        sys.exit(1)
    todos.remove(todo)
    _save_todos(todos, base_dir / TODOS_FILE)
    print(f"Todo #{args.id} removed")


def cmd_clear(_args: argparse.Namespace, base_dir: Path) -> None:
    todos = _load_todos(base_dir / TODOS_FILE)
    before = len(todos)
    todos = [t for t in todos if not t["done"]]
    removed = before - len(todos)
    _save_todos(todos, base_dir / TODOS_FILE)
    print(f"Cleared {removed} done todo(s)")


# ── CLI setup ────────────────────────────────────────────────────────


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="todo.py",
        description="A tiny command-line todo manager.",
    )
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("add", help="Add a new todo").add_argument(
        "title", type=str, help="Title of the todo"
    )

    sub.add_parser("list", help="List all todos")

    done_p = sub.add_parser("done", help="Mark a todo as done")
    done_p.add_argument("id", type=int, help="ID of the todo to mark done")

    rm_p = sub.add_parser("rm", help="Remove a todo")
    rm_p.add_argument("id", type=int, help="ID of the todo to remove")

    sub.add_parser("clear", help="Remove all done todos")

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(1)

    base_dir = Path(os.getcwd())
    dispatch = {
        "add": cmd_add,
        "list": cmd_list,
        "done": cmd_done,
        "rm": cmd_rm,
        "clear": cmd_clear,
    }
    dispatch[args.command](args, base_dir)


if __name__ == "__main__":
    main()
