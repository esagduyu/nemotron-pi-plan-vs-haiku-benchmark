# Tiny CLI Todo Manager

A small command-line todo manager written in Python 3.11+ using only stdlib.

## Usage

```bash
# Add a new todo
python todo.py add "Buy groceries"

# List all todos
python todo.py list

# Mark a todo as done
python todo.py done 1

# Remove a todo
python todo.py rm 1

# Clear all done todos
python todo.py clear
```

## Arguments

| Command | Description |
|---------|-------------|
| `add <title>` | Add a new todo with the given title. Prints the new ID. |
| `list` | Print all todos as `[ID] [x·] title`. `x` = done, `·` = open. |
| `done <id>` | Mark a todo done by ID. |
| `rm <id>` | Delete a todo by ID. |
| `clear` | Remove all done todos. |

## Storage

- Data is stored in `./todos.json` (created automatically if missing).
- JSON schema: `{"next_id": int, "todos": [{"id": int, "title": str, "done": bool}, ...]}`.
- IDs are monotonically increasing and never reused, even after `rm`.
- `clear` does not reset `next_id`.

## Error Handling

- Missing or invalid IDs print `error: <message>` to stderr and exit with code 1.
- Non-integer IDs are rejected by argparse with exit code 2.
- Empty/whitespace-only titles are rejected with exit code 1.
- Corrupt `todos.json` is reported as an error (exit 1).

## Running Tests

```bash
pytest tests/
```

## Requirements

- Python 3.11+
- `pytest` for tests (dev dependency only)
- No other external runtime dependencies