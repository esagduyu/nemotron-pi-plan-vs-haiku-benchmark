"""Tests for the tiny todo CLI."""

import json
import subprocess
import sys
from pathlib import Path

import pytest

# The module lives one level up from tests/
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import todo  # noqa: E402


@pytest.fixture()
def store(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Place todos.json inside a temp directory and make todo resolve to it."""
    monkeypatch.chdir(tmp_path)
    return tmp_path / "todos.json"


# -- add ---------------------------------------------------------------


def test_add_prints_id_and_persists(store: Path) -> None:
    new_id = todo.cmd_add("Learn Python", path=store)
    assert new_id == 1

    data = json.loads(store.read_text())
    assert data["next_id"] == 2
    assert len(data["todos"]) == 1
    assert data["todos"][0] == {"id": 1, "title": "Learn Python", "done": False}


def test_add_rejects_empty_title(store: Path) -> None:
    with pytest.raises(todo.TodoError, match="must not be empty"):
        todo.cmd_add("   ", path=store)


def test_add_increments_id(store: Path) -> None:
    id1 = todo.cmd_add("First", path=store)
    id2 = todo.cmd_add("Second", path=store)
    assert id2 == id1 + 1


# -- list --------------------------------------------------------------


def test_list_empty(store: Path) -> None:
    assert todo.cmd_list(path=store) == []


def test_list_format(store: Path) -> None:
    todo.cmd_add("Buy milk", path=store)
    todo.cmd_done(1, path=store)
    lines = todo.cmd_list(path=store)
    assert lines == ["[1] [x] Buy milk"]


# -- done --------------------------------------------------------------


def test_done_marks_todo(store: Path) -> None:
    todo.cmd_add("Read", path=store)
    todo.cmd_done(1, path=store)
    lines = todo.cmd_list(path=store)
    assert lines == ["[1] [x] Read"]


def test_done_unknown_id(store: Path, capsys) -> None:
    rc = todo.main(["done", "999"])
    assert rc == 1
    err = capsys.readouterr().err
    assert "error:" in err
    assert "not found" in err


# -- rm ----------------------------------------------------------------


def test_rm_removes_todo(store: Path) -> None:
    todo.cmd_add("A", path=store)
    todo.cmd_add("B", path=store)
    todo.cmd_rm(1, path=store)
    lines = todo.cmd_list(path=store)
    assert lines == ["[2] [·] B"]


def test_rm_id_not_reused(store: Path) -> None:
    todo.cmd_add("A", path=store)
    todo.cmd_rm(1, path=store)
    new_id = todo.cmd_add("B", path=store)
    assert new_id == 2  # not 1


def test_rm_unknown_id(store: Path, capsys) -> None:
    rc = todo.main(["rm", "999"])
    assert rc == 1
    assert "not found" in capsys.readouterr().err


# -- clear -------------------------------------------------------------


def test_clear_removes_only_done(store: Path) -> None:
    todo.cmd_add("Done one", path=store)
    todo.cmd_add("Keep me", path=store)
    todo.cmd_done(1, path=store)
    todo.cmd_clear(path=store)
    lines = todo.cmd_list(path=store)
    assert lines == ["[2] [·] Keep me"]


def test_clear_with_nothing_done(store: Path) -> None:
    todo.cmd_add("Open", path=store)
    rc = todo.main(["clear"])
    assert rc == 0


# -- CLI error handling ------------------------------------------------


def test_invalid_id_exits_nonzero_no_traceback(tmp_path: Path) -> None:
    """Run todo.py as a subprocess to ensure no Python traceback on bad input."""
    # Copy the script into the temp dir so it runs in isolation.
    project_root = Path(__file__).resolve().parent.parent
    script = tmp_path / "todo.py"
    script.write_text((project_root / "todo.py").read_text())
    result = subprocess.run(
        [sys.executable, str(script), "done", "abc"],
        capture_output=True,
        text=True,
        cwd=tmp_path,
    )
    assert result.returncode != 0
    assert "Traceback" not in result.stderr
    assert "error" in result.stderr


def test_corrupt_json_exits_nonzero(store: Path, capsys) -> None:
    store.write_text("not json{{{")
    rc = todo.main(["list"])
    assert rc == 1
    err = capsys.readouterr().err
    assert "error:" in err
