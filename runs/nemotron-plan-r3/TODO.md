# Plan: Tiny CLI Todo Manager

## Overview
Build a small command-line todo app using Python 3.11+ stdlib only (except pytest for tests).

## Status: Complete

All features implemented and all 5 pytest tests passing.

## Features
- `add <title>` — add new todo, print new ID
- `list` — print all todos as `[ID] [x|·] title`. `x` = done, `·` = open.
- `done <id>` — mark a todo done by ID.
- `rm <id>` — delete a todo by ID.
- `clear` — remove all done todos.

## Technical Details
- Language: Python 3.11+, stdlib only (except pytest for tests).
- CLI: argparse with subcommands; entry: `python todo.py <command> [args]`.
- Persistence: JSON file at `./todos.json` (created if missing).
- Schema: each todo has integer `id`, string `title`, boolean `done`.
- IDs: monotonically increasing — never reused even after `rm`.
- Errors: missing/invalid IDs print clear error to stderr and exit non-zero. No stack traces.
- Tests: 5 pytest tests in `tests/test_todo.py` covering add, list, done, rm, clear. Use a temp directory for the JSON file (don't pollute the cwd during tests).
- README.md: brief, with usage examples.

## Layout
One file (`todo.py`) with tests in `tests/test_todo.py`.

## Quality bar
- No external runtime deps.
- No silent failures.
- Tests pass with `pytest tests/`.
- Code is readable — type hints encouraged but not required.