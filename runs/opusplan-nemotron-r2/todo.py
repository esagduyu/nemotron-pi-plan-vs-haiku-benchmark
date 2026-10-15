"""Tiny CLI todo manager — stdlib only."""

import argparse
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List


class TodoError(Exception):
    """Raised for todo-app business logic errors."""


def _default_path() -> Path:
    """Return the default storage path, overridable via TODO_FILE env var."""
    return Path(os.environ.get("TODO_FILE", "./todos.json"))


def load(path: str | Path | None = None) -> Dict[str, Any]:
    """Load the todo store from *path*.

    Returns ``{"next_id": int, "todos": [...]}``.
    If the file is missing, returns an empty store.
    Raises TodoError on invalid JSON or wrong structure.
    """
    if path is None:
        path = _default_path()
    if isinstance(path, str):
        path = Path(path)
    if not path.exists():
        return {"next_id": 1, "todos": []}
    try:
        text = path.read_text(encoding="utf-8")
        data = json.loads(text)
    except (json.JSONDecodeError, OSError) as exc:
        raise TodoError(f"cannot read todo file: {exc}") from None
    # Validate structure
    if not isinstance(data, dict):
        raise TodoError("store must be a JSON object")
    if "next_id" not in data or "todos" not in data:
        raise TodoError("store missing required keys: next_id, todos")
    if not isinstance(data["next_id"], int):
        raise TodoError("next_id must be an integer")
    if not isinstance(data["todos"], list):
        raise TodoError("todos must be a list")
    for i, t in enumerate(data["todos"]):
        if not isinstance(t, dict):
            raise TodoError(f"todo entry {i} must be an object")
        if "id" not in t or "title" not in t or "done" not in t:
            raise TodoError(f"todo entry {i} missing id/title/done")
        if not isinstance(t["id"], int):
            raise TodoError(f"todo entry {i} id must be an integer")
        if not isinstance(t["title"], str):
            raise TodoError(f"todo entry {i} title must be a string")
        if not isinstance(t["done"], bool):
            raise TodoError(f"todo entry {i} done must be a boolean")
    return data


def save(path: Path, data: Dict[str, Any]) -> None:
    """Write the store atomically using a temp file + os.replace."""
    path_str = str(path)
    parent = os.path.dirname(path_str)
    os.makedirs(parent, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=parent, prefix=".todo_")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        os.replace(tmp, path_str)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


# ---------------------------------------------------------------------------
# Core operations
# ---------------------------------------------------------------------------

def add_todo(data: Dict[str, Any], title: str) -> int:
    """Add a new open todo and return its ID.

    Rejects empty or whitespace-only titles.
    """
    if not title or title.strip() == "":
        raise TodoError("title must not be empty or whitespace")
    todo_id = data["next_id"]
    data["next_id"] += 1
    data["todos"].append({"id": todo_id, "title": title, "done": False})
    return todo_id


def mark_done(data: Dict[str, Any], todo_id: int) -> None:
    """Mark the todo with *todo_id* as done.

    Raises TodoError if the ID is not found.
    """
    for todo in data["todos"]:
        if todo["id"] == todo_id:
            todo["done"] = True
            return
    raise TodoError(f"todo with id {todo_id} not found")


def remove_todo(data: Dict[str, Any], todo_id: int) -> None:
    """Remove the todo with *todo_id*.

    Raises TodoError if the ID is not found.
    Does not decrement next_id.
    """
    for i, todo in enumerate(data["todos"]):
        if todo["id"] == todo_id:
            data["todos"].pop(i)
            return
    raise TodoError(f"todo with id {todo_id} not found")


def clear_done(data: Dict[str, Any]) -> int:
    """Remove all done todos and return the count removed."""
    before = len(data["todos"])
    data["todos"] = [t for t in data["todos"] if not t["done"]]
    return before - len(data["todos"])


def format_todo(todo: Dict[str, Any]) -> str:
    """Format a single todo as ``[ID] [x|·] title``."""
    marker = "x" if todo["done"] else "·"
    return f"[{todo['id']}] [{marker}] {todo['title']}"


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="todo.py",
        description="Tiny CLI todo manager",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # add <title>
    add_parser = subparsers.add_parser("add", help="Add a new todo")
    add_parser.add_argument("title", help="Title of the todo")

    # list
    subparsers.add_parser("list", help="List all todos")

    # done <id>
    done_parser = subparsers.add_parser("done", help="Mark a todo as done")
    done_parser.add_argument("id", type=int, help="Todo ID")

    # rm <id>
    rm_parser = subparsers.add_parser("rm", help="Remove a todo")
    rm_parser.add_argument("id", type=int, help="Todo ID")

    # clear
    subparsers.add_parser("clear", help="Clear all done todos")
    return parser


def main(argv: List[str] | None = None) -> int:
    """Entry point. Returns exit code."""
    parser = _build_parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        # argparse calls sys.exit(code) for --help / errors
        return exc.code if exc.code is not None else 0

    cmd = args.command
    try:
        env_path = str(_default_path())
        data = load(path=env_path)
    except TodoError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    # Attach the resolved path to data so save() can use it
    data["_path"] = env_path

    try:
        if cmd == "add":
            todo_id = add_todo(data, args.title)
            save(data["_path"], data)
            print(todo_id)
        elif cmd == "list":
            for todo in data["todos"]:
                print(format_todo(todo))
        elif cmd == "done":
            mark_done(data, args.id)
            save(data["_path"], data)
        elif cmd == "rm":
            remove_todo(data, args.id)
            save(data["_path"], data)
        elif cmd == "clear":
            count = clear_done(data)
            save(data["_path"], data)
            print(count)
    except TodoError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except Exception:
        sys.exit(1)