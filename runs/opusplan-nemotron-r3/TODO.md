# TODO

## Goal
Build a stdlib-only Python CLI todo manager (`todo.py`) with JSON persistence, pytest tests, and a README, per SPEC.md.

## Tasks

### 1. Storage layer (in `todo.py`)
- [ ] Define file format: `{"next_id": int, "todos": [{"id": int, "title": str, "done": bool}, ...]}` so IDs are never reused after `rm`
- [ ] Implement `load(path) -> dict`: return empty store `{"next_id": 1, "todos": []}` if the file is missing; raise a clear error on unreadable/invalid JSON
- [ ] Implement `save(path, data)`: write atomically (temp file + `os.replace`) to avoid corrupting `todos.json`
- [ ] Resolve the data path as `./todos.json` relative to the current working directory at call time (not import time)

### 2. Commands (in `todo.py`)
- [ ] `add <title>`: reject empty/whitespace-only titles; append todo with `next_id`, increment `next_id`, save, print the new ID
- [ ] `list`: print each todo as `[ID] [x|·] title`; print nothing when empty
- [ ] `done <id>`: mark the todo done; error if ID not found
- [ ] `rm <id>`: delete the todo; error if ID not found (`next_id` unchanged)
- [ ] `clear`: remove all done todos (leave `next_id` unchanged)

### 3. CLI & error handling (in `todo.py`)
- [ ] Build `argparse` parser with the five subcommands; `id` arguments parsed as `int` (argparse rejects non-integers with exit code 2 and a stderr message)
- [ ] Expose `main(argv: list[str] | None = None) -> int` and call it via `if __name__ == "__main__": sys.exit(main())`
- [ ] Define a `TodoError` exception; `main` catches it (and `OSError`/JSON errors), prints `error: <message>` to stderr, returns exit code 1 — no stack traces

### 4. Tests (`tests/test_todo.py`)
- [ ] Fixture using `tmp_path` + `monkeypatch.chdir` so `todos.json` lives in a temp dir
- [ ] Test `add` prints the ID and persists the todo
- [ ] Test `list` output format for open and done todos
- [ ] Test `done` marks a todo done; unknown ID exits non-zero with stderr message
- [ ] Test `rm` removes a todo and IDs are not reused after `rm`
- [ ] Test `clear` removes only done todos
- [ ] Test invalid (non-integer) ID exits non-zero without a traceback
- [ ] Run `pytest tests/` and confirm all tests pass

### 5. Documentation
- [ ] Write `README.md` with requirements, usage examples for every command, storage notes, and how to run tests

## Notes
- Assumptions (Phase 2 questions skipped per instructions):
  - Single-file implementation (`todo.py`) — the app is small enough that splitting adds no value.
  - Storing `next_id` in the JSON file is how "never reused" IDs are guaranteed; `clear` also does not reset it.
  - `done` on an already-done todo is a no-op success (idempotent), not an error.
  - `clear` with nothing to clear succeeds silently; `add`/`done`/`rm`/`clear` print a short confirmation (`add` prints only the ID, as specified).
  - Corrupt `todos.json` is reported as an error (exit 1), never silently overwritten.
- Tests call `main(argv)` in-process and use `capsys` for output; one test runs `todo.py` via `subprocess` to verify no traceback on bad input.
- No external runtime dependencies; `pytest` is the only dev dependency.
