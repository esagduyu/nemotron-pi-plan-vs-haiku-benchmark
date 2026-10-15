# TODO

## Goal
Build a small CLI todo manager in Python with argparse subcommands, JSON persistence, and pytest tests.

## Tasks

### 1. Implement core todo.py
- [ ] Create `todo.py` with argparse subcommands: add, list, done, rm, clear
- [ ] Implement JSON persistence (load/save `todos.json`)
- [ ] Implement `add <title>` — prints new ID, monotonically increasing
- [ ] Implement `list` — prints `[ID] [x|·] title`
- [ ] Implement `done <id>` — marks todo done by ID
- [ ] Implement `rm <id>` — deletes todo by ID, never reuses IDs
- [ ] Implement `clear` — removes all done todos
- [ ] Add error handling: invalid/missing IDs print to stderr and exit non-zero

### 2. Write tests
- [ ] Create `tests/__init__.py`
- [ ] Create `tests/test_todo.py` with at least 4 pytest tests (add, list, done, rm)
- [ ] Use `tempfile.TemporaryDirectory` to isolate JSON file during tests
- [ ] Verify tests pass with `pytest tests/`

### 3. Documentation
- [ ] Create `README.md` with brief usage examples

## Notes
- Python 3.11+, stdlib only (except pytest for tests)
- Single file (`todo.py`) for simplicity
- `todos.json` stored in working directory
- IDs are monotonically increasing and never reused
- All errors go to stderr with `sys.exit(1)`, no stack traces
