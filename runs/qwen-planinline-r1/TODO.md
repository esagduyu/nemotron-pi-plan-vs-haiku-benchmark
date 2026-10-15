# TODO

## Goal
Build a small command-line todo manager in Python with JSON persistence, CLI subcommands (add, list, done, rm, clear), and pytest tests.

## Tasks

### 1. Project scaffolding
- [x] Create `todo.py` entry-point file with argparse subcommands (add, list, done, rm, clear)
- [x] Create `tests/` directory and `tests/__init__.py`
- [x] Create `README.md` with brief usage examples

### 2. Core logic
- [x] Implement `load_todos()` and `save_todos()` for JSON persistence at `./todos.json`
- [x] Implement `add_todo(title)` — creates todo with monotonically increasing ID, prints new ID
- [x] Implement `list_todos()` — prints all todos as `[ID] [x|·] title`
- [x] Implement `done_todo(id)` — marks a todo done by ID, errors on missing/invalid ID
- [x] Implement `rm_todo(id)` — deletes a todo by ID, errors on missing/invalid ID
- [x] Implement `clear_todos()` — removes all done todos

### 3. Error handling
- [x] Ensure invalid/missing IDs print clear error to stderr and exit non-zero (no stack traces)

### 4. Tests
- [x] Write pytest tests in `tests/test_todo.py` covering add, list, done, rm (≥4 tests)
- [x] Use temp directory for JSON file during tests (no cwd pollution)

### 5. Verification
- [x] Run `pytest tests/` and confirm all tests pass

## Notes
- Python 3.11+, stdlib only (except pytest for tests).
- IDs are monotonically increasing and never reused.
- JSON schema: `{id: int, title: str, done: bool}`.
- CLI entry: `python todo.py <command> [args]`.
