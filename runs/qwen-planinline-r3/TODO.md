# TODO

## Goal
Build a tiny CLI todo manager in Python (stdlib only) with subcommands for add, list, done, rm, and clear, persisted to a JSON file, plus pytest tests and a README.

## Tasks

### 1. Project scaffolding
- [x] Create `todo.py` (entry point with argparse subcommands: add, list, done, rm, clear)
- [x] Create `todos.json` loader/saver helper functions (read/write JSON, handle missing file)
- [x] Implement todo schema: dict with `id` (int), `title` (str), `done` (bool); IDs are monotonically increasing, never reused

### 2. CLI commands
- [x] Implement `add <title>` — appends a todo, prints the new ID
- [x] Implement `list` — prints all todos as `[ID] [x|·] title`
- [x] Implement `done <id>` — marks a todo done by ID; error if ID not found
- [x] Implement `rm <id>` — deletes a todo by ID; error if ID not found
- [x] Implement `clear` — removes all done todos
- [x] Ensure all errors print to stderr and exit with non-zero code (no stack traces)

### 3. Tests
- [x] Create `tests/__init__.py`
- [x] Create `tests/test_todo.py` with at least 4 pytest tests covering add, list, done, rm
- [x] Use a temporary directory for the JSON file in tests (no cwd pollution)
- [x] Verify tests pass with `pytest tests/`

### 4. Documentation
- [x] Create `README.md` with brief description and usage examples for all subcommands

## Notes
- Python 3.11+, stdlib only (except pytest for tests).
- Single-file approach for `todo.py` is acceptable; splitting into modules is also fine.
- `todos.json` stored in the working directory where the script is run.
- Error messages should be clear and user-friendly, not raw Python tracebacks.
