# Tiny CLI Todo Manager

A minimal command-line todo app — Python stdlib only, JSON persistence.

## Usage

```bash
python todo.py add "Buy groceries"       # → Added todo #1: Buy groceries
python todo.py list                       # → [1] [·] Buy groceries
python todo.py done 1                     # → Marked todo #1 as done
python todo.py list                       # → [1] [x] Buy groceries
python todo.py rm 1                       # → Removed todo #1
python todo.py clear                      # → Clear all done todos
```

## Persistence

Todos are stored in `./todos.json` (created on first `add`).

## Tests

```bash
pytest tests/ -q
```
