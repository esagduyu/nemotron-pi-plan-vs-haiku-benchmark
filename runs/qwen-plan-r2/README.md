# Tiny CLI Todo Manager

A minimal command-line todo app built with Python stdlib only.

## Usage

```bash
python todo.py add "Buy groceries"      # Add a todo
python todo.py list                     # List all todos
python todo.py done 1                   # Mark todo #1 as done
python todo.py rm 2                     # Delete todo #2
python todo.py clear                    # Remove all completed todos
```

## Output format

`[ID] [x|·] title` — `x` means done, `·` means open.

## Persistence

Todos are stored in `todos.json` in the current directory.

## Tests

```bash
pytest tests/
```
