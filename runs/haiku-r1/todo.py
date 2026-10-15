#!/usr/bin/env python3
"""Tiny command-line todo manager backed by a JSON file."""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path

DEFAULT_PATH = Path("todos.json")


class TodoError(Exception):
    """A user-facing error. Reported on stderr without a stack trace."""


@dataclass
class Todo:
    id: int
    title: str
    done: bool = False


class TodoStore:
    """Reads and writes todos to a JSON file.

    File layout: {"next_id": int, "todos": [{"id": int, "title": str, "done": bool}, ...]}.
    ``next_id`` is stored explicitly so IDs are never reused, even after deletion.
    """

    def __init__(self, path: Path = DEFAULT_PATH) -> None:
        self.path = path

    def add(self, title: str) -> int:
        title = title.strip()
        if not title:
            raise TodoError("title must not be empty")
        next_id, todos = self._load()
        todos.append(Todo(id=next_id, title=title))
        self._save(next_id + 1, todos)
        return next_id

    def list(self) -> list[Todo]:
        _, todos = self._load()
        return todos

    def done(self, todo_id: int) -> None:
        next_id, todos = self._load()
        todo = self._find(todos, todo_id)
        todo.done = True
        self._save(next_id, todos)

    def remove(self, todo_id: int) -> None:
        next_id, todos = self._load()
        todo = self._find(todos, todo_id)
        todos.remove(todo)
        self._save(next_id, todos)

    def clear(self) -> int:
        """Remove all done todos and return how many were removed."""
        next_id, todos = self._load()
        remaining = [t for t in todos if not t.done]
        removed = len(todos) - len(remaining)
        if removed:
            self._save(next_id, remaining)
        return removed

    @staticmethod
    def _find(todos: list[Todo], todo_id: int) -> Todo:
        for todo in todos:
            if todo.id == todo_id:
                return todo
        raise TodoError(f"no todo with id {todo_id}")

    def _load(self) -> tuple[int, list[Todo]]:
        if not self.path.exists():
            return 1, []
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise TodoError(f"cannot read {self.path}: {exc}") from exc
        return self._parse(raw)

    def _parse(self, raw: object) -> tuple[int, list[Todo]]:
        """Validate the decoded JSON and convert it to Python objects."""
        bad = TodoError(f"{self.path} has an invalid format")
        if not isinstance(raw, dict):
            raise bad
        next_id = raw.get("next_id")
        items = raw.get("todos")
        if not isinstance(next_id, int) or not isinstance(items, list):
            raise bad
        todos = []
        for item in items:
            if not isinstance(item, dict):
                raise bad
            todo_id, title, done = item.get("id"), item.get("title"), item.get("done")
            if not isinstance(todo_id, int) or not isinstance(title, str) or not isinstance(done, bool):
                raise bad
            todos.append(Todo(id=todo_id, title=title, done=done))
        return next_id, todos

    def _save(self, next_id: int, todos: list[Todo]) -> None:
        """Write atomically so a crash never leaves a half-written file."""
        data = {"next_id": next_id, "todos": [asdict(t) for t in todos]}
        try:
            fd, tmp_name = tempfile.mkstemp(dir=self.path.parent or ".", suffix=".tmp")
            with os.fdopen(fd, "w", encoding="utf-8") as tmp:
                json.dump(data, tmp, indent=2)
                tmp.write("\n")
            os.replace(tmp_name, self.path)
        except OSError as exc:
            raise TodoError(f"cannot write {self.path}: {exc}") from exc


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="todo.py", description="A tiny todo manager.")
    sub = parser.add_subparsers(dest="command", required=True, metavar="command")

    add = sub.add_parser("add", help="add a new todo")
    add.add_argument("title", help="text of the todo")

    sub.add_parser("list", help="list all todos")

    done = sub.add_parser("done", help="mark a todo as done")
    done.add_argument("id", type=int, help="ID of the todo")

    rm = sub.add_parser("rm", help="delete a todo")
    rm.add_argument("id", type=int, help="ID of the todo")

    sub.add_parser("clear", help="remove all done todos")
    return parser


def run(args: argparse.Namespace, store: TodoStore) -> None:
    if args.command == "add":
        print(store.add(args.title))
    elif args.command == "list":
        todos = store.list()
        if not todos:
            print("No todos.")
        for todo in todos:
            mark = "x" if todo.done else "·"
            print(f"[{todo.id}] [{mark}] {todo.title}")
    elif args.command == "done":
        store.done(args.id)
    elif args.command == "rm":
        store.remove(args.id)
    elif args.command == "clear":
        print(f"Removed {store.clear()} done todo(s).")


def main(argv: list[str] | None = None, path: Path = DEFAULT_PATH) -> int:
    args = build_parser().parse_args(argv)
    try:
        run(args, TodoStore(path))
    except TodoError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
