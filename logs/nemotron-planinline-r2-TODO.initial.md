# TODO

## Goal
Build a small command-line todo app at the working directory using Python 3.11+ stdlib only (except pytest for tests), following the functional requirements and layout from SPEC.md.

## Tasks

### 1. Project Setup
- [ ] Create `todo.py` with argparse subcommands (add, list, done, rm, clear)
- [ ] Set up `todos.json` persistence at `./todos.json`
- [ ] Implement monotonically increasing IDs that are never reused

### 2. Core Functionality
- [ ] Implement `add <title>` command — add new todo, print new ID
- [ ] Implement `list` command — print all todos as `[ID] [x|·] title`. `x` = done, `·` = open.
- [ ] Implement `done <id>` command — mark a todo done by ID
- [ ] Implement `rm <id>` command — delete a todo by ID
- [ ] Implement `clear` command — remove all done todos

### 3. Error Handling
- [ ] Missing/invalid IDs should print clear error to stderr and exit non-zero
- [ ] Don't crash with a stack trace on errors

### 4. Tests
- [ ] Create `tests/test_todo.py` with at least 4 pytest tests covering add, list, done, rm
- [ ] Use a temp directory for the JSON file during tests (don't pollute cwd)
- [ ] Ensure tests pass with `pytest tests/`

### 5. Documentation
- [ ] Create `README.md` with brief description and usage examples

## Notes
- Language: Python 3.11+, stdlib only (except pytest for tests)
- No external runtime deps
- IDs must be monotonically increasing — never reused even after rm
- Tests should pass with pytest
- Code should be readable — type hints encouraged but not required