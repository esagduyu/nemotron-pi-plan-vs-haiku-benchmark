# Tiny CLI Todo Manager

A minimal command-line todo app using only Python stdlib + pytest.

## Usage

```bash
# Add a todo
python todo.py add "Buy groceries"

# List all todos
python todo.py list

# Mark a todo done
python todo.py done 1

# Remove a todo
python todo.py rm 1

# Clear all completed todos
python todo.py clear
```

## Persistence

Todos are stored in `./todos.json` (created automatically on first add).

## Tests

```bash
pip install pytest
pytest tests/ -q
```
