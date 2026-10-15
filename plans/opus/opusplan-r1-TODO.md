# TODO

## Goal
Build a stdlib-only Python CLI todo manager (`python todo.py <command>`) with JSON persistence, never-reused IDs, clean error handling, pytest coverage, and a README, per SPEC.md.

## Tasks

### 1. Storage layer (`todo.py`)
- [ ] Define the on-disk format: `{"next_id": int, "todos": [{"id": int, "title": str, "done": bool}, ...]}`
- [ ] Implement `load(path) -> dict` that returns an empty store (`next_id: 1, todos: []`) when the file is missing
- [ ] Make `load` raise a `TodoError` with a clear message when the file is unreadable, not valid JSON, or has the wrong shape
- [ ] Implement `save(path, data)` that writes to a temp file in the same directory and atomically replaces `todos.json`

### 2. Core operations (`todo.py`, pure functions on the store)
- [ ] `add_todo(data, title) -> int`: reject empty/whitespace-only titles, assign `next_id`, increment `next_id`, return the new ID
- [ ] `find_todo(data, id)`: raise `TodoError("no todo with id N")` when the ID is missing
- [ ] `mark_done(data, id)`: set `done = True` (idempotent if already done)
- [ ] `remove_todo(data, id)`: delete the todo without touching `next_id`
- [ ] `clear_done(data) -> int`: remove all done todos and return how many were removed
- [ ] `format_todo(todo) -> str`: return `[ID] [x] title` or `[ID] [·] title`

### 3. CLI (`todo.py`)
- [ ] Build an `argparse` parser with subcommands `add <title>`, `list`, `done <id>`, `rm <id>`, `clear`
- [ ] Parse `<id>` with a custom type that rejects non-integer / non-positive values with a clear message (argparse exits 2 on stderr)
- [ ] `main(argv=None) -> int`: dispatch to the operation, print results (`add` prints the new ID; `list` prints one line per todo, or nothing when empty), save only on mutating commands
- [ ] Catch `TodoError` in `main`, print `error: <message>` to stderr, return exit code 1 (no stack traces)
- [ ] Add `if __name__ == "__main__": sys.exit(main())`; force UTF-8 stdout so `·` prints on any locale

### 4. Tests (`tests/test_todo.py`)
- [ ] Add a fixture that `chdir`s into pytest's `tmp_path` (via `monkeypatch.chdir`) so `./todos.json` lands in a temp dir
- [ ] Test `add`: prints ID 1 then 2 and persists both todos to `todos.json`
- [ ] Test `list`: output matches `[1] [·] a` / `[2] [x] b` format
- [ ] Test `done`: marks the todo done in the file; `done` on a missing ID exits non-zero with a stderr message
- [ ] Test `rm`: removes the todo; a subsequent `add` gets a new, higher ID (no reuse); `rm` on a missing ID exits non-zero
- [ ] Test `clear`: removes only done todos
- [ ] Test invalid ID (`done abc`) and corrupt `todos.json` both exit non-zero without a traceback (one subprocess test to confirm no traceback end to end)
- [ ] Run `pytest tests/` and confirm all tests pass

### 5. Documentation
- [ ] Write `README.md`: requirements (Python 3.11+), usage examples for each command with sample output, the JSON file location/format, and how to run the tests

## Notes
- **Assumptions (Phase 2 skipped):**
  - Single-file implementation (`todo.py`) — the app is small enough that splitting adds no value.
  - IDs are kept monotonic by storing `next_id` in the JSON alongside the `todos` list (the spec's per-todo schema is kept as is inside the list).
  - `todos.json` is resolved relative to the current working directory, as the spec says `./todos.json`.
  - Empty titles are an error. Marking an already-done todo done again succeeds silently.
  - `list` with no todos prints nothing and exits 0.
  - Exit codes: 0 on success, 1 for runtime errors (missing ID, corrupt file), 2 for argparse usage errors.
- **Tests** mostly call `main([...])` in-process with `capsys`, plus one subprocess test for the no-traceback guarantee.
- **Risk:** the `·` character on non-UTF-8 terminals is handled by reconfiguring stdout to UTF-8.
- No dependencies besides `pytest` (test-only); no `requirements.txt` beyond a note in the README.
