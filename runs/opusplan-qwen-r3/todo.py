"""Tiny CLI todo manager with JSON persistence."""

import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any


class TodoError(Exception):
    """Raised when a business-logic or persistence error occurs."""


def _data_path() -> Path:
    """Return the path to todos.json relative to the current working directory."""
    return Path.cwd() / "todos.json"


def load(path: Path | None = None) -> dict[str, Any]:
    """Load the todo store from disk.

    Returns an empty store if the file is missing.
    Raises TodoError on unreadable or invalid JSON.
    """
    if path is None:
        path = _data_path()
    if not path.exists():
        return {"next_id": 1, "todos": []}
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise TodoError(f"cannot read {path}: {exc}") from exc
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise TodoError(f"invalid JSON in {path}: {exc}") from exc
    if not isinstance(data, dict) or "todos" not in data:
        raise TodoError(f"invalid store schema in {path}")
    return data


def save(data: dict[str, Any], path: Path | None = None) -> None:
    """Atomically write *data* to disk via temp-file + os.replace."""
    if path is None:
        path = _data_path()
    dir_ = path.parent
    fd, tmp = tempfile.mkstemp(dir=str(dir_), suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2)
            fh.write("\n")
        os.replace(tmp, str(path))
    except BaseException:
        os.unlink(tmp)
        raise


# ---------------------------------------------------------------------------
# Command implementations
# ---------------------------------------------------------------------------

def cmd_add(title: str, path: Path | None = None) -> int:
    """Add a new todo. Returns the new ID."""
    if not title.strip():
        raise TodoError("title must not be empty or whitespace-only")
    data = load(path)
    new_id = data["next_id"]
    data["todos"].append({"id": new_id, "title": title, "done": False})
    data["next_id"] = new_id + 1
    save(data, path)
    return new_id


def cmd_list(path: Path | None = None) -> list[str]:
    """Return the formatted list of todos."""
    data = load(path)
    lines: list[str] = []
    for todo in data["todos"]:
        status = "x" if todo["done"] else "·"
        lines.append(f"[{todo['id']}] [{status}] {todo['title']}")
    return lines


def cmd_done(todo_id: int, path: Path | None = None) -> None:
    """Mark a todo as done (idempotent)."""
    data = load(path)
    for todo in data["todos"]:
        if todo["id"] == todo_id:
            todo["done"] = True
            save(data, path)
            return
    raise TodoError(f"todo with id {todo_id} not found")


def cmd_rm(todo_id: int, path: Path | None = None) -> None:
    """Remove a todo by ID. next_id is unchanged."""
    data = load(path)
    before = len(data["todos"])
    data["todos"] = [t for t in data["todos"] if t["id"] != todo_id]
    if len(data["todos"]) == before:
        raise TodoError(f"todo with id {todo_id} not found")
    save(data, path)


def cmd_clear(path: Path | None = None) -> None:
    """Remove all done todos. next_id is unchanged."""
    data = load(path)
    data["todos"] = [t for t in data["todos"] if not t["done"]]
    save(data, path)


# ---------------------------------------------------------------------------
# CLI & entry-point
# ---------------------------------------------------------------------------

def _build_parser() -> "argparse.ArgumentParser":
    import argparse

    parser = argparse.ArgumentParser(
        prog="todo",
        description="Tiny CLI todo manager",
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


def main(argv: list[str] | None = None) -> int:
    """Run the CLI. Returns an exit code."""
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help(sys.stderr)
        return 1

    try:
        if args.command == "add":
            new_id = cmd_add(args.title)
            print(new_id)

        elif args.command == "list":
            for line in cmd_list():
                print(line)

        elif args.command == "done":
            cmd_done(args.id)
            print(f"marked todo {args.id} done")

        elif args.command == "rm":
            cmd_rm(args.id)
            print(f"removed todo {args.id}")

        elif args.command == "clear":
            cmd_clear()
            print("cleared all done todos")

    except (TodoError, OSError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
