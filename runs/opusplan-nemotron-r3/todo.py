#!/usr/bin/env python3
"""Tiny CLI todo manager with JSON persistence."""

import argparse
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional


class TodoError(Exception):
    """Custom error for todo operations that should show a clean message."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


def resolve_path(path: str = "todos.json") -> Path:
    """Resolve the data path relative to the current working directory at call time."""
    return Path(path)


def load(path: str = "todos.json") -> Dict[str, Any]:
    """Load the todo store from a JSON file.

    Returns empty store {"next_id": 1, "todos": []} if the file is missing.
    Raises TodoError on unreadable or invalid JSON.
    """
    p = resolve_path(path)
    if not p.exists():
        return {"next_id": 1, "todos": []}
    try:
        with open(p, "r", encoding="utf-8") as f:
            data = json.load(f)
        # Validate schema minimally
        if not isinstance(data, dict):
            raise TodoError("Invalid JSON format: expected a JSON object")
        if "next_id" not in data or "todos" not in data:
            raise TodoError("Invalid JSON format: missing 'next_id' or 'todos'")
        return data
    except json.JSONDecodeError as e:
        raise TodoError(f"Invalid JSON: {e}")


def save(path: str, data: Dict[str, Any]) -> None:
    """Save the todo store to a JSON file atomically using temp file + os.replace."""
    p = resolve_path(path)
    # Write to a temp file in the same directory, then replace
    dir_name = p.parent if p.parent else "."
    # Ensure directory exists
    p.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(dir=dir_name, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        os.replace(tmp_path, p)
    except BaseException:
        # Clean up temp file if something went wrong
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise


def _generate_id(store: Dict[str, Any]) -> int:
    """Return the next ID and increment it in store."""
    next_id = store["next_id"]
    store["next_id"] = next_id + 1
    return next_id


def _find_todo(store: Dict[str, Any], todo_id: int) -> Optional[Dict[str, Any]]:
    """Find a todo by ID. Returns None if not found."""
    for todo in store["todos"]:
        if todo["id"] == todo_id:
            return todo
    return None


def add(title: str, path: str = "todos.json") -> int:
    """Add a new todo with the given title.

    Rejects empty or whitespace-only titles.
    Prints the new ID and saves.
    """
    if not title or title.strip() == "":
        raise TodoError("Title must not be empty or whitespace-only")
    store = load(path)
    todo_id = _generate_id(store)
    store["todos"].append({"id": todo_id, "title": title, "done": False})
    save(path, store)
    return todo_id


def list_todos(path: str = "todos.json") -> None:
    """Print all todos as [ID] [x|·] title. Print nothing when empty."""
    store = load(path)
    todos = store["todos"]
    if not todos:
        return
    for todo in todos:
        status = "x" if todo["done"] else "·"
        print(f"[{todo['id']}] [{status}] {todo['title']}")


def done(todo_id: int, path: str = "todos.json") -> None:
    """Mark a todo done by ID. No-op if already done. Error if ID not found."""
    store = load(path)
    todo = _find_todo(store, todo_id)
    if todo is None:
        raise TodoError(f"Todo with ID {todo_id} not found")
    todo["done"] = True
    save(path, store)


def rm(todo_id: int, path: str = "todos.json") -> None:
    """Delete the todo by ID. Error if ID not found. IDs are never reused."""
    store = load(path)
    todo = _find_todo(store, todo_id)
    if todo is None:
        raise TodoError(f"Todo with ID {todo_id} not found")
    store["todos"] = [t for t in store["todos"] if t["id"] != todo_id]
    save(path, store)


def clear_done(path: str = "todos.json") -> None:
    """Remove all done todos. Does not reset next_id."""
    store = load(path)
    before = len(store["todos"])
    store["todos"] = [t for t in store["todos"] if not t["done"]]
    after = len(store["todos"])
    # If nothing was cleared, it still succeeds silently
    save(path, store)


def _build_parser() -> argparse.ArgumentParser:
    """Build the argparse parser with subcommands."""
    parser = argparse.ArgumentParser(
        prog="todo.py", description="Tiny CLI todo manager"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # add <title>
    add_parser = subparsers.add_parser("add", help="Add a new todo")
    add_parser.add_argument("title", help="Title of the todo")

    # done <id>
    done_parser = subparsers.add_parser("done", help="Mark a todo done")
    done_parser.add_argument("id", type=int, help="Todo ID")

    # rm <id>
    rm_parser = subparsers.add_parser("rm", help="Remove a todo")
    rm_parser.add_argument("id", type=int, help="Todo ID")

    # clear
    clear_parser = subparsers.add_parser("clear", help="Clear all done todos")

    # list (no arguments)
    list_parser = subparsers.add_parser("list", help="List all todos")

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    """Entry point. Returns exit code."""
    parser = _build_parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as e:
        # argparse calls sys.exit(code) for --help or error; re-raise as-is
        raise

    command = args.command
    if command is None:
        parser.print_help()
        return 0

    path = "todos.json"

    try:
        if command == "add":
            result = add(args.title, path)
            print(result)
        elif command == "list":
            list_todos(path)
        elif command == "done":
            done(args.id, path)
        elif command == "rm":
            rm(args.id, path)
        elif command == "clear":
            clear_done(path)
        else:
            print(f"error: unknown command '{command}'", file=sys.stderr)
            return 1
    except TodoError as e:
        print(f"error: {e.message}", file=sys.stderr)
        return 1
    except OSError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        # Catch-all for unexpected errors — print usage info without traceback
        print(f"error: {e}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())