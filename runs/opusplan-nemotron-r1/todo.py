"""Tiny CLI todo manager — stdlib only."""

import argparse
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional

ERROR_MSG = "error: "
TODO_FILE = "./todos.json"


class TodoError(Exception):
    """Custom error for todo operations."""

    pass


# ── Storage layer ──────────────────────────────────────────────────────────

def load(path: str = TODO_FILE) -> Dict[str, Any]:
    """Load the JSON store from *path*.

    Returns ``{"next_id": int, "todos": [...]}``.
    If the file is missing, returns an empty store.
    Raises TodoError for unreadable / invalid / wrong-shape files.
    """
    if not os.path.exists(path):
        return {"next_id": 1, "todos": []}
    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
    except json.JSONDecodeError as exc:
        raise TodoError(f"invalid JSON in {path}") from exc
    except OSError as exc:
        raise TodoError(f"cannot read {path}") from exc
    # Validate shape
    if not isinstance(data, dict):
        raise TodoError(f"expected dict in {path}, got {type(data).__name__}")
    if "next_id" not in data or "todos" not in data:
        raise TodoError(f"missing keys in {path}")
    if not isinstance(data["next_id"], int):
        raise TodoError(f"next_id must be int in {path}")
    if not isinstance(data["todos"], list):
        raise TodoError(f"todos must be list in {path}")
    for i, t in enumerate(data["todos"]):
        if not isinstance(t, dict):
            raise TodoError(f"todo at index {i} is not a dict")
        if "id" not in t or "title" not in t or "done" not in t:
            raise TodoError(f"todo at index {i} missing required fields")
        if not isinstance(t["id"], int):
            raise TodoError(f"todo id at index {i} must be int")
        if not isinstance(t["title"], str):
            raise TodoError(f"todo title at index {i} must be str")
        if not isinstance(t["done"], bool):
            raise TodoError(f"todo done at index {i} must be bool")
    return data


def save(path: str, data: Dict[str, Any]) -> None:
    """Atomically write *data* to *path* via a temp file + replace."""
    directory = os.path.dirname(path) or "."
    fd, tmp_path = tempfile.mkstemp(dir=directory, suffix=".json")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2)
            fh.write("\n")
        os.replace(tmp_path, path)
    except BaseException:
        # Clean up temp file on failure
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise


# ── Core operations (pure functions on the store) ─────────────────────────

def add_todo(data: Dict[str, Any], title: str) -> int:
    """Add a new todo with *title*.

    Rejects empty or whitespace-only titles.
    Assigns next_id, increments next_id, returns the new ID.
    """
    if not title or title.isspace():
        raise TodoError("title must not be empty or whitespace-only")
    new_id = data["next_id"]
    data["todos"].append({"id": new_id, "title": title, "done": False})
    data["next_id"] = new_id + 1
    return new_id


def find_todo(data: Dict[str, Any], id_: int) -> Optional[Dict[str, Any]]:
    """Return the todo dict with the given *id*, or None."""
    for todo in data["todos"]:
        if todo["id"] == id_:
            return todo
    return None


def find_todo_raise(data: Dict[str, Any], id_: int) -> Dict[str, Any]:
    """Return the todo dict with the given *id*, or raise TodoError."""
    todo = find_todo(data, id_)
    if todo is None:
        raise TodoError(f"no todo with id {id_}")
    return todo


def mark_done(data: Dict[str, Any], id_: int) -> None:
    """Set the todo with *id* to done. Idempotent if already done."""
    todo = find_todo_raise(data, id_)
    todo["done"] = True


def remove_todo(data: Dict[str, Any], id_: int) -> None:
    """Delete the todo with *id* without touching next_id."""
    todo = find_todo_raise(data, id_)
    data["todos"].remove(todo)


def clear_done(data: Dict[str, Any]) -> int:
    """Remove all done todos and return how many were removed."""
    before = len(data["todos"])
    data["todos"] = [t for t in data["todos"] if not t["done"]]
    return before - len(data["todos"])


def format_todo(todo: Dict[str, Any]) -> str:
    """Format a single todo: ``[ID] [x] title`` or ``[ID] [·] title``."""
    marker = "x" if todo["done"] else "·"
    return f"[{todo['id']}] [{marker}] {todo['title']}"


# ── Formatting a whole store ───────────────────────────────────────────────

def format_all(data: Dict[str, Any]) -> List[str]:
    """Return formatted lines for all todos in *data*."""
    return [format_todo(t) for t in data["todos"]]


# ── CLI ─────────────────────────────────────────────────────────────────────

def _positive_int(value: str) -> int:
    """Argparse type: accept only positive integers, reject others."""
    try:
        iv = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"positive integer expected, got {value!r}")
    if iv <= 0:
        raise argparse.ArgumentTypeError(f"positive integer expected, got {value!r}")
    return iv


def main(argv: Optional[List[str]] = None) -> int:
    """Run the CLI. Returns an exit code (0 = success, 1 = error, 2 = argparse)."""
    # Force UTF-8 stdout so · prints on any locale
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
        except Exception:
            pass

    parser = argparse.ArgumentParser(
        prog="todo.py", description="Tiny CLI todo manager"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # add <title>
    add_parser = subparsers.add_parser("add", help="Add a new todo")
    add_parser.add_argument("title", type=str, help="Todo title")

    # list
    subparsers.add_parser("list", help="List all todos")

    # done <id>
    done_parser = subparsers.add_parser("done", help="Mark a todo done")
    done_parser.add_argument("id", type=_positive_int, help="Todo ID")

    # rm <id>
    rm_parser = subparsers.add_parser("rm", help="Remove a todo")
    rm_parser.add_argument("id", type=_positive_int, help="Todo ID")

    # clear
    subparsers.add_parser("clear", help="Clear all done todos")

    args = parser.parse_args(argv)

    # Load store
    try:
        data = load(TODO_FILE)
    except TodoError as exc:
        print(ERROR_MSG + str(exc), file=sys.stderr)
        return 1

    cmd = args.command

    try:
        if cmd == "add":
            new_id = add_todo(data, args.title)
            save(TODO_FILE, data)
            print(new_id)
            return 0

        elif cmd == "list":
            lines = format_all(data)
            for line in lines:
                print(line)
            return 0

        elif cmd == "done":
            mark_done(data, args.id)
            save(TODO_FILE, data)
            return 0

        elif cmd == "rm":
            remove_todo(data, args.id)
            save(TODO_FILE, data)
            return 0

        elif cmd == "clear":
            n = clear_done(data)
            if n > 0:
                save(TODO_FILE, data)
            return 0

    except TodoError as exc:
        print(ERROR_MSG + str(exc), file=sys.stderr)
        return 1

    # Should not reach here, but safety net
    print(ERROR_MSG + "unexpected error", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())