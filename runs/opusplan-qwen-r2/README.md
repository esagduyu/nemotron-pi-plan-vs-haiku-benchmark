# Tiny CLI Todo Manager

A small command-line todo app — Python 3.11+, stdlib only.

## Requirements

- Python 3.11 or later
- No external dependencies (pytest is only needed for tests)

## Usage

```bash
# Add a new todo
python todo.py add "Buy milk"

# List all todos
python todo.py list

# Mark a todo as done
python todo.py done 1

# Remove a todo
python todo.py rm 1

# Remove all done todos
python todo.py clear
```

## Store

Todos are persisted in `./todos.json` (JSON format). Set the `TODO_FILE` environment variable to use a different path.

## Running Tests

```bash
pytest tests/
```
