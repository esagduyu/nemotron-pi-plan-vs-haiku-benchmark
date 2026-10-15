# TODO

## Goal
Build a small command-line todo manager in Python 3.11+ using only stdlib (except pytest for tests), with argparse subcommands for add/list/done/rm/clear, JSON persistence at ./todos.json, monotonically increasing IDs, and proper error handling.

## Tasks

### 1. Project Setup and Base Structure
- [x] Create `todo.py` entry point with argparse subcommands (add, list, done, rm, clear)
- [x] Set up `todos.json` persistence with monotonically increasing IDs
- [x] Implement ID management that never reuses IDs even after rm

### 2. add Command
- [x] Implement `add <title>` command that adds a new todo and prints the new ID
- [x] Ensure todo is persisted to todos.json

### 3. list Command
- [x] Implement `list` command that prints all todos as `[ID] [x|·] title`
- [x] `x` = done, `·` = open

### 4. done Command
- [x] Implement `done <id>` command that marks a todo done by ID
- [x] Print clear error to stderr and exit non-zero for missing/invalid IDs

### 5. rm Command
- [x] Implement `rm <id>` command that deletes a todo by ID
- [x] Print clear error to stderr and exit non-zero for missing/invalid IDs

### 6. clear Command
- [x] Implement `clear` command that removes all done todos

### 7. Tests
- [x] Create `tests/test_todo.py` with at least 4 pytest tests covering add, list, done, rm
- [x] Use temp directory for JSON file in tests

### 8. README.md
- [x] Create brief README.md with usage examples

## Notes
- No external runtime deps
- No silent failures
- Tests should pass with `pytest tests/`
- Type hints encouraged but not required