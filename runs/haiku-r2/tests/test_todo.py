import json
import subprocess
import sys
from pathlib import Path

import pytest

from todo import main

TODO_SCRIPT = Path(__file__).resolve().parents[1] / "todo.py"


@pytest.fixture
def todo_file(tmp_path: Path) -> Path:
    return tmp_path / "todos.json"


def run(path: Path, *args: str) -> int:
    return main(list(args), path=path)


def test_add_prints_id_and_persists(todo_file, capsys):
    assert run(todo_file, "add", "buy", "milk") == 0
    assert capsys.readouterr().out == "1\n"
    data = json.loads(todo_file.read_text())
    assert data["todos"] == [{"id": 1, "title": "buy milk", "done": False}]


def test_list_shows_open_and_done(todo_file, capsys):
    run(todo_file, "add", "first")
    run(todo_file, "add", "second")
    run(todo_file, "done", "2")
    capsys.readouterr()

    assert run(todo_file, "list") == 0
    assert capsys.readouterr().out == "[1] [·] first\n[2] [x] second\n"


def test_list_empty(todo_file, capsys):
    assert run(todo_file, "list") == 0
    assert capsys.readouterr().out == "No todos.\n"


def test_done_marks_todo(todo_file, capsys):
    run(todo_file, "add", "task")
    assert run(todo_file, "done", "1") == 0
    assert json.loads(todo_file.read_text())["todos"][0]["done"] is True


def test_done_unknown_id_fails(todo_file, capsys):
    run(todo_file, "add", "task")
    capsys.readouterr()
    assert run(todo_file, "done", "99") == 1
    assert "no todo with id 99" in capsys.readouterr().err


def test_rm_deletes_todo(todo_file, capsys):
    run(todo_file, "add", "keep")
    run(todo_file, "add", "drop")
    assert run(todo_file, "rm", "2") == 0
    assert [t["title"] for t in json.loads(todo_file.read_text())["todos"]] == ["keep"]


def test_ids_are_never_reused(todo_file, capsys):
    run(todo_file, "add", "a")
    run(todo_file, "add", "b")
    run(todo_file, "rm", "2")
    capsys.readouterr()
    run(todo_file, "add", "c")
    assert capsys.readouterr().out == "3\n"


def test_clear_removes_only_done(todo_file, capsys):
    run(todo_file, "add", "a")
    run(todo_file, "add", "b")
    run(todo_file, "done", "1")
    capsys.readouterr()
    assert run(todo_file, "clear") == 0
    assert "Removed 1 done todo(s)." in capsys.readouterr().out
    assert [t["id"] for t in json.loads(todo_file.read_text())["todos"]] == [2]


def test_empty_title_rejected(todo_file, capsys):
    assert run(todo_file, "add", "   ") == 1
    assert "title must not be empty" in capsys.readouterr().err
    assert not todo_file.exists()


def test_corrupt_file_reports_error(todo_file, capsys):
    todo_file.write_text("{not json")
    assert run(todo_file, "list") == 1
    assert "not valid JSON" in capsys.readouterr().err


def test_entry_point_uses_cwd_todos_json(tmp_path):
    result = subprocess.run(
        [sys.executable, str(TODO_SCRIPT), "add", "hello"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert result.stdout == "1\n"
    assert (tmp_path / "todos.json").exists()
