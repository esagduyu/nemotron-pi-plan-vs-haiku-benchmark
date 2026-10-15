# TODO

## Goal
Build a tiny CLI todo manager in Python (stdlib only) with subcommands for add, list, done, rm, and clear, persisted to a JSON file, plus pytest tests and a README.

## Tasks

### 1. Project scaffolding
- [ ] Create `todo.py` (entry point with argparse subcommands: add, list, done, rm, clear)
- [ ] Create `todos.json` loader/saver helper functions (read/write JSON, handle missing file)
- [ ] Implement todo schema: dict with `id` (int), `title` (str), `done` (bool); IDs are monotonically increasing, never reused

### 2. CLI commands
- [ ] Implement `add <title>` — appends a todo, prints the new ID
- [ ] Implement `list` — prints all todos as `[ID] [x|·] title`
- [ ] Implement `done <id>` — marks a todo done by ID; error if ID not found
- [ ] Implement `rm <id>` — deletes a todo by ID; error if ID not found
- [ ] Implement `clear` — removes all done todos
- [ ] Ensure all errors print to stderr and exit with non-zero code (no stack traces)

### 3. Tests
- [ ] Create `tests/__init__.py`
- [ ] Create `tests/test_todo.py` with at least 4 pytest tests covering add, list, done, rm
- [ ] Use a temporary directory for the JSON file in tests (no cwd pollution)
- [ ] Verify tests pass with `pytest tests/`

### 4. Documentation
- [ ] Create `README.md` with brief description and usage examples for all subcommands

## Notes
- Python 3.11+, stdlib only (except pytest for tests).
- Single-file approach for `todo.py` is acceptable; splitting into modules is also fine.
- `todos.json` stored in the working directory where the script is run.
- Error messages should be clear and user-friendly, not raw Python tracebacks.
