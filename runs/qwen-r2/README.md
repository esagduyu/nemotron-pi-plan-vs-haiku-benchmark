# Tiny CLI Todo Manager

A minimal command-line todo app — Python stdlib only, JSON-backed.

## Usage

```bash
python todo.py add <title>      # Add a new todo
python todo.py list             # List all todos
python todo.py done <id>        # Mark a todo as done
python todo.py rm <id>          # Remove a todo
python todo.py clear            # Remove all done todos
```

## Examples

```
$ python todo.py add "Buy groceries"
Added todo #1
$ python todo.py add "Walk the dog"
Added todo #2
$ python todo.py list
[1] [·] Buy groceries
[2] [·] Walk the dog
$ python todo.py done 1
Todo #1 marked done
$ python todo.py list
[1] [x] Buy groceries
[2] [·] Walk the dog
$ python todo.py rm 2
Todo #2 removed
$ python todo.py clear
Cleared 1 done todo(s)
```

## Tests

```bash
pytest tests/ -q
```
