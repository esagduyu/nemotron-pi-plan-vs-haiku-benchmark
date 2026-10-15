# TODO

## Goal
Build a tiny CLI todo manager in Python with argparse subcommands, JSON persistence, and pytest tests.

## Tasks

### 1. Project Setup
- [ ] Create `todo.py` with argparse subcommands (add, list, done, rm, clear)
- [ ] Set up `todos.json` persistence using JSON file at `./todos.json`
- [ ] Implement integer IDs that are monotonically increasing and never reused

### 2. Core Functionality
- [ ] Implement `add <title>` command — add new todo, print new ID
- [ ] Implement `list` command — print all todos as `[ID] [x|·] title`
- [ ] Implement `done <id>` command — mark todo done by ID
- [ ] Implement `rm <id>` command — delete todo by ID
- [ ] Implement `clear` command — remove all done todos

### 3. Error Handling
- [ ] Handle missing/invalid IDs — print clear error to stderr and exit non-zero
- [ ] Don't crash with stack trace on errors

### 4. Tests
- [ ] Create `tests/test_todo.py` with at least 4 pytest tests covering add, list, done, rm
- [ ] Use temp directory for JSON file during tests

### 5. Documentation
- [ ] Create `README.md` with brief usage examples

## Notes
- Language: Python 3.11+, stdlib only (except pytest for tests)
- No external runtime deps
- IDs monotonically increasing, never reused even after rm
- Tests should pass with `pytest tests/`