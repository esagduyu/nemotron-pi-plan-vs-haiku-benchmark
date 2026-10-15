#!/usr/bin/env python3
"""A tiny command-line todo manager backed by a JSON file."""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

DEFAULT_PATH = Path("todos.json")


class TodoError(Exception):
    """A user-facing error. Reported on stderr with a non-zero exit code."""


@dataclass
class Todo:
    id: int
    title: str
    done: bool = False


class Store:
    """Loads and saves the todo list to a JSON file.

    File format: {"next_id": <int>, "todos": [{"id": int, "title": str, "done": bool}, ...]}

    ``next_id`` is stored explicitly so IDs are never reused, even after
    the highest-numbered todo has been deleted.
    """

    def __init__(self, path: Path) -> None:
        self.path = path

    def load(self) -> tuple[int, list[Todo]]:
        """Return (next_id, todos). A missing file means an empty list."""
        if not self.path.exists():
            return 1, []
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise TodoError(f"cannot read {self.path}: {exc}") from exc

        try:
            todos = [_parse_todo(item) for item in data["todos"]]
            next_id = _as_int(data["next_id"], "next_id")
        except (KeyError, TypeError, ValueError) as exc:
            raise TodoError(f"{self.path} has an invalid format: {exc}") from exc

        # Guard against a hand-edited file that would hand out a duplicate ID.
        highest = max((t.id for t in todos), default=0)
        return max(next_id, highest + 1), todos

    def save(self, next_id: int, todos: list[Todo]) -> None:
        """Write atomically so a crash mid-write cannot corrupt the file."""
        data = {"next_id": next_id, "todos": [vars(t) for t in todos]}
        fd, tmp_name = tempfile.mkstemp(dir=self.path.parent or ".", suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                json.dump(data, handle, indent=2)
                handle.write("\n")
            os.replace(tmp_name, self.path)
        except OSError as exc:
            os.unlink(tmp_name)
            raise TodoError(f"cannot write {self.path}: {exc}") from exc


def _as_int(value: Any, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{field} must be an integer, got {value!r}")
    return value


def _parse_todo(item: Any) -> Todo:
    if not isinstance(item, dict):
        raise TypeError(f"todo must be an object, got {item!r}")
    title = item["title"]
    done = item["done"]
    if not isinstance(title, str):
        raise ValueError(f"title must be a string, got {title!r}")
    if not isinstance(done, bool):
        raise ValueError(f"done must be a boolean, got {done!r}")
    return Todo(id=_as_int(item["id"], "id"), title=title, done=done)


# --- Operations -----------------------------------------------------------


def add_todo(store: Store, title: str) -> int:
    title = title.strip()
    if not title:
        raise TodoError("title must not be empty")
    next_id, todos = store.load()
    todos.append(Todo(id=next_id, title=title))
    store.save(next_id + 1, todos)
    return next_id


def list_todos(store: Store) -> list[Todo]:
    _, todos = store.load()
    return todos


def mark_done(store: Store, todo_id: int) -> None:
    next_id, todos = store.load()
    _find(todos, todo_id).done = True
    store.save(next_id, todos)


def remove_todo(store: Store, todo_id: int) -> None:
    next_id, todos = store.load()
    _find(todos, todo_id)
    store.save(next_id, [t for t in todos if t.id != todo_id])


def clear_done(store: Store) -> int:
    """Remove all done todos. Returns how many were removed."""
    next_id, todos = store.load()
    remaining = [t for t in todos if not t.done]
    if len(remaining) != len(todos):
        store.save(next_id, remaining)
    return len(todos) - len(remaining)


def _find(todos: list[Todo], todo_id: int) -> Todo:
    for todo in todos:
        if todo.id == todo_id:
            return todo
    raise TodoError(f"no todo with id {todo_id}")


def format_todo(todo: Todo) -> str:
    mark = "x" if todo.done else "·"
    return f"[{todo.id}] [{mark}] {todo.title}"


# --- CLI ------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="todo.py", description="A tiny todo manager.")
    parser.add_argument(
        "--file",
        type=Path,
        default=DEFAULT_PATH,
        help="JSON file to store todos in (default: ./todos.json)",
    )
    commands = parser.add_subparsers(dest="command", required=True, metavar="command")

    add = commands.add_parser("add", help="add a new todo")
    add.add_argument("title", help="text of the todo")

    commands.add_parser("list", help="list all todos")

    done = commands.add_parser("done", help="mark a todo as done")
    done.add_argument("id", type=int, help="ID of the todo")

    rm = commands.add_parser("rm", help="delete a todo")
    rm.add_argument("id", type=int, help="ID of the todo")

    commands.add_parser("clear", help="remove all done todos")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    store = Store(args.file)
    try:
        if args.command == "add":
            print(add_todo(store, args.title))
        elif args.command == "list":
            todos = list_todos(store)
            if not todos:
                print("No todos.")
            for todo in todos:
                print(format_todo(todo))
        elif args.command == "done":
            mark_done(store, args.id)
            print(f"Marked {args.id} as done.")
        elif args.command == "rm":
            remove_todo(store, args.id)
            print(f"Removed {args.id}.")
        elif args.command == "clear":
            print(f"Removed {clear_done(store)} done todo(s).")
    except TodoError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
