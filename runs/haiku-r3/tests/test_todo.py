import json
from pathlib import Path

import pytest

from todo import main


@pytest.fixture
def todo_file(tmp_path: Path) -> Path:
    """A JSON file inside a temp directory, so tests never touch the cwd."""
    return tmp_path / "todos.json"


def run(todo_file: Path, *args: str) -> int:
    return main(["--file", str(todo_file), *args])


def test_add_prints_id_and_persists(todo_file, capsys):
    assert run(todo_file, "add", "buy milk") == 0
    assert capsys.readouterr().out == "1\n"

    data = json.loads(todo_file.read_text())
    assert data["todos"] == [{"id": 1, "title": "buy milk", "done": False}]


def test_list_shows_open_and_done_todos(todo_file, capsys):
    run(todo_file, "add", "first")
    run(todo_file, "add", "second")
    run(todo_file, "done", "2")
    capsys.readouterr()

    assert run(todo_file, "list") == 0
    assert capsys.readouterr().out == "[1] [·] first\n[2] [x] second\n"


def test_list_empty(todo_file, capsys):
    assert run(todo_file, "list") == 0
    assert capsys.readouterr().out == "No todos.\n"


def test_done_marks_todo_complete(todo_file, capsys):
    run(todo_file, "add", "write tests")
    capsys.readouterr()

    assert run(todo_file, "done", "1") == 0
    data = json.loads(todo_file.read_text())
    assert data["todos"][0]["done"] is True


def test_done_unknown_id_fails_cleanly(todo_file, capsys):
    run(todo_file, "add", "only one")
    capsys.readouterr()

    assert run(todo_file, "done", "99") == 1
    captured = capsys.readouterr()
    assert captured.err == "error: no todo with id 99\n"
    assert captured.out == ""


def test_rm_deletes_todo(todo_file, capsys):
    run(todo_file, "add", "a")
    run(todo_file, "add", "b")
    capsys.readouterr()

    assert run(todo_file, "rm", "1") == 0
    assert capsys.readouterr().out == "Removed 1.\n"
    run(todo_file, "list")
    assert capsys.readouterr().out == "[2] [·] b\n"


def test_rm_unknown_id_fails_cleanly(todo_file, capsys):
    assert run(todo_file, "rm", "5") == 1
    assert "no todo with id 5" in capsys.readouterr().err


def test_ids_are_never_reused_after_rm(todo_file, capsys):
    run(todo_file, "add", "a")
    run(todo_file, "add", "b")
    run(todo_file, "rm", "2")
    capsys.readouterr()

    run(todo_file, "add", "c")
    assert capsys.readouterr().out == "3\n"


def test_clear_removes_only_done_todos(todo_file, capsys):
    for title in ["a", "b", "c"]:
        run(todo_file, "add", title)
    run(todo_file, "done", "1")
    run(todo_file, "done", "3")
    capsys.readouterr()

    assert run(todo_file, "clear") == 0
    assert capsys.readouterr().out == "Removed 2 done todo(s).\n"
    run(todo_file, "list")
    assert capsys.readouterr().out == "[2] [·] b\n"


def test_add_rejects_empty_title(todo_file, capsys):
    assert run(todo_file, "add", "   ") == 1
    assert "title must not be empty" in capsys.readouterr().err
    assert not todo_file.exists()


def test_corrupt_file_reports_error(todo_file, capsys):
    todo_file.write_text("{not json")

    assert run(todo_file, "list") == 1
    assert "cannot read" in capsys.readouterr().err
