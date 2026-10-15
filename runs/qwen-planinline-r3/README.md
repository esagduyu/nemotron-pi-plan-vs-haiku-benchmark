# Tiny CLI Todo Manager

A minimal command-line todo app built with Python 3.11+ (stdlib only).

## Usage

```bash
python todo.py add "Buy milk"        # Add a todo → prints new ID
python todo.py list                   # List all todos: [ID] [x|·] title
python todo.py done 1                 # Mark todo #1 as done
python todo.py rm 2                   # Delete todo #2
python todo.py clear                  # Remove all completed todos
```

## Storage

Todos are persisted in `todos.json` in the current working directory.

## Running Tests

```bash
pytest tests/
```
