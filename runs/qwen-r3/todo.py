#!/usr/bin/env python3
"""A tiny CLI todo manager backed by a JSON file."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

TODOS_FILE = Path("todos.json")


def _load_todos(path: Path = TODOS_FILE) -> tuple[list[dict[str, Any]], int]:
    """Load todos and the next-seq counter from the JSON file."""
    if not path.exists():
        return [], 1
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        print(f"Error: could not parse {path}: {exc}", file=sys.stderr)
        sys.exit(1)
    if isinstance(raw, dict):
        # New format: {"todos": [...], "_next_seq": int}
        todos = raw.get("todos", [])
        next_seq = raw.get("_next_seq", max((t["id"] for t in todos), default=0) + 1)
        return todos, next_seq
    elif isinstance(raw, list):
        # Legacy format (plain list) — compute next_seq from existing IDs
        max_id = max((t["id"] for t in raw), default=0)
        return raw, max_id + 1
    else:
        print(f"Error: {path} has an unexpected JSON structure", file=sys.stderr)
        sys.exit(1)


def _save_todos(todos: list[dict[str, Any]], next_seq: int, path: Path = TODOS_FILE) -> None:
    """Persist todos to the JSON file with an embedded next-seq counter."""
    payload = {"todos": todos, "_next_seq": next_seq}
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _next_id(todos: list[dict[str, Any]], next_seq: int) -> int:
    """Return the next monotonically increasing ID."""
    return next_seq


def _find_todo(todos: list[dict[str, Any]], todo_id: int) -> dict[str, Any] | None:
    """Return the first todo with the given ID, or None."""
    for t in todos:
        if t["id"] == todo_id:
            return t
    return None


# ── command handlers ────────────────────────────────────────────────


def cmd_add(args: argparse.Namespace) -> None:
    todos, next_seq = _load_todos()
    todo: dict[str, Any] = {"id": next_seq, "title": args.title, "done": False}
    todos.append(todo)
    _save_todos(todos, next_seq + 1)
    print(f"Added todo #{todo['id']}: {todo['title']}")


def cmd_list(_args: argparse.Namespace) -> None:
    todos, _ = _load_todos()
    if not todos:
        print("(empty)")
        return
    for t in todos:
        status = "x" if t["done"] else "·"
        print(f"[{t['id']}] [{status}] {t['title']}")


def cmd_done(args: argparse.Namespace) -> None:
    todos, next_seq = _load_todos()
    todo = _find_todo(todos, args.id)
    if todo is None:
        print(f"Error: no todo with ID {args.id}", file=sys.stderr)
        sys.exit(1)
    todo["done"] = True
    _save_todos(todos, next_seq)
    print(f"Marked todo #{todo['id']} as done")


def cmd_rm(args: argparse.Namespace) -> None:
    todos, next_seq = _load_todos()
    todo = _find_todo(todos, args.id)
    if todo is None:
        print(f"Error: no todo with ID {args.id}", file=sys.stderr)
        sys.exit(1)
    todos.remove(todo)
    _save_todos(todos, next_seq)
    print(f"Removed todo #{todo['id']}")


def cmd_clear(_args: argparse.Namespace) -> None:
    todos, next_seq = _load_todos()
    before = len(todos)
    todos = [t for t in todos if not t["done"]]
    _save_todos(todos, next_seq)
    removed = before - len(todos)
    print(f"Cleared {removed} done todo(s)")


# ── CLI setup ───────────────────────────────────────────────────────


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="todo.py",
        description="Tiny command-line todo manager",
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
    handlers = {
        "add": cmd_add,
        "list": cmd_list,
        "done": cmd_done,
        "rm": cmd_rm,
        "clear": cmd_clear,
    }
    handlers[args.command](args)


if __name__ == "__main__":
    main()
