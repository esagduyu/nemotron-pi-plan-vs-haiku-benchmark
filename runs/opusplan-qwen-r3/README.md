# Tiny CLI Todo Manager

A minimal, stdlib-only Python CLI todo manager with JSON persistence.

## Requirements

- Python 3.11+
- No external dependencies (stdlib only)
- `pytest` for running tests

## Usage

```bash
# Add a todo
python todo.py add "Buy milk"
# → 1

# List all todos
python todo.py list
# → [1] [·] Buy milk

# Mark a todo as done
python todo.py done 1
# → marked todo 1 done

# Remove a todo
python todo.py rm 1
# → removed todo 1

# Clear all done todos
python todo.py clear
# → cleared all done todos
```

## Storage

Todos are persisted in `todos.json` in the current working directory.

Schema:
```json
{
  "next_id": 2,
  "todos": [
    {"id": 1, "title": "Buy milk", "done": true}
  ]
}
```

- IDs are monotonically increasing and never reused.
- Writes are atomic (temp file + `os.replace`).

## Running tests

```bash
pytest tests/ -q
```
