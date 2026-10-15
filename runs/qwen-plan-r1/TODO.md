# TODO

## Goal
Build a tiny CLI todo manager in Python (stdlib only) with argparse subcommands, JSON persistence, and pytest tests.

## Tasks

### 1. Scaffold project structure
- [x] Create `tests/` directory with `__init__.py`
- [x] Create `todo.py` entry point with argparse subcommand setup (`add`, `list`, `done`, `rm`, `clear`)

### 2. Implement persistence layer
- [x] Implement `load_todos(path)` — reads `todos.json`, returns list of dicts (returns `[]` if file missing)
- [x] Implement `save_todos(path, todos)` — writes todos to `todos.json`
- [x] Use `./todos.json` as the default persistence path

### 3. Implement CLI commands
- [x] `add <title>` — append a new todo with auto-incrementing ID, save, print the new ID to stdout
- [x] `list` — print all todos as `[ID] [x|·] title` (x=done, ·=open)
- [x] `done <id>` — find todo by ID, set `done=True`, save, print confirmation or error if not found
- [x] `rm <id>` — delete todo by ID, save, print confirmation or error if not found
- [x] `clear` — remove all done todos, save, print count of removed items

### 4. Implement error handling
- [x] Invalid/missing IDs: print clear error to stderr, `sys.exit(1)`
- [x] Invalid JSON in `todos.json`: print clear error to stderr, `sys.exit(1)`
- [x] No bare stack traces — all exceptions caught and reported gracefully

### 5. Write tests
- [x] `tests/test_todo.py` — test `add` command (verify ID returned and persisted)
- [x] `tests/test_todo.py` — test `list` command (verify output format)
- [x] `tests/test_todo.py` — test `done` command (verify done flag toggled)
- [x] `tests/test_todo.py` — test `rm` command (verify todo removed)
- [x] All tests use `tempfile.TemporaryDirectory` to isolate `todos.json`

### 6. Write README.md
- [x] Brief description of the project
- [x] Usage examples for all 5 commands
- [x] Notes on running tests (`pytest tests/`)

### 7. Verify everything works
- [x] Run `pytest tests/` — all tests pass
- [x] Manually test each command end-to-end
- [x] Verify error cases produce stderr output and non-zero exit codes

## Notes
- Python 3.11+, stdlib only (json, argparse, sys, os, tempfile).
- IDs are monotonically increasing integers, never reused.
- Each todo has: `id` (int), `title` (str), `done` (bool).
- One-file layout: `todo.py` handles everything; `tests/test_todo.py` for tests.
