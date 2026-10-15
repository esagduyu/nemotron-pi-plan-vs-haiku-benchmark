#!/usr/bin/env python3
"""Tiny CLI todo manager — stdlib only."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

DATA_FILE = Path("todos.json")

_SENTRY_KEY = "__next_id__"


# ── persistence ──────────────────────────────────────────────────────────────

def _load() -> tuple[list[dict[str, Any]], int]:
    """Load todos and the next-usable ID.

    Returns ``(todos, next_id)`` where ``next_id`` is never reused.
    """
    if not DATA_FILE.exists():
        return [], 1
    raw = DATA_FILE.read_text(encoding="utf-8")
    data = json.loads(raw)
    if not isinstance(data, list):
        raise ValueError("todos.json has unexpected shape")

    # Separate real todos from the sentinel entry.
    todos: list[dict[str, Any]] = []
    next_id = 1
    for entry in data:
        if entry.get("title") == _SENTRY_KEY:
            next_id = entry["id"]
        else:
            todos.append(entry)
    return todos, next_id


def _save(todos: list[dict[str, Any]], next_id: int) -> None:
    sentinel: dict[str, Any] = {"id": next_id, "title": _SENTRY_KEY, "done": True}
    DATA_FILE.write_text(
        json.dumps(todos + [sentinel], indent=2) + "\n", encoding="utf-8"
    )


def _find_todo(todos: list[dict[str, Any]], todo_id: int) -> dict[str, Any]:
    """Return the todo dict with the given ID, or raise ValueError."""
    for t in todos:
        if t["id"] == todo_id:
            return t
    raise ValueError(f"Todo with ID {todo_id} not found")


# ── commands ─────────────────────────────────────────────────────────────────

def cmd_add(args: argparse.Namespace) -> None:
    todos, next_id = _load()
    todo: dict[str, Any] = {"id": next_id, "title": args.title, "done": False}
    todos.append(todo)
    _save(todos, next_id + 1)
    print(f"Added todo #{todo['id']}: {todo['title']}")


def cmd_list(args: argparse.Namespace) -> None:
    todos, _ = _load()
    if not todos:
        print("(none)")
        return
    for t in todos:
        status = "x" if t["done"] else "·"
        print(f"[{t['id']}] [{status}] {t['title']}")


def cmd_done(args: argparse.Namespace) -> None:
    todos, next_id = _load()
    todo = _find_todo(todos, args.id)
    todo["done"] = True
    _save(todos, next_id)
    print(f"Marked todo #{todo['id']} as done")


def cmd_rm(args: argparse.Namespace) -> None:
    todos, next_id = _load()
    todo = _find_todo(todos, args.id)
    todos.remove(todo)
    _save(todos, next_id)
    print(f"Removed todo #{todo['id']}")


def cmd_clear(args: argparse.Namespace) -> None:
    todos, next_id = _load()
    before = len(todos)
    todos = [t for t in todos if not t["done"]]
    _save(todos, next_id)
    removed = before - len(todos)
    print(f"Cleared {removed} done todo(s)")


# ── CLI ──────────────────────────────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="todo",
        description="Tiny CLI todo manager",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("add", help="Add a new todo").add_argument("title", type=str)

    sub.add_parser("list", help="List all todos")

    done_p = sub.add_parser("done", help="Mark a todo as done")
    done_p.add_argument("id", type=int)

    rm_p = sub.add_parser("rm", help="Remove a todo")
    rm_p.add_argument("id", type=int)

    sub.add_parser("clear", help="Remove all done todos")

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    try:
        match args.command:
            case "add":
                cmd_add(args)
            case "list":
                cmd_list(args)
            case "done":
                cmd_done(args)
            case "rm":
                cmd_rm(args)
            case "clear":
                cmd_clear(args)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
