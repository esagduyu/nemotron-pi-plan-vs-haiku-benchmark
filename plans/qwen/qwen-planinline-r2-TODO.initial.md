# TODO

## Goal
Build a small command-line todo manager in Python with argparse subcommands, JSON persistence, and pytest tests.

## Tasks

### 1. Core module — `todo.py`
- [ ] Implement `add <title>`: reads todos.json (or creates it), appends a new todo with monotonically increasing ID, prints the new ID
- [ ] Implement `list`: reads todos.json, prints each todo as `[ID] [x|·] title`
- [ ] Implement `done <id>`: marks a todo by ID as done; prints error to stderr and exits non-zero if ID not found
- [ ] Implement `rm <id>`: deletes a todo by ID; prints error to stderr and exits non-zero if ID not found
- [ ] Implement `clear`: removes all done todos from todos.json
- [ ] Add argparse CLI with subcommands (add, list, done, rm, clear) and entry point
- [ ] Ensure JSON schema: each todo has integer `id`, string `title`, boolean `done`
- [ ] Ensure IDs are monotonically increasing and never reused
- [ ] Handle missing/invalid todos.json gracefully (treat as empty list)

### 2. Tests — `tests/test_todo.py`
- [ ] Write test for `add`: verify a todo is created with correct ID and title
- [ ] Write test for `list`: verify output format `[ID] [x|·] title`
- [ ] Write test for `done`: verify a todo is marked done by ID
- [ ] Write test for `rm`: verify a todo is deleted by ID
- [ ] Use a temp directory for the JSON file so tests don't pollute cwd
- [ ] Verify error cases: invalid ID prints to stderr and exits non-zero

### 3. README.md
- [ ] Write brief README with project description, usage examples for all subcommands

### 4. Verification
- [ ] Run `pytest tests/` and confirm all tests pass
- [ ] Manually verify CLI commands work end-to-end

## Notes
- Python 3.11+, stdlib only (except pytest for tests)
- JSON persistence at `./todos.json`
- No external runtime dependencies
- No silent failures — all errors go to stderr with non-zero exit
- Monotonically increasing IDs, never reused after deletion
