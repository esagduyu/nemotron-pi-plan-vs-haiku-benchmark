# Tiny CLI Todo Manager

A minimal command-line todo app in Python (stdlib only).

## Usage

```bash
python todo.py add <title>      # Add a new todo
python todo.py list             # List all todos
python todo.py done <id>        # Mark a todo as done
python todo.py rm <id>          # Delete a todo
python todo.py clear            # Remove all done todos
```

## Persistence

Todos are stored in `todos.json` in the current directory.

## Tests

```bash
pytest tests/
```
