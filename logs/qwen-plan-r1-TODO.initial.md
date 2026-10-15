# TODO

## Goal
Build a tiny CLI todo manager in Python (stdlib only) with argparse subcommands, JSON persistence, and pytest tests.

## Tasks

### 1. Scaffold project structure
- [ ] Create `tests/` directory with `__init__.py`
- [ ] Create `todo.py` entry point with argparse subcommand setup (`add`, `list`, `done`, `rm`, `clear`)

### 2. Implement persistence layer
- [ ] Implement `load_todos(path)` — reads `todos.json`, returns list of dicts (returns `[]` if file missing)
- [ ] Implement `save_todos(path, todos)` — writes todos to `todos.json`
- [ ] Use `./todos.json` as the default persistence path

### 3. Implement CLI commands
- [ ] `add <title>` — append a new todo with auto-incrementing ID, save, print the new ID to stdout
- [ ] `list` — print all todos as `[ID] [x|·] title` (x=done, ·=open)
- [ ] `done <id>` — find todo by ID, set `done=True`, save, print confirmation or error if not found
- [ ] `rm <id>` — delete todo by ID, save, print confirmation or error if not found
- [ ] `clear` — remove all done todos, save, print count of removed items

### 4. Implement error handling
- [ ] Invalid/missing IDs: print clear error to stderr, `sys.exit(1)`
- [ ] Invalid JSON in `todos.json`: print clear error to stderr, `sys.exit(1)`
- [ ] No bare stack traces — all exceptions caught and reported gracefully

### 5. Write tests
- [ ] `tests/test_todo.py` — test `add` command (verify ID returned and persisted)
- [ ] `tests/test_todo.py` — test `list` command (verify output format)
- [ ] `tests/test_todo.py` — test `done` command (verify done flag toggled)
- [ ] `tests/test_todo.py` — test `rm` command (verify todo removed)
- [ ] All tests use `tempfile.TemporaryDirectory` to isolate `todos.json`

### 6. Write README.md
- [ ] Brief description of the project
- [ ] Usage examples for all 5 commands
- [ ] Notes on running tests (`pytest tests/`)

### 7. Verify everything works
- [ ] Run `pytest tests/` — all tests pass
- [ ] Manually test each command end-to-end
- [ ] Verify error cases produce stderr output and non-zero exit codes

## Notes
- Python 3.11+, stdlib only (json, argparse, sys, os, tempfile).
- IDs are monotonically increasing integers, never reused.
- Each todo has: `id` (int), `title` (str), `done` (bool).
- One-file layout: `todo.py` handles everything; `tests/test_todo.py` for tests.
