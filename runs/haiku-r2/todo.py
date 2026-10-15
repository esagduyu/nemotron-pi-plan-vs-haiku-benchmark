#!/usr/bin/env python3
"""Tiny command-line todo manager backed by a JSON file."""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass, field
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


@dataclass
class TodoList:
    todos: list[Todo] = field(default_factory=list)
    # Stored on disk so IDs are never reused, even after the highest one is removed.
    next_id: int = 1

    def add(self, title: str) -> Todo:
        title = title.strip()
        if not title:
            raise TodoError("title must not be empty")
        todo = Todo(id=self.next_id, title=title)
        self.todos.append(todo)
        self.next_id += 1
        return todo

    def get(self, todo_id: int) -> Todo:
        for todo in self.todos:
            if todo.id == todo_id:
                return todo
        raise TodoError(f"no todo with id {todo_id}")

    def mark_done(self, todo_id: int) -> Todo:
        todo = self.get(todo_id)
        todo.done = True
        return todo

    def remove(self, todo_id: int) -> Todo:
        todo = self.get(todo_id)
        self.todos = [t for t in self.todos if t.id != todo_id]
        return todo

    def clear_done(self) -> int:
        remaining = [t for t in self.todos if not t.done]
        removed = len(self.todos) - len(remaining)
        self.todos = remaining
        return removed


def load(path: Path) -> TodoList:
    """Load todos from ``path``. A missing file means an empty list."""
    if not path.exists():
        return TodoList()
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise TodoError(f"{path} is not valid JSON: {exc}") from exc
    except OSError as exc:
        raise TodoError(f"cannot read {path}: {exc}") from exc
    return _from_dict(raw, path)


def save(todo_list: TodoList, path: Path) -> None:
    """Write todos to ``path`` atomically, so a crash never leaves a half-written file."""
    data = {
        "next_id": todo_list.next_id,
        "todos": [
            {"id": t.id, "title": t.title, "done": t.done} for t in todo_list.todos
        ],
    }
    tmp = path.with_name(path.name + ".tmp")
    try:
        tmp.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        os.replace(tmp, path)
    except OSError as exc:
        raise TodoError(f"cannot write {path}: {exc}") from exc


def _from_dict(raw: Any, path: Path) -> TodoList:
    if (
        not isinstance(raw, dict)
        or not isinstance(raw.get("todos"), list)
        or not isinstance(raw.get("next_id"), int)
    ):
        raise TodoError(f"{path} has an unexpected format")
    todos = []
    for entry in raw["todos"]:
        if not (
            isinstance(entry, dict)
            and isinstance(entry.get("id"), int)
            and isinstance(entry.get("title"), str)
            and isinstance(entry.get("done"), bool)
        ):
            raise TodoError(f"{path} contains an invalid todo: {entry!r}")
        todos.append(Todo(id=entry["id"], title=entry["title"], done=entry["done"]))
    return TodoList(todos=todos, next_id=raw["next_id"])


def format_todo(todo: Todo) -> str:
    marker = "x" if todo.done else "·"
    return f"[{todo.id}] [{marker}] {todo.title}"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="todo.py", description="Tiny todo manager.")
    sub = parser.add_subparsers(dest="command", required=True, metavar="command")

    add = sub.add_parser("add", help="add a new todo")
    add.add_argument("title", nargs="+", help="title (quotes optional)")

    sub.add_parser("list", help="list all todos")

    done = sub.add_parser("done", help="mark a todo as done")
    done.add_argument("id", type=int)

    rm = sub.add_parser("rm", help="delete a todo")
    rm.add_argument("id", type=int)

    sub.add_parser("clear", help="remove all done todos")
    return parser


def main(argv: list[str] | None = None, path: Path = DEFAULT_PATH) -> int:
    args = build_parser().parse_args(argv)
    try:
        todos = load(path)
        if args.command == "add":
            todo = todos.add(" ".join(args.title))
            save(todos, path)
            print(todo.id)
        elif args.command == "list":
            if not todos.todos:
                print("No todos.")
            for todo in todos.todos:
                print(format_todo(todo))
        elif args.command == "done":
            todo = todos.mark_done(args.id)
            save(todos, path)
            print(f"Marked {todo.id} as done.")
        elif args.command == "rm":
            todo = todos.remove(args.id)
            save(todos, path)
            print(f"Deleted {todo.id}.")
        elif args.command == "clear":
            removed = todos.clear_done()
            save(todos, path)
            print(f"Removed {removed} done todo(s).")
    except TodoError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
