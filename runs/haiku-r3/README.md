# todo

A tiny command-line todo manager. Standard library only, Python 3.11+.

Todos are stored in `./todos.json` in the current directory (created on first write).

## Usage

```sh
python todo.py add "buy milk"     # prints the new ID, e.g. 1
python todo.py add "write tests"  # 2
python todo.py list
# [1] [·] buy milk
# [2] [·] write tests

python todo.py done 1
python todo.py list
# [1] [x] buy milk
# [2] [·] write tests

python todo.py rm 2               # delete a todo
python todo.py clear              # remove all done todos
```

IDs only ever increase. Deleting a todo never frees its ID for reuse.

Use `--file` to store todos somewhere else:

```sh
python todo.py --file ~/work-todos.json list
```

Errors (unknown ID, empty title, unreadable file) print to stderr and exit with status 1.

## Tests

```sh
pip install pytest
pytest tests/ -q
```

The tests write to a temporary directory and never touch `./todos.json`.
