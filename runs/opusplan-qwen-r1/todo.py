"""Tiny CLI todo manager — stdlib only, JSON persistence."""

import argparse
import json
import os
import re
import sys
import tempfile

# Force UTF-8 stdout so "·" prints on any locale.
if sys.stdout.encoding != "utf-8":
    sys.stdout = open(sys.stdout.fileno(), mode="w", encoding="utf-8", closefd=False)

STORE_PATH = "./todos.json"


class TodoError(Exception):
    """Raised for application-level errors (bad IDs, corrupt file, …)."""


# ── Storage layer ────────────────────────────────────────────────────────────

def _default_store() -> dict:
    return {"next_id": 1, "todos": []}


def load(path: str = STORE_PATH) -> dict:
    """Load the todo store from *path*.

    Returns an empty store when the file is missing.
    Raises TodoError when the file is unreadable, not valid JSON, or has the
    wrong shape.
    """
    if not os.path.isfile(path):
        return _default_store()

    try:
        raw = open(path, "r", encoding="utf-8").read()
    except OSError as exc:
        raise TodoError(f"cannot read {path}: {exc}") from exc

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise TodoError(f"{path} is not valid JSON: {exc}") from exc

    if not isinstance(data, dict):
        raise TodoError(f"{path} has the wrong shape (expected a JSON object)")
    if "next_id" not in data or not isinstance(data["next_id"], int):
        raise TodoError(f"{path}: missing or invalid 'next_id'")
    if "todos" not in data or not isinstance(data["todos"], list):
        raise TodoError(f"{path}: missing or invalid 'todos'")

    return data


def save(data: dict, path: str = STORE_PATH) -> None:
    """Atomically write *data* to *path*."""
    dir_name = os.path.dirname(os.path.abspath(path))
    fd, tmp_path = tempfile.mkstemp(dir=dir_name, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2, ensure_ascii=False)
            fh.write("\n")
        os.replace(tmp_path, path)
    except BaseException:
        os.unlink(tmp_path)
        raise


# ── Core operations ──────────────────────────────────────────────────────────

def add_todo(data: dict, title: str) -> int:
    """Add a todo with *title*. Returns the new ID.

    Rejects empty / whitespace-only titles.
    """
    if not title or not title.strip():
        raise TodoError("title must not be empty")
    new_id = data["next_id"]
    data["todos"].append({"id": new_id, "title": title, "done": False})
    data["next_id"] = new_id + 1
    return new_id


def find_todo(data: dict, id: int) -> dict:
    """Return the todo with the given *id*. Raises TodoError if missing."""
    for todo in data["todos"]:
        if todo["id"] == id:
            return todo
    raise TodoError(f"no todo with id {id}")


def mark_done(data: dict, id: int) -> None:
    """Mark the todo with *id* as done (idempotent)."""
    todo = find_todo(data, id)
    todo["done"] = True


def remove_todo(data: dict, id: int) -> None:
    """Remove the todo with *id*. Does not touch next_id."""
    todo = find_todo(data, id)
    data["todos"].remove(todo)


def clear_done(data: dict) -> int:
    """Remove all done todos. Returns the number removed."""
    before = len(data["todos"])
    data["todos"] = [t for t in data["todos"] if not t["done"]]
    return before - len(data["todos"])


def format_todo(todo: dict) -> str:
    """Return ``[ID] [x] title`` or ``[ID] [·] title``."""
    status = "x" if todo["done"] else "·"
    return f"[{todo['id']}] [{status}] {todo['title']}"


# ── CLI ──────────────────────────────────────────────────────────────────────

def _positive_int(s: str) -> int:
    """Argparse type: must be a positive integer."""
    try:
        value = int(s)
    except ValueError:
        raise argparse.ArgumentTypeError(f"invalid positive integer: {s!r}")
    if value < 1:
        raise argparse.ArgumentTypeError(f"expected a positive integer, got {value}")
    return value


def main(argv=None) -> int:
    """Entry point. Returns an exit code."""
    parser = argparse.ArgumentParser(
        description="Tiny CLI todo manager",
    )
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("add", help="Add a new todo").add_argument(
        "title", help="Title of the todo"
    )
    sub.add_parser("list", help="List all todos")
    sub.add_parser("done", help="Mark a todo as done").add_argument(
        "id", type=_positive_int, help="ID of the todo"
    )
    sub.add_parser("rm", help="Remove a todo").add_argument(
        "id", type=_positive_int, help="ID of the todo"
    )
    sub.add_parser("clear", help="Remove all done todos")

    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        # argparse calls sys.exit on errors (code 2) or --help (code 0).
        # We let --help pass through; for errors we normalise to code 1.
        if exc.code == 0:
            return 0
        return 1

    if args.command is None:
        parser.print_help(sys.stderr)
        return 1

    try:
        data = load()
    except TodoError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    try:
        if args.command == "add":
            new_id = add_todo(data, args.title)
            save(data)
            print(f"Added todo {new_id}")
            return 0

        if args.command == "list":
            for todo in data["todos"]:
                print(format_todo(todo))
            return 0

        if args.command == "done":
            mark_done(data, args.id)
            save(data)
            return 0

        if args.command == "rm":
            remove_todo(data, args.id)
            save(data)
            return 0

        if args.command == "clear":
            removed = clear_done(data)
            save(data)
            print(f"Removed {removed} done todo(s)")
            return 0

    except TodoError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
