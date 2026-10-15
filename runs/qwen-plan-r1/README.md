# Tiny CLI Todo Manager

A minimal command-line todo app built with Python stdlib only.

## Usage

```bash
# Add a todo
python todo.py add "Buy groceries"

# List all todos
python todo.py list

# Mark a todo as done
python todo.py done 1

# Remove a todo
python todo.py rm 1

# Remove all completed todos
python todo.py clear
```

## Options

- `--todos PATH` — Use a custom JSON file (default: `./todos.json`)

## Tests

```bash
pytest tests/
```

## File format

Todos are stored as a JSON array. Each todo has:
- `id` (int) — monotonically increasing, never reused
- `title` (str) — the todo text
- `done` (bool) — completion status
