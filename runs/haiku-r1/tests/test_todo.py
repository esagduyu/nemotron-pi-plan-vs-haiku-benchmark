import json
from pathlib import Path

import pytest

from todo import DEFAULT_PATH, TodoError, TodoStore, main


@pytest.fixture
def path(tmp_path: Path) -> Path:
    return tmp_path / "todos.json"


def test_add_returns_incrementing_ids_and_persists(path: Path) -> None:
    store = TodoStore(path)
    assert store.add("buy milk") == 1
    assert store.add("  write tests  ") == 2
    assert [t.title for t in TodoStore(path).list()] == ["buy milk", "write tests"]


def test_add_rejects_empty_title(path: Path) -> None:
    with pytest.raises(TodoError):
        TodoStore(path).add("   ")


def test_list_shows_new_todos_as_open(path: Path) -> None:
    store = TodoStore(path)
    assert store.list() == []
    store.add("walk dog")
    todos = store.list()
    assert len(todos) == 1
    assert (todos[0].id, todos[0].title, todos[0].done) == (1, "walk dog", False)


def test_done_marks_todo_complete(path: Path) -> None:
    store = TodoStore(path)
    store.add("a")
    store.add("b")
    store.done(2)
    assert [t.done for t in store.list()] == [False, True]


def test_done_unknown_id_raises(path: Path) -> None:
    with pytest.raises(TodoError, match="no todo with id 99"):
        TodoStore(path).done(99)


def test_rm_deletes_todo(path: Path) -> None:
    store = TodoStore(path)
    store.add("a")
    store.add("b")
    store.remove(1)
    assert [t.title for t in store.list()] == ["b"]


def test_rm_unknown_id_raises(path: Path) -> None:
    with pytest.raises(TodoError):
        TodoStore(path).remove(1)


def test_ids_are_not_reused_after_rm(path: Path) -> None:
    store = TodoStore(path)
    store.add("a")
    store.add("b")
    store.remove(2)
    assert store.add("c") == 3


def test_clear_removes_only_done_todos(path: Path) -> None:
    store = TodoStore(path)
    store.add("a")
    store.add("b")
    store.add("c")
    store.done(1)
    store.done(3)
    assert store.clear() == 2
    assert [t.title for t in store.list()] == ["b"]


def test_corrupt_file_raises_clear_error(path: Path) -> None:
    path.write_text("{not json", encoding="utf-8")
    with pytest.raises(TodoError, match="cannot read"):
        TodoStore(path).list()


def test_wrong_schema_raises_clear_error(path: Path) -> None:
    path.write_text(json.dumps({"next_id": 1, "todos": [{"id": "x"}]}), encoding="utf-8")
    with pytest.raises(TodoError, match="invalid format"):
        TodoStore(path).list()


def test_cli_add_and_list(path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["add", "buy milk"], path=path) == 0
    assert capsys.readouterr().out == "1\n"
    assert main(["done", "1"], path=path) == 0
    assert main(["add", "walk dog"], path=path) == 0
    capsys.readouterr()
    assert main(["list"], path=path) == 0
    assert capsys.readouterr().out == "[1] [x] buy milk\n[2] [·] walk dog\n"


def test_cli_errors_go_to_stderr_with_nonzero_exit(
    path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert main(["rm", "7"], path=path) == 1
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "no todo with id 7" in captured.err


def test_cli_rejects_non_numeric_id(path: Path) -> None:
    with pytest.raises(SystemExit) as exc:
        main(["done", "abc"], path=path)
    assert exc.value.code != 0


def test_default_path_is_cwd_todos_json() -> None:
    assert DEFAULT_PATH == Path("todos.json")
