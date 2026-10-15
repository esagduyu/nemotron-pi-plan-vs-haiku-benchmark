# Tiny CLI Todo Manager

A small command-line todo manager built with Python 3.11+ stdlib only.

## Usage

```bash
# Add a new todo
python todo.py add "Buy milk"

# List all todos
python todo.py list

# Mark a todo done
python todo.py done 1

# Remove a todo
python todo.py rm 1

# Remove all done todos
python todo.py clear
```

## Persistence

Todos are saved to `todos.json` in the current directory.

## ID Management

IDs are monotonically increasing and never reused, even after removal.