# TODO

## Goal
Build a small command-line todo manager in Python with JSON persistence, CLI subcommands (add, list, done, rm, clear), and pytest tests.

## Tasks

### 1. Project scaffolding
- [ ] Create `todo.py` entry-point file with argparse subcommands (add, list, done, rm, clear)
- [ ] Create `tests/` directory and `tests/__init__.py`
- [ ] Create `README.md` with brief usage examples

### 2. Core logic
- [ ] Implement `load_todos()` and `save_todos()` for JSON persistence at `./todos.json`
- [ ] Implement `add_todo(title)` — creates todo with monotonically increasing ID, prints new ID
- [ ] Implement `list_todos()` — prints all todos as `[ID] [x|·] title`
- [ ] Implement `done_todo(id)` — marks a todo done by ID, errors on missing/invalid ID
- [ ] Implement `rm_todo(id)` — deletes a todo by ID, errors on missing/invalid ID
- [ ] Implement `clear_todos()` — removes all done todos

### 3. Error handling
- [ ] Ensure invalid/missing IDs print clear error to stderr and exit non-zero (no stack traces)

### 4. Tests
- [ ] Write pytest tests in `tests/test_todo.py` covering add, list, done, rm (≥4 tests)
- [ ] Use temp directory for JSON file during tests (no cwd pollution)

### 5. Verification
- [ ] Run `pytest tests/` and confirm all tests pass

## Notes
- Python 3.11+, stdlib only (except pytest for tests).
- IDs are monotonically increasing and never reused.
- JSON schema: `{id: int, title: str, done: bool}`.
- CLI entry: `python todo.py <command> [args]`.
