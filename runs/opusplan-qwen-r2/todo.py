"""Tiny CLI todo manager with JSON persistence."""

import json
import os
import sys
import tempfile
from typing import Any


class TodoError(Exception):
    """Raised when a todo operation fails (missing ID, corrupt data, etc.)."""


def _store_path() -> str:
    """Return the path to the JSON store, from TODO_FILE env or default."""
    return os.environ.get("TODO_FILE", "todos.json")


def load(path: str | None = None) -> dict[str, Any]:
    """Load the todo store from disk.

    Returns an empty store (next_id=1, todos=[]) when the file is missing.
    Raises TodoError on invalid JSON or wrong structure.
    """
    if path is None:
        path = _store_path()
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        return {"next_id": 1, "todos": []}
    except json.JSONDecodeError as exc:
        raise TodoError(f"Corrupt store file: {exc}") from exc

    if not isinstance(data, dict):
        raise TodoError("Store file has wrong structure: expected a JSON object")
    if "next_id" not in data or not isinstance(data["next_id"], int):
        raise TodoError("Store file missing or invalid 'next_id' field")
    if "todos" not in data or not isinstance(data["todos"], list):
        raise TodoError("Store file missing or invalid 'todos' field")
    return data


def save(path: str | None = None, data: dict[str, Any] | None = None) -> None:
    """Atomically save the todo store to disk (temp file + os.replace)."""
    if path is None:
        path = _store_path()
    if data is None:
        data = load(path)
    dir_name = os.path.dirname(path) or "."
    fd, tmp_path = tempfile.mkstemp(dir=dir_name, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
            f.write("\n")
        os.replace(tmp_path, path)
    except BaseException:
        os.unlink(tmp_path)
        raise


def add_todo(data: dict[str, Any], title: str) -> int:
    """Add a new todo. Returns the new ID. Rejects empty/whitespace titles."""
    if not title.strip():
        raise TodoError("Title cannot be empty")
    todo_id = data["next_id"]
    data["todos"].append({"id": todo_id, "title": title, "done": False})
    data["next_id"] = todo_id + 1
    return todo_id


def mark_done(data: dict[str, Any], todo_id: int) -> None:
    """Mark a todo as done. Raises TodoError if ID not found."""
    for todo in data["todos"]:
        if todo["id"] == todo_id:
            todo["done"] = True
            return
    raise TodoError(f"Todo with ID {todo_id} not found")


def remove_todo(data: dict[str, Any], todo_id: int) -> None:
    """Remove a todo by ID. Raises TodoError if not found. Does not reuse IDs."""
    for i, todo in enumerate(data["todos"]):
        if todo["id"] == todo_id:
            data["todos"].pop(i)
            return
    raise TodoError(f"Todo with ID {todo_id} not found")


def clear_done(data: dict[str, Any]) -> int:
    """Remove all done todos. Returns count removed."""
    before = len(data["todos"])
    data["todos"] = [t for t in data["todos"] if not t["done"]]
    return before - len(data["todos"])


def format_todo(todo: dict[str, Any]) -> str:
    """Format a single todo as '[ID] [x|·] title'."""
    status = "x" if todo["done"] else "·"
    return f"[{todo['id']}] [{status}] {todo['title']}"


def main(argv: list[str] | None = None) -> int:
    """CLI entry point. Returns an exit code."""
    import argparse

    parser = argparse.ArgumentParser(description="Tiny CLI todo manager")
    sub = parser.add_subparsers(dest="command")

    add_p = sub.add_parser("add", help="Add a new todo")
    add_p.add_argument("title", help="Title of the new todo")
    sub.add_parser("list", help="List all todos")
    done_p = sub.add_parser("done", help="Mark a todo as done")
    done_p.add_argument("id", type=int, help="ID of the todo to mark done")
    rm_p = sub.add_parser("rm", help="Remove a todo")
    rm_p.add_argument("id", type=int, help="ID of the todo to remove")
    sub.add_parser("clear", help="Remove all done todos")

    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help(sys.stderr)
        return 1

    try:
        data = load()

        if args.command == "add":
            if not args.title:
                raise TodoError("Title cannot be empty")
            new_id = add_todo(data, args.title)
            save(data=data)
            print(f"Added todo {new_id}")
            return 0

        if args.command == "list":
            for todo in data["todos"]:
                print(format_todo(todo))
            return 0

        if args.command == "done":
            mark_done(data, args.id)
            save(data=data)
            print(f"Todo {args.id} marked done")
            return 0

        if args.command == "rm":
            remove_todo(data, args.id)
            save(data=data)
            print(f"Todo {args.id} removed")
            return 0

        if args.command == "clear":
            count = clear_done(data)
            save(data=data)
            print(f"Removed {count} done todo(s)")
            return 0

    except TodoError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
